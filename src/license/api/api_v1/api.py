from fastapi import APIRouter

from license.api.api_v1.endpoints import license, product, status

api_router = APIRouter()

api_router.include_router(license.router, prefix="/users", tags=["Licenses"])
api_router.include_router(product.router, prefix="/products", tags=["Products"])
api_router.include_router(status.router, prefix="/status", tags=["Debug"])
