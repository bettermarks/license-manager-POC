import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("url", "params", "result"),
    [
        ("https://example.com", {"foo": "bar", "biz": "bam"}, "https://example.com/?foo=bar&biz=bam"),
        ("https://example.com?param=1", {"foo": "bar", "biz": "bam"}, "https://example.com/?param=1&foo=bar&biz=bam"),
        ("https://example.com?param=1", None, "https://example.com/?param=1"),
        ("https://example.com", None, "https://example.com/"),
        ("https://example.com", {}, "https://example.com/"),
    ]
)
async def test_add_url_params(url, params, result):
    from licensing.api.api_v1.endpoints.oidc import add_url_params
    assert await add_url_params(url, params) == result


@pytest.mark.skip(reason="authorize_redirect needs to be mocked")
def test_login(test_app, monkeypatch):
    response = test_app.get("/oidc/login/glu")
    assert response.status_code == 302
    assert response.json()