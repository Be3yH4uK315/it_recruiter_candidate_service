from fastapi import APIRouter
from .endpoints import candidates

api_router = APIRouter()
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])