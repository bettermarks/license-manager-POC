import uuid
from typing import Dict

from fastapi import status as http_status, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.crud.hierarchy_provider import get_user_memberships, lookup_membership
from licensing.crud.product import get_product
from licensing.model import license as model
from licensing.schema import license as schema
from licensing.utils import async_measure_time


@async_measure_time
async def purchase(session: AsyncSession, purchaser_eid: str, license_data: schema.LicenseCreate) -> Dict[str, str]:
    """
    The license purchase process performed by a user for one or more entities, they are member of.

    :param session: the SQLAlchemy session
    :param purchaser_eid: the EID of the license purchaser
    :param license_data: license data (pydantic schema) containing license info like 'valid_from', etc.
    :raises HTTPException: possible codes 409, 422 or 500
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
        lic = model.License(
            uuid=license_uuid,
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
    except IntegrityError as _ex:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail=(
                f"License creation failed: A license for at least one of the owner EIDs"
                f"'({license_data.owner_eids})({license_data.owner_type})', "
                f"valid from '{license_data.valid_from}' to '{license_data.valid_to}' "
                f"already has been created."
            )
        )
    return {"license_uuid": license_uuid}
