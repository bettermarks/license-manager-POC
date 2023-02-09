from typing import List
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


async def get_hierarchy_provider(session: AsyncSession, eid: str) -> hierarchy_provider_model.HierarchyProvider:
    return (
        await session.execute(
            statement=select(
                hierarchy_provider_model.HierarchyProvider
            ).where(
                hierarchy_provider_model.HierarchyProvider.eid == eid
            )
        )
    ).scalar_one_or_none()


