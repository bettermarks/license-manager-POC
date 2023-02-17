import datetime
import uuid
from functools import reduce
from typing import List, Any, Tuple

from sqlalchemy import select, text, bindparam
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


async def get_free_seats_for_licenses(
        session: AsyncSession, license_uuids: List[uuid.UUID]
) -> Any:  # List[Tuple[uuid.UUID, int]]:
    """
    for every license uuid given, get the number of free seats
    """
    return (
        await session.execute(
            text(
                f"""
                    SELECT
                        l.license_uuid,
                        MAX(l.seats) - SUM(CASE WHEN s.id IS NOT NULL THEN 1 ELSE 0 END) as free_seats
                    FROM
                        license l
                        LEFT JOIN seat s ON s.ref_license = l.id AND s.is_occupied
                    WHERE
                        l.license_uuid IN :license_uuids
                    GROUP BY
                        l.license_uuid
                """
            ).bindparams(
                bindparam("license_uuids", expanding=True)
            ),
            params={"license_uuids": license_uuids}
        )
    ).scalars().all()


async def check_for_licenses(url: str, user_eid: str) -> Any:
    """
    checks for any licenses, a user could 'get'.
    Raises an HTTPException on failure
    """
    pass


async def get_permissions(session: AsyncSession, hierarchy_provider_url: str, user_eid: str) -> List[Any]:
    """
    A just logged in user wants to get his permissions.
    """
    # 0. check, if requesting user is purchaser
    # TODO

    # 1. get the hierarchy list (for the user) from the hierarchy provider (or raise an exception)
    hierarchy_provider, memberships = await get_user_memberships(session, hierarchy_provider_url, user_eid)
    if not memberships:   # no membership, no permission
        return []

    # 1. is there already an active! seat 'taken' by the requesting user?
    active_seats = await get_active_seats(session, user_eid, datetime.date.today())

    if active_seats:
        pass  # TODO check, if they should be freed or not. currently
    else:
        # get ALL currently valid licenses
        licenses = await get_licenses_for_entities(
            session,
            hierarchy_provider.id,
            {(m["eid"], m["level"]) for m in memberships.values()},
            datetime.date.today()
        )

        for x in await get_free_seats_for_licenses(session, [l.license_uuid for l in licenses]):
            print(f"license {x}")



        # ok, sort the licenses list by product.eid and by owner_level ascending and then
        # create a new list, in which only the first elements for every distinct product eid
        # are inserted. This gives a list of all licenses, where all possible products are
        # available
        unique = reduce(
            lambda acc, l: acc + [l] if (acc and acc[-1].product.eid != l.product.eid) or (not acc) else acc,
            sorted(licenses, key=lambda l: (l.product.eid, l.owner_level)),
            []
        )


        for l in licenses:
            print("license =", (l.product.eid, l.owner_level, l.id, l.license_uuid, l.owner_eid, l.product.permissions))

        for l in unique:
            print("unique =", (l.product.eid, l.owner_level, l.id, l.license_uuid, l.owner_eid, l.product.permissions))


        # reserve a seat for the first one!  # TODO This is not a valid solution. Will be discussed!
        if licenses:
            return [{"allow": "all"}]   # TODO this should be handled in product ACLs later ...
        else:
            return []
    return []
