from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Story Flicks"
    debug: bool = True
    version: str = "1.0.0"
    
    text_provider: str = "openai"
    image_provider: str = "openai"
    
    openai_base_url: str = "https://api.openai.com/v1"
    aliyun_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    ollama_base_url: str = "http://localhost:11434/v1"
    
    openai_api_key: str = ""
    aliyun_api_key: str = ""
    deepseek_api_key: str = ""
    ollama_api_key: str = ""
    
    text_llm_model: str = "gpt-4o"
    image_llm_model: str = "dall-e-3"

    class Config:
        env_file = ".env"
      
@lru_cache()
def get_settings() -> Settings:
    return Settings()

