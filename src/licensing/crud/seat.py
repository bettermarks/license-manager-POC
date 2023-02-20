import datetime
from functools import reduce
from typing import List, Any, Tuple, Set

from sqlalchemy import select, tuple_, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from licensing.crud.hierarchy_provider import get_user_memberships
from licensing.schema import seat as seat_schema
from licensing.model import seat as seat_model
from licensing.model import license as license_model


async def get_occupied_seats(session: AsyncSession, user_eid: str) -> List[seat_schema.Seat]:
    """
    gets all seats for a given user, that are currently 'occupied'.
    """
    return (
        await session.execute(
            select(
                seat_model.Seat
            ).where(
                seat_model.Seat.user_eid == user_eid
            ).where(
                seat_model.Seat.is_occupied
            )
        )
    ).scalars().all()


async def get_valid_licenses_and_occupied_seats(
        session: AsyncSession, hierarchy_provider_id: int, entities: Set[Tuple[str, int]], when: datetime.date
) -> List[Tuple[license_model.License, int]]:
    """
    Gets all (distinct) licenses, that are valid at a given date (when),
    that are owned by the given entities under a given hierarchy provider.
    :returns a list of tuples containing the valid license object plus the number of occupied seats.
    """
    # get the '# of occupied seats' per license UUID (that is the combined licenses that share seats)
    occupied_seats = select(
        license_model.License.license_uuid, func.count().label("occupied_seats")
    ).join(
        seat_model.Seat,
        and_(
            seat_model.Seat.ref_license == license_model.License.id,
            seat_model.Seat.is_occupied
        )
    ).group_by(
        license_model.License.license_uuid
    ).subquery()

    # join the two queries
    return (
        await session.execute(
            select(
                license_model.License, func.coalesce(occupied_seats.c.occupied_seats, 0)
            ).join_from(
                license_model.License, occupied_seats,
                license_model.License.license_uuid == occupied_seats.c.license_uuid,
                isouter=True
            ).where(
                and_(
                    license_model.License.ref_hierarchy_provider == hierarchy_provider_id,
                    license_model.License.valid_from <= when,
                    license_model.License.valid_to >= when,
                    tuple_(license_model.License.owner_eid, license_model.License.owner_level).in_(list(entities))
                )
            ).options(   # we need that as async does not support lazy loading!
                selectinload(license_model.License.product)
            )
        )
    ).all()


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

    # 1. is there already an occupied! seat 'taken' by the requesting user?
    occupied_seats = await get_occupied_seats(session, user_eid)

    if False: # occupied_seats:
        for seat in occupied_seats:
            print("seat = ", seat.__dict__)
    else:
        # get ALL currently valid licenses
        licenses_and_ocuupied_seats = await get_valid_licenses_and_occupied_seats(
            session,
            hierarchy_provider.id,
            {(m["eid"], m["level"]) for m in memberships.values()},
            datetime.date.today()
        )

        for l in licenses_and_ocuupied_seats:
            print(f"license id = {l[0].id},  license product = {l[0].product.eid} license free seats = {l[0].seats - l[1]}")

        for l in sorted(licenses_and_ocuupied_seats, key=lambda l: (l[0].product.eid, l[1])):
            print(f"license id = {l[0].id},  license product = {l[0].product.eid} license free seats = {l[0].seats - l[1]}")

        # ok, sort the licenses list by product.eid and by the number of occupied seats ascending and then
        # create a new list, in which only the first elements for every distinct product eid
        # are inserted. This gives a list of all licenses, where all possible products are
        # available
        licenses_to_occupy = reduce(
            lambda acc, l: acc + [l] if (acc and acc[-1].product.eid != l.product.eid) or (not acc) else acc,
            [l[0] for l in sorted(licenses_and_ocuupied_seats, key=lambda l: (l[0].product.eid, l[1]))],
            []
        )

        for l in licenses_to_occupy:
            print("unique =", (l.product.eid, l.owner_level, l.id, l.license_uuid, l.owner_eid, l.product.permissions))
            seat = seat_model.Seat(
                ref_license=l.id,
                user_eid=user_eid,
                occupied_at=datetime.datetime.utcnow(),
                last_login=datetime.datetime.utcnow(),
                is_occupied=True
            )
            print("seat = ", seat)
            session.add(seat)
        await session.commit()

        if licenses_and_ocuupied_seats:
            return [{"allow": "all"}]   # TODO this should be handled in product ACLs later ...
        else:
            return []
    return []
