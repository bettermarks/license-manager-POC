from functools import lru_cache
from typing import Dict, Tuple

from fastapi import status as http_status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.client.hierarchy_provider_client import hierarchy_provider_memberships_url
from licensing.http_client import http_get
from licensing.model import hierarchy_provider as model
from licensing.utils import async_measure_time


# a custom type representing indexed 'hierarchy memberships'. It is basically
# a dict with
# key = tuple(
#   <<the type, sth. like 'school'>>,
#   <<the eid, sth. like '1234567'>>
# ) and
# value = {
#   "eid": <<the eid, sth. like '1234567'>>,
#   "type": <<the type, sth. like 'school'>>,
#   "level": <<the level, something like 1>>
# }
memberships_type = Dict[Tuple[str, str], Dict[str, int]]


@lru_cache()
async def find_hierarchy_provider(session: AsyncSession, url: str) -> model.HierarchyProvider:
    """
    finds a hierarchy provider with a given url or raises an HTTPException, if not found
    """
    provider = (
        await session.execute(
            statement=select(
                model.HierarchyProvider
            ).where(
                model.HierarchyProvider.url == url
            )
        )
    ).scalar_one_or_none()
    if not provider:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Hierarchy provider with base URL='{url}' is not registered."
        )
    return provider


@async_measure_time
async def get_user_memberships(
        session: AsyncSession, url: str, user_eid: str
) -> (model.HierarchyProvider, memberships_type):
    """
    gets the membership list for a user by requesting the hierarchy provider.
    catches any exception raised from the request and 'translate' it to some 500
    http error.
    :return a tuple (the registered hierarchy provider object, the memberships of 'memberships' type (see above))
    """
    hierarchy_provider = await find_hierarchy_provider(session, url)
    try:
        memberships_raw = await http_get(hierarchy_provider_memberships_url(f"{url}/", user_eid))
        return hierarchy_provider, {
            (m["type"], m["eid"]): {
                "type": m["type"],
                "eid": m["eid"],
                "level": m["level"]
            } for m in memberships_raw
        }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hierarchy provider server at base URL='{url}' did not respond properly ({e})."
        )


def lookup_membership(memberships: memberships_type, typ: str, eid: str):
    """
    looks up some membership in a given 'membership dict' (see above), that is got from
    the hierarchy provider
    :param memberships: the memberships dict to be looked up
    :param typ: a given type to be looked up (together with an eid)
    :param eid: a given eid to be looked up (together wit ha type)
    :return: a dict like {"type": <<some type>>, "eid": <<some eid>>, "level": <<some level>>} OR {}
    """
    return memberships.get((typ, eid), {})
