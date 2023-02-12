import datetime
from typing import List, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.crud.hierarchy_provider import get_user_memberships
from licensing.crud.license import get_licenses_for_entities
from licensing.schema import seat as seat_schema
from licensing.model import seat as seat_model


async def get_active_seats(session: AsyncSession, user_eid: str, when: datetime.date) -> List[seat_schema.Seat]:
    """
    gets all seats, that are active at a given date (when)
    """
    return (
        await session.execute(
            statement=select(
                seat_model.Seat
            ).where(
                seat_model.Seat.user_eid == user_eid
            ).where(
                seat_model.Seat.is_occupied
            )
        )
    ).scalars().all()


async def check_for_licenses(url: str, user_eid: str) -> Any:
    """
    checks for any licenses, a user could 'get'.
    Raises an HTTPException on failure
    """
    pass


async def get_permissions(session: AsyncSession, hierarchy_provider_url: str, user_eid: str) -> Any:
    """
    A just logged in user wants to get his permissions.
    """
    # 0. check, if requesting user is purchaser
    # TODO

    # 1. get the hierarchy list (for the user) from the hierarchy provider (or raise an exception)
    hierarchy_provider, memberships = await get_user_memberships(session, hierarchy_provider_url, user_eid)

    # 1. Is there already an active! seat 'taken' by the requesting user?
    active_seats = await get_active_seats(session, user_eid, datetime.date.today())

    if active_seats:
        pass  # TODO check, if they should be freed or not. currently
    else:
        # get ALL currently valid licenses
        licenses = await get_licenses_for_entities(
            session, hierarchy_provider.id, memberships, datetime.date.today()
        )
        print("licenses = ", licenses)
    return "OK"
