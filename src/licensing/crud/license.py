from typing import List

from fastapi import status as http_status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.hierarchy_provider_client import get_hierarchy
from licensing.crud.hierarchy_provider import find_hierarchy_provider
from licensing.crud.product import find_product
from licensing.model import license as license_model
from licensing.schema import license as license_schema


async def check_owners(url: str, purchaser_eid: str, owner_hierarchy_level: str, owner_eids: List[str]) -> bool:
    """
    checks, if the requested license owners are in the 'hierarchy path' of the purchaser.
    That means: is the purchaser 'allowed' to purchase a license for the given owners?
    This is true, if and only if the purchaser is 'member' of the license owner, f.e.
    some class or some school.
    Raises an HTTPException on failure
    """
    try:
        hierarchy_list = await get_hierarchy(url, purchaser_eid)
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,  # TODO is this the correct error?
            detail=f"Hierarchy provider server at base URL='{url}' did not respond."
        )

    # Now do the actual check. TODO Can we do that in a more elegant way?
    hierarchy_list_as_string = '\t'.join(hierarchy_list)
    for owner_eid in owner_eids:
        if f"{owner_hierarchy_level}({owner_eid})" not in hierarchy_list_as_string:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Provided license owner ('{owner_eid}') cannot be found in users hierarchy."
            )
    return True


async def purchase_license(
        session: AsyncSession,
        purchaser_eid: str,
        license_data: license_schema.LicenseCreate
) -> license_model.License:
    """
    The license purchase process performed by a user for one or more entities, they are member of.
    """
    # 0. check, if requesting user is purchaser
    # TODO

    # 1. find hierarchy provider url provided (exception is raised, if hierarchy provider is not registered)
    await find_hierarchy_provider(session, license_data.hierarchy_provider_url)

    # 2. find product (exception is raised, if product cannot be found)
    product = await find_product(session, license_data.product_eid)

    # 3. check, if owners are in the purchasers hierarchy path (exception is raised, if not!)
    await check_owners(
        license_data.hierarchy_provider_url,
        purchaser_eid,
        license_data.owner_hierarchy_level,
        license_data.owner_eids
    )

    # 4. create license
    lic = license_model.License(
        ref_product=product.id,
        purchaser_eid=purchaser_eid,
        **{k: v for k, v in license_data if k not in ["product_eid", "hierarchy_provider_url"]}
    )
    session.add(lic)
    await session.commit()
    return lic


