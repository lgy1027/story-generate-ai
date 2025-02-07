from fastapi import APIRouter

router = APIRouter(
    prefix="/api",
)

router.include_router(router)

