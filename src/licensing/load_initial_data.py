from sqlalchemy.exc import IntegrityError

from licensing.db import get_async_session_context
from licensing.model.hierarchy_provider import HierarchyProvider
from licensing.model.product import Product

INITIAL_PRODUCTS = [
    Product(
        eid="full_access",
        name="bettermarks full access product",
        description="This product gives full access to all bettermarks features"
    )
]

INITIAL_HIERARCHY_PROVIDERS = [
    HierarchyProvider(
        url="http://0.0.0.0:5001/hierarchy",
        short_name="glu",
        name="GLU user class management system",
        description="This is our GLU user class management system used to get valid hierarchies"
    ),
    HierarchyProvider(
        url="https://unviention-hb.de/hierarchy",
        short_name="univention_hb",
        name="Univention HB user class management system",
        description="This is the Univention HB user class management system used to get valid hierarchies",
    ),
    HierarchyProvider(
        url="https://schulcloud-ni.de/hierarchy",
        short_name="schulcloud_ni",
        name="Schulcloud NI user class management system",
        description="This is the Schulcloud NI user class management system used to get valid hierarchies",
    )
]


async def load_data(data):
    async with get_async_session_context() as session:
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

