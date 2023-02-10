from typing import List, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.schema import seat as seat_schema
from licensing.model import seat as seat_model


async def get_active_seats(session: AsyncSession, user_eid: str) -> List[seat_schema.Seat]:
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

    # 1. get the users hierarchy in any case
    get_user_hierarchy

    # 1. Is there already an active! seat 'taken' by the requesting user?

    active_seats = await get_active_seats(session, user_eid)


    if active_seats:
        pass  # TODO check, if they should be freed or not
        print("active seats =", active_seats)
    else:
        print("active seats =", active_seats)
