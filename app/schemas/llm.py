from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.models.const import Language
from typing import Optional

class StoryGenerationRequest(BaseModel):
    resolution: Optional[str] = Field(default="1024*1024", description="分辨率")
    text_llm_provider: Optional[str] = Field(default=None, description="文本模型供应商")
    text_llm_model: Optional[str] = Field(default=None, description="文本模型名称")
    image_llm_provider: Optional[str] = Field(default=None, description="图像模型供应商")
    image_llm_model: Optional[str] = Field(default=None, description="图像模型名称")
    segments: int = Field(...,ge=1,le=10, description="story segments")
    story_prompt: str = Field(..., min_length=20,max_length=4000,description="story prompt")
    language: Language = Field(default=Language.CHINESE_CN, description="story language")

class StorySegment(BaseModel):
    text: str = Field(..., description="story text")
    image_prompt: str = Field(..., description="Image generation prompt")
    url: str = Field(None, description="generation image url")
    
class StoryGenerationResponse(BaseModel):
     segments: List[StorySegment] = Field(..., description="Generated story segments")