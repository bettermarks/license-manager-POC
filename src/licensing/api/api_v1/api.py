from fastapi import APIRouter

from licensing.api.api_v1.endpoints import license, oidc, product, status

api_router = APIRouter()

api_router.include_router(license.router, prefix="/users", tags=["Licenses"])
api_router.include_router(product.router, prefix="/products", tags=["Products"])
api_router.include_router(status.router, prefix="/status", tags=["Debug"])
api_router.include_router(oidc.router, prefix="/oidc", tags=["Auth"])
