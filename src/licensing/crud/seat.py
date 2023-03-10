import datetime
from typing import List, Any, Tuple, Set

from sqlalchemy import select, tuple_, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from licensing.crud.hierarchy_provider import get_user_memberships
from licensing.schema import seat as seat_schema
from licensing.model import seat as seat_model
from licensing.model import license as license_model


async def get_occupied_seats(
    session: AsyncSession, user_eid: str
) -> List[seat_schema.Seat]:
    """
    gets all seats, that are active at a given date (when)
    """
    return (
        (
            await session.execute(
                select(seat_model.Seat)
                .where(seat_model.Seat.user_eid == user_eid)
                .where(seat_model.Seat.is_occupied)
            )
        )
        .scalars()
        .all()
    )


async def get_licenses_for_entities(
    session: AsyncSession,
    hierarchy_provider_id: int,
    entities: Set[Tuple[str, int]],
    when: datetime.date,
) -> Any:
    """
    Gets all (distinct) licenses, that are valid at a given date (when),
    that are owned by the given entities under a given hierarchy provider.
    """
    return (
        await session.execute(
            select(
                license_model.License,
                func.sum(case((seat_model.Seat.is_occupied, 1), else_=0)).label(
                    "occupied_seats"
                ),
            )
            .join(
                seat_model.Seat,
                seat_model.Seat.ref_license == license_model.License.id,
                isouter=True,
            )
            .where(
                license_model.License.ref_hierarchy_provider == hierarchy_provider_id
            )
            .where(license_model.License.valid_from <= when)
            .where(license_model.License.valid_to >= when)
            .where(
                tuple_(
                    license_model.License.owner_eid, license_model.License.owner_level
                ).in_(list(entities))
            )
            .group_by(license_model.License.id, license_model.License.ref_product)
            .options(  # we need that as async does not support lazy loading!
                selectinload(license_model.License.product)
            )
        )
    ).all()


async def check_for_licenses(url: str, user_eid: str) -> Any:
    """
    checks for any licenses, a user could 'get'.
    Raises an HTTPException on failure
    """
    pass


async def get_permissions(
    session: AsyncSession, hierarchy_provider_url: str, user_eid: str
) -> List[Any]:
    """
    A just logged in user wants to get his permissions.
    """
    # 0. check, if requesting user is purchaser
    # TODO

    # 1. get the hierarchy list (for the user) from the hierarchy provider
    # (or raise an exception)
    hierarchy_provider, memberships = await get_user_memberships(
        session, hierarchy_provider_url, user_eid
    )
    if not memberships:  # no membership, no permission
        return []

    # 1. is there already an occupied! seat 'taken' by the requesting user?
    occupied_seats = await get_occupied_seats(session, user_eid)

    if occupied_seats:
        pass  # TODO check, if they should be freed or not. currently
    else:
        # get ALL currently valid licenses
        licenses = await get_licenses_for_entities(
            session,
            hierarchy_provider.id,
            {(m["eid"], m["level"]) for m in memberships.values()},
            datetime.date.today(),
        )

        for lic in licenses:
            # print("license =", (l.is_occupied, l.product.eid, l.owner_level, l.id, l.license_uuid, l.owner_eid, l.product.permissions))  # noqa: E501
            print(
                f"licens id = {lic[0].id},  license product = {lic[0].product} license "
                f"free seats = {lic[0].seats - lic[1]}"
            )
        # for x in await get_free_seats_for_licenses(session, [l.license_uuid for l in licenses]):  # noqa: E501
        #    print(f"license {x}")

        # ok, sort the licenses list by product.eid and by owner_level ascending and
        # then create a new list, in which only the first elements for every distinct
        # product eid are inserted. This gives a list of all licenses, where all
        # possible products are available
        # unique = reduce(
        #    lambda acc, l: acc + [l] if (acc and acc[-1].product.eid != l.product.eid) or (not acc) else acc,  # noqa: E501
        #    sorted(licenses, key=lambda l: (l.product.eid, l.owner_level)),
        #    []
        # )

        # for l in unique:
        #    print("unique =", (l.product.eid, l.owner_level, l.id, l.license_uuid, l.owner_eid, l.product.permissions))  # noqa: E501

        # reserve a seat for the first one!
        # TODO This is not a valid solution. Will be discussed!
        if licenses:
            return [
                {"allow": "all"}
            ]  # TODO this should be handled in product ACLs later ...
        else:
            return []
    return []
