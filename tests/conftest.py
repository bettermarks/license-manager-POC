import pytest
from starlette.testclient import TestClient



@pytest.fixture(scope="module")
def test_app():
    from licensing.main import app
    from licensing.api.api_v1.endpoints import oidc

    client = TestClient(app)
    oidc.register_providers()
    yield client
