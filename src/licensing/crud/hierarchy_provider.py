from fastapi import status as http_status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.model import hierarchy_provider as hierarchy_provider_model
from licensing.hierarchy_provider_client import get_hierarchy_from_provider


async def get_hierarchy_provider(session: AsyncSession, url: str) -> hierarchy_provider_model.HierarchyProvider:
    return (
        await session.execute(
            statement=select(
                hierarchy_provider_model.HierarchyProvider
            ).where(
                hierarchy_provider_model.HierarchyProvider.url == url
            )
        )
    ).scalar_one_or_none()


async def find_hierarchy_provider(session: AsyncSession, url: str) -> hierarchy_provider_model.HierarchyProvider:
    """
    checks, if the provided hierarchy provider exists or raises an HTTPException
    """
    provider = await get_hierarchy_provider(session, url)
    if not provider:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Hierarchy provider with base URL='{url}' is not registered."
        )
    return provider


async def get_user_hierarchy(url: str, user_eid) -> list:
    """
    gets the hierarchy list for a user by requesting the hierarchy provider.
    catches any exception raised from the request and 'translate' it to some 500
    http error.
    """
    try:
        return await get_hierarchy_from_provider(url, user_eid)
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hierarchy provider server at base URL='{url}' did not respond properly."
        )
