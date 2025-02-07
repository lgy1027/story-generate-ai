from fastapi import APIRouter
from app.api import llm

router = APIRouter(
    prefix="/api",
)

router.include_router(llm.router, prefix="/llm", tags=["llm"])

