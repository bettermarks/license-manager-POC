from functools import lru_cache
from typing import Dict

from fastapi import status as http_status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.client.hierarchy_provider_client import hierarchy_provider_memberships_url
from licensing.http_client import http_get
from licensing.model import hierarchy_provider as model
from licensing.utils import async_measure_time


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
) -> (model.HierarchyProvider, Dict[str, Dict[str, int]]):
    """
    gets the membership list for a user by requesting the hierarchy provider.
    catches any exception raised from the request and 'translate' it to some 500
    http error.
    ::returns a tuple (the registered hierarchy provider object, the memberships as
        a dict with key=entity EID) and value={"type": <<sth. like 'school'>>, "level": <<some int>>}
    """
    hierarchy_provider = await find_hierarchy_provider(session, url)
    try:
        memberships_raw = await http_get(hierarchy_provider_memberships_url(f"{url}/", user_eid))
        return hierarchy_provider, {
            m["eid"]: {
                "type": m["type"],
                "level": m['level']
            } for m in memberships_raw
        }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hierarchy provider server at base URL='{url}' did not respond properly ({e})."
        )
