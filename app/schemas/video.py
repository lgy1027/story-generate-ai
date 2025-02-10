from pydantic import BaseModel,Field
from typing import Optional,Dict,Any
from app.models.const import Language, ImageStyle


class VideoGenerateRequest(BaseModel):
    """视频生成请求"""
    text_llm_provider: Optional[str] = Field(default=None, description="Text LLM provider")
    image_llm_provider: Optional[str] = Field(default=None, description="Image LLM provider")
    text_llm_model: Optional[str] = Field(default=None, description="Text LLM model")
    image_llm_model: Optional[str] = Field(default=None, description="Image LLM model")
    test_mode: bool = Field(default=False, description="是否为测试模式")
    task_id: Optional[str] = Field(default=None, description="任务ID")
    segments: int = Field(default=3, ge=1, le=10, description="分段数量")
    language: Language = Field(default=Language.CHINESE_CN, description="故事语言")
    story_prompt: Optional[str] = Field(default=None, description="故事提示词")
    image_style: ImageStyle = Field(default=ImageStyle.realistic, description="图片风格")
    voice_name: str = Field(default="zh-CN-XiaoxiaoNeural", description="语音名称")
    voice_rate: float = Field(default=1.0, description="语音速率")
    resolution: Optional[str] = Field(default="1024*1024", description="分辨率")

class VideoGenerateResponse(BaseModel):
    """视频生成响应"""
    success: bool
    data: Optional[Dict[str,Any]] = None
    message: Optional[str] = None