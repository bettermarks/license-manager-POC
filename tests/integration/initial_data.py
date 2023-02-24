from licensing.model.hierarchy_provider import HierarchyProvider
from licensing.model.product import Product


INITIAL_TEST_PRODUCTS = [
    Product(
        eid="full_access",
        name="full access for all bettermarks content",
        description="This product gives full access to all bettermarks books",
        permissions=[{"*": "rx"}]
    ),
]

INITIAL_TEST_HIERARCHY_PROVIDERS = [
    HierarchyProvider(
        url="http://0.0.0.0:5001/hierarchy",
        short_name="glu",
        name="GLU user class management system",
        description="This is our GLU user class management system used to get valid hierarchies"
    ),
]
