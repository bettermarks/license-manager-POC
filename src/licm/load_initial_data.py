from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from licm.client import http_get
from licm.db import get_session
from licm.model.hierarchy_provider import HierarchyProvider
from licm.model.product import Product

INITIAL_PRODUCTS = [
    Product(
        eid="full_access",
        name="bettermarks full access product",
        description="This product gives full access to all bettermarks features"
    )
]

INITIAL_HIERARCHY_PROVIDERS = [
    HierarchyProvider(
        eid="glu",
        name="GLU user class management system",
        description="This is our GLU user class management system used to get valid hierarchies",
        hierarchy_url="http://localhost:8000/hierarchy"
    ),
    HierarchyProvider(
        eid="univention_hb",
        name="Univention HB user class management system",
        description="This is the Univention HB user class management system used to get valid hierarchies",
        hierarchy_url="https://unviention-hb.de/hierarchy"
    ),
    HierarchyProvider(
        eid="schulcloud_ni",
        name="Schulcloud NI user class management system",
        description="This is the Schulcloud NI user class management system used to get valid hierarchies",
        hierarchy_url="https://schulcloud-ni.de/hierarchy"
    )
]


async def load_data(data):
    async with get_session() as session:
        for p in data:
            try:
                session.add(p)
                await session.commit()
            except IntegrityError:
                await session.rollback()


async def load_initial_products():
    await load_data(INITIAL_PRODUCTS)


async def load_initial_hierarchy_providers():
    await load_data(INITIAL_HIERARCHY_PROVIDERS)


async def load_hierarchy_levels_for_providers():
    for p in INITIAL_HIERARCHY_PROVIDERS:
        # response = http_get(p.url, {})
        response = {"school": 1, "class": 2, "student": 3, "teacher": 3}
