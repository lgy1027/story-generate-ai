from fastapi import APIRouter, HTTPException
from typing import List,Dict
from enum import Enum
from loguru import logger
from app.schemas.llm import (
    StoryGenerationResponse,
    StoryGenerationRequest
)

router = APIRouter()

class LLMType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    
@router.get("/story",response_model=StoryGenerationResponse)
async def generate_story(request: StoryGenerationRequest) -> StoryGenerationResponse:
    """根据给定的prompt生成故事"""