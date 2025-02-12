from fastapi import APIRouter
from app.api import llm,video

router = APIRouter(
    prefix="/api",
)

router.include_router(llm.router, prefix="/llm", tags=["llm"])
router.include_router(video.router, prefix="/video", tags=["video"])