from datetime import date
from typing import List

from fastapi import status as http_status, HTTPException
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.crud.hierarchy_provider import get_user_memberships
from licensing.crud.product import find_product
from licensing.hierarchy_provider_client import encode_entity
from licensing.model import license as license_model
from licensing.model import license_owner as license_owner_model
from licensing.schema import license as schema
from licensing.utils import async_measure_time


@async_measure_time
async def get_licenses_for_entities(
        session: AsyncSession, hierarchy_provider_id: int, entities: List[str], when: date
) -> List[license_model.License]:
    """
    gets all licenses, that are valid at a given date (when), that are owned by the given entities under
    a given hierarchy provider
    """
    stmt = text(f"""
        SELECT
            DISTINCT id
        FROM
            (
            SELECT
                id,
                '(' || owner_hierarchy_level || ')(' || owner_eid || ')' as encoded_owner
            FROM
                (	
                SELECT
                    id,
                    owner_hierarchy_level,
                    unnest(owner_eids) as owner_eid
                from 
                    license
                where
                    valid_from <= '{when}'
                    AND valid_to >= '{when}'
                    AND ref_hierarchy_provider = {hierarchy_provider_id}
                ) li
            ) lo
        WHERE
            lo.encoded_owner IN ({', '.join([f"'{e}'" for e in entities])});            
    """)

    # TODO Can this be achieved in only one query instead of two?
    # Get all license ids ...
    stmt = stmt.columns(license_model.License.id)
    license_ids = (await session.execute(stmt)).scalars().all()

    # Now we need to get the license objects for those IDs and return the objects.
    return (
        await session.execute(
            select(model.License).where(
                model.License.id.in_(license_ids)
            )
        )
    ).scalars().all()


@async_measure_time
async def purchase(
        session: AsyncSession, purchaser_eid: str, license_data: schema.LicenseCreate
) -> license_model.License:
    """
    The license purchase process performed by a user for one or more entities, they are member of.
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
