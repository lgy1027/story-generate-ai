from fastapi import APIRouter
from app.schemas.video import VideoGenerateRequest, VideoGenerateResponse

router = APIRouter()

@router.post("/generater",response_class=VideoGenerateResponse)
async def generater(request: VideoGenerateRequest) -> VideoGenerateResponse:
    