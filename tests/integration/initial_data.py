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
        url="http://mocked_hierarchy_provider.com/hierarchy",
        short_name="a mocked hierarchy provider",
        name="some mocked hierarchy provider",
        description="This is some mocked hierarchy provider"
    ),
]
