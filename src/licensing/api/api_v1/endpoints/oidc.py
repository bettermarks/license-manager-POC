from fastapi import APIRouter, Request
from authlib.integrations.starlette_client import OAuth
from requests.models import PreparedRequest

oauth = OAuth()
router = APIRouter()

async def add_url_params(url: str, params: dict):
    req = PreparedRequest()
    req.prepare_url(url, params)
    return req.url

@router.get("/login/{provider}")
async def login(request: Request, provider: str):
    redirect_uri = await add_url_params(request.url_for('callback'), {"provider": provider})
    request.session["provider"] = provider
    return await getattr(oauth, provider).authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def callback(request: Request, provider: str):
    # TODO: store and validate state
    provider = request.session["provider"]
    token = await getattr(oauth, provider).authorize_access_token(request)
    request.session['user'] = dict(token['userinfo'])
    return token


def register_providers():
    oauth.register(
        name="glu",
        client_id="license-manager",
        client_secret="J2HDLw6E47sVmFjwmFgC",
        # server_metadata_url="https://glu.bettermarks.loc/o/.well-known/openid-configuration/",
        server_metadata_url="https://glu-ci00.bettermarks.com/o/.well-known/openid-configuration/",
        client_kwargs={
            "scope": "bm openid"
        }
    )