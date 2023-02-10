from typing import List

from fastapi import status as http_status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.model import hierarchy_provider as hierarchy_provider_model


async def get_hierarchy_providers(session: AsyncSession) -> List[hierarchy_provider_model.HierarchyProvider]:
    return (
        await session.execute(
            statement=select(
                hierarchy_provider_model.HierarchyProvider
            )
        )
    ).scalars().all()


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


