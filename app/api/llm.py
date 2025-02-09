from fastapi import APIRouter, HTTPException
from typing import List,Dict
from enum import Enum
from loguru import logger
from app.schemas.llm import (
    StoryGenerationResponse,
    StoryGenerationRequest,
    ImageGenerationRequest,
    ImageGenerationResponse
)
from app.services.llm import llm_service


router = APIRouter()

class LLMType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    
@router.post("/story",response_model=StoryGenerationResponse)
async def generate_story(request: StoryGenerationRequest) -> StoryGenerationResponse:
    """根据给定的prompt生成故事"""
    try:
        resp = await llm_service.generate_story(request)
        return StoryGenerationResponse(segments=resp)
    except Exception as e:
        logger.error(f"Error generating story: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating story, err msg:{e}")
    
@router.post("/image",response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest) -> ImageGenerationResponse:
    """根据给定的prompt生成图片"""
    try:
        image_url = await llm_service.generate_image(prompt=request.prompt, image_llm_provider=request.image_llm_provider, image_llm_model=request.image_llm_model, resolution=request.resolution)
        return ImageGenerationResponse(image_url=image_url)
    except Exception as e:
        logger.error(f"Error generating story: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating story,err msg:{e}")
    

@router.post("/story-with-images", response_model=StoryGenerationResponse)
async def generate_story_with_images(request: StoryGenerationRequest) -> StoryGenerationResponse:
    """生成故事和配图"""
    try:
        segments = await llm_service.generate_story_with_images(request)
        return StoryGenerationResponse(segments=segments)
    except Exception as e:
        logger.error(f"Failed to generate story with images: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/providers", response_model=Dict[str, List[str]])
async def get_llm_providers():
    """
    获取 LLM Provider 列表
    """
    # 这里将实现获取 LLM Provider 的逻辑
    return llm_service.get_llm_providers()