from fastapi import status as http_status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.crud.hierarchy_provider import find_hierarchy_provider, get_user_hierarchy
from licensing.crud.product import find_product
from licensing.model import license as license_model
from licensing.schema import license as license_schema


async def purchase_license(
        session: AsyncSession, purchaser_eid: str, license_data: license_schema.LicenseCreate
) -> license_model.License:
    """
    The license purchase process performed by a user for one or more entities, they are member of.
    """
    # 0. check, if requesting user is purchaser
    # TODO

    # 1. find hierarchy provider url provided (exception is raised, if hierarchy provider is not registered)
    hierarchy_provider = await find_hierarchy_provider(session, license_data.hierarchy_provider_url)

    # 2. find product (exception is raised, if product cannot be found)
    product = await find_product(session, license_data.product_eid)

    # 3. check, if owners are in the purchasers hierarchy path (exception is raised, if not!)
    # checks, if the requested license owners are in the 'hierarchy path' of the purchaser.
    # That means: is the purchaser 'allowed' to purchase a license for the given owners?
    # This is true, if and only if the purchaser is 'member' of the license owner, f.e.
    # some class or some school.

    # 3.1 get the hierarchy list (for the purchaser) from the hierarchy provider (or raise an exception)
    hierarchy_list = await get_user_hierarchy(license_data.hierarchy_provider_url, purchaser_eid)

    # 3.2 Now do the actual check. TODO Can we do that in a more elegant way?
    hierarchy_list_as_string = '::'.join(hierarchy_list)
    for owner_eid in license_data.owner_eids:
        if f"{license_data.owner_hierarchy_level}({owner_eid})" not in hierarchy_list_as_string:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Provided license owner ('{owner_eid}') cannot be found in users hierarchy."
            )

    # 4. create license
    lic = license_model.License(
        ref_product=product.id,
        ref_hierarchy_provider=hierarchy_provider.id,
        purchaser_eid=purchaser_eid,
        **{k: v for k, v in license_data if k not in ["product_eid", "hierarchy_provider_url"]}
    )
    session.add(lic)
    await session.commit()
    return lic
