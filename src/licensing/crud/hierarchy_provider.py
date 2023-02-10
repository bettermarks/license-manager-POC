from functools import lru_cache

from fastapi import status as http_status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.model import hierarchy_provider as hp_model
from licensing.hierarchy_provider_client import get_hierarchy_from_provider


@lru_cache()
async def get_hierarchy_provider(session: AsyncSession, url: str) -> hp_model.HierarchyProvider:
    """
    gets a hierarchy provider with a given url or nothing
    """
    return (
        await session.execute(
            statement=select(
                hp_model.HierarchyProvider
            ).where(
                hp_model.HierarchyProvider.url == url
            )
        )
    ).scalar_one_or_none()


@lru_cache()
async def find_hierarchy_provider(session: AsyncSession, url: str) -> hp_model.HierarchyProvider:
    """
    finds a hierarchy provider with a given url or raises an HTTPException, if not found
    """
    provider = await get_hierarchy_provider(session, url)
    if not provider:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Hierarchy provider with base URL='{url}' is not registered."
        )
    return provider


async def get_user_hierarchy(session: AsyncSession, url: str, user_eid) -> (hp_model.HierarchyProvider, list):
    """
    gets the hierarchy list for a user by requesting the hierarchy provider.
    catches any exception raised from the request and 'translate' it to some 500
    http error.
    returns a tuple (the registered hierarchy provider object, the hierarchy itself as a list)
    """
    hp = await find_hierarchy_provider(session, url)  # raises exception, if not found
    try:
        return hp, await get_hierarchy_from_provider(url, user_eid)
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hierarchy provider server at base URL='{url}' did not respond properly."
        )
