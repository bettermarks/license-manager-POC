from datetime import date
from typing import Set, List

from fastapi import status as http_status, HTTPException
from sqlalchemy import text, select, bindparam, Date, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.crud.hierarchy_provider import get_user_memberships
from licensing.crud.product import find_product
from licensing.hierarchy_provider_client import encode_entity, decode_entity
from licensing.model import license as license_model
from licensing.model import license_owner as license_owner_model
from licensing.schema import license as schema
from licensing.utils import async_measure_time


@async_measure_time
async def get_licenses_for_entities(
        session: AsyncSession, hierarchy_provider_id: int, entities: Set[str], when: date
) -> List[license_model.License]:
    """
    Gets all (distinct) licenses, that are valid at a given date (when),
    that are owned by the given entities under a given hierarchy provider.

    :param session: the SQLAlchemy session
    :param hierarchy_provider_id: the id of the hierarchy provider the licenses to get should apply to
    :param entities: the license owners, the licenses to get should apply to
    :param when: actually 'today'
    :return: a list of License objects, that are owned by the given entities, but only with an 'id' attribute.
    """
    return (
        await session.execute(
            select(
                license_model.License
            ).from_statement(
                text(
                    f"""
                        SELECT
                            DISTINCT 
                                l.id, 
                                l.valid_from
                        FROM
                            license_owner lo
                            INNER JOIN license l ON l.id = lo.ref_license
                        WHERE
                            l.ref_hierarchy_provider = :hierarchy_provider_id
                            AND l.valid_from <= :when
                            AND l.valid_to >= :when
                            AND (lo.hierarchy_level, lo.eid) IN :entity_list
                    """
                ).bindparams(
                    bindparam("when", type_=Date),
                    bindparam("hierarchy_provider_id", type_=BigInteger),
                    bindparam("entity_list", expanding=True)
                ).columns(
                    license_model.License.id,
                )
            ),
            params={
                "when": when,
                "hierarchy_provider_id": hierarchy_provider_id,
                "entity_list": [decode_entity(e) for e in entities]}
        )
    ).scalars().all()


@async_measure_time
async def purchase(
        session: AsyncSession, purchaser_eid: str, license_data: schema.LicenseCreate
) -> license_model.License:
    """
    The license purchase process performed by a user for one or more entities, they are member of.

    :param session: the SQLAlchemy session
    :param purchaser_eid: the EID of the license purchaser
    :param license_data: license data (pydantic schema) containing license info like 'valid_from', etc.
    :return: the created license model OR raises an HTTP exception
    """
    # 0. check, if requesting user is purchaser
    # TODO

    # 2. find product (exception is raised, if product cannot be found)
    product = await find_product(session, license_data.product_eid)

    # 3. check, if owners are in the purchasers hierarchy path (exception is raised, if not!)
    # checks, if the requested license owners are in the 'hierarchy path' of the purchaser.
    # That means: is the purchaser 'allowed' to purchase a license for the given owners?
    # This is true, if and only if the purchaser is 'member' of the license owner, f.e.
    # some class or some school.

    # 3.1 get the hierarchy list (for the purchaser) from the hierarchy provider (or raise an exception)
    hierarchy_provider, memberships = await get_user_memberships(
        session, license_data.hierarchy_provider_url, purchaser_eid
    )

    # 3.2 Now do the actual check.
    for owner_eid in license_data.owner_eids:
        if encode_entity(license_data.owner_hierarchy_level, owner_eid) not in memberships:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"License creation failed: license owner ('{owner_eid}') does not match any users membership."
            )

    # 4. create license
    lic = license_model.License(
        purchaser_eid=purchaser_eid,
        valid_from=license_data.valid_from,
        valid_to=license_data.valid_to,
        seats=license_data.seats
    )
    lic.product = product
    lic.hierarchy_provider = hierarchy_provider
    session.add(lic)

    # 4.1 ... and the license owner info for all license owners
    for owner_eid in license_data.owner_eids:
        license_owner = license_owner_model.LicenseOwner(
            eid=owner_eid,
            hierarchy_level=license_data.owner_hierarchy_level
        )
        license_owner.license = lic
        license_owner.hierarchy_provider = hierarchy_provider
        session.add(license_owner)
    await session.commit()
    return lic
