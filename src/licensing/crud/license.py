import uuid
from datetime import date
from typing import List, Dict

from fastapi import status as http_status, HTTPException
from sqlalchemy import text, select, bindparam, Date, BigInteger, exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from licensing.crud.hierarchy_provider import get_user_memberships, lookup_membership
from licensing.crud.product import get_product
from licensing.model import license as license_model
from licensing.schema import license as schema
from licensing.utils import async_measure_time


@async_measure_time
async def get_licenses_for_entities(
        session: AsyncSession, hierarchy_provider_id: int, entities: Dict[(str, int)], when: date
) -> List[license_model.License]:
    """
    Gets all (distinct) licenses, that are valid at a given date (when),
    that are owned by the given entities under a given hierarchy provider.

    :param session: the SQLAlchemy session
    :param hierarchy_provider_id: the id of the hierarchy provider the licenses to get should apply to
    :param entities: the license owners, the licenses to get should apply to (as a dict of tuples with key=entity EID)
    :param when: actually 'today'
    :return: a list of License objects, that are owned by the given entities, but only with an selected attributes.
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
                                l.id 
                        FROM
                            license_owner lo
                            INNER JOIN license l ON l.id = lo.ref_license
                        WHERE
                            l.ref_hierarchy_provider = :hierarchy_provider_id
                            AND l.valid_from <= :when
                            AND l.valid_to >= :when
                            AND (lo.eid, lo.hierarchy_level) IN :entity_list
                    """
                ).bindparams(
                    bindparam("when", type_=Date),
                    bindparam("hierarchy_provider_id", type_=BigInteger),
                    bindparam("entity_list", expanding=True)
                ).columns(
                    license_model.License.id
                )
            ).options(   # we need that as async does not support lazy loading!
                selectinload(license_model.License.product)
            ),
            params={
                "when": when,
                "hierarchy_provider_id": hierarchy_provider_id,
                "entity_list": [(k, v[0]) for k, v in entities.items()]}
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
    :return: nothing or raises an HTTPError (409, 422, or 500)
    """
    # 0. check, if requesting user is purchaser
    # TODO

    # 2. find product (exception is raised, if product cannot be found)
    product = await get_product(session, license_data.product_eid)
    if not product:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"License creation failed: product with EID '{license_data.product_eid}' cannot be not found."
        )

    # 3. check, if owners are in the purchasers hierarchy path (exception is raised, if not!)
    # checks, if the requested license owners are in the 'hierarchy path' of the purchaser.
    # That means: is the purchaser 'allowed' to purchase a license for the given owners?
    # This is true, if and only if the purchaser is 'member' of the license owner, f.e.
    # some class or some school. If everything is fine, create the license!

    # 3.1 get all the 'memberships' (for the purchaser) from the hierarchy provider (or raise an exception (422,500))
    try:
        hierarchy_provider, memberships = await get_user_memberships(
            session, license_data.hierarchy_provider_url, purchaser_eid
        )
    except HTTPException as ex:
        raise HTTPException(
            status_code=ex.status_code,
            detail=f"License creation failed: {ex.detail}"
        )
    # generate a random UUID as a license identifier
    license_uuid = uuid.uuid4()

    # 3.3 Now do the actual check and insert licenses.
    for owner_eid in license_data.owner_eids:
        membership = lookup_membership(memberships, license_data.owner_type, owner_eid)
        if not membership:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"License creation failed: license owner ('{owner_eid}') does not match any users membership."
            )

        # 3.2. create license (will be rolled back, if some checks for 'owners' fail ...
        lic = license_model.License(
            license_uuid=license_uuid,
            purchaser_eid=purchaser_eid,
            owner_eid=owner_eid,
            owner_type=membership["type"],
            owner_level=membership["level"],
            valid_from=license_data.valid_from,
            valid_to=license_data.valid_to,
            seats=license_data.seats,
            is_seats_shared=len(license_data.owner_eids) > 1
        )
        lic.product = product
        lic.hierarchy_provider = hierarchy_provider
        session.add(lic)

    # ok, everything seems to be fine, commit!
    try:
        await session.commit()
    except exc.IntegrityError as _ex:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail=(
                f"License creation failed: A license for at least one of the owner EIDs"
                f"'({license_data.owner_eids})({license_data.owner_type})', "
                f"valid from '{license_data.valid_from}' to {license_data.valid_to} "
                f"already has been created."
            )
        )
    return {"license_uuid": license_uuid}
