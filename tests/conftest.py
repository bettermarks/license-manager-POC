import pytest
from starlette.testclient import TestClient

from licm.main import licm


@pytest.fixture(scope="module")
def test_app():
    client = TestClient(licm)
    yield client
