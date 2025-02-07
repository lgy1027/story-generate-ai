import json
from app.config import get_settings
from openai import OpenAI
import dashscope
from app.schemas.llm import StoryGenerationRequest, StoryGenerationResponse
from typing import List, Dict, Any
from app.models.const import Language,LANGUAGE_NAMES
from loguru import logger
from app.exceptions import LLMResponseValidationError


settings = get_settings()
openai_client = None
aliyun_text_client = None
if settings.openai_api_key:
    openai_client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url or "https://api.chatanywhere.tech/v1")

if settings.aliyun_api_key:
    dashscope.api_key = settings.aliyun_api_key
    aliyun_text_client = OpenAI(api_key=settings.aliyun_api_key, base_url=settings.aliyun_base_url  or "https://dashscope.aliyuncs.com/compatible-mode/v1")

if settings.deepseek_api_key:
    deepseek_client = OpenAI(api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url or "https://api.deepseek.com/v1")

if settings.ollama_api_key:
    ollama_client = OpenAI(api_key=settings.ollama_api_key, base_url=settings.ollama_base_url or "http://localhost:11434/v1")

class LLMService:
    def __init__(self):
        self.openai_client = openai_client
        self.aliyun_text_client = aliyun_text_client
        self.text_llm_model = settings.text_llm_model
        self.image_llm_model = settings.image_llm_model
    
    async def generate_story(self, request: StoryGenerationRequest) -> List[Dict[str, Any]]:
        """生成故事场景

        Args:
            story_prompt (str): 故事提示. 必填参数.
            segments (int, optional): 故事分段数. Defaults to 3.

        Returns:
            List[Dict[str, Any]]: 故事场景列表
        """
        messages = [
            {"role": "system", "content": "你是一个专业的故事创作者，善于创作引人入胜的故事。请只返回JSON格式的内容。"},
            {"role": "user", "content": await self._get_story_prompt(request.story_prompt,request.language,request.segments)}
        ]
        
        logger.info(f"prompt messages: {json.dumps(messages, indent=4, ensure_ascii=False)}")
        
        response = await self._generate_response(text_llm_provider=request.text_llm_provider or None, text_llm_model=request.text_llm_model or None, messages=messages, response_format="json_object")

        response = response["list"]
        
        response = self.normalize_keys(response)
        
        logger.info(f"Generate story: {json.dumps(response, indent=4, ensure_ascii=False)}")
        
        self._validate_story_response(response)
        
    def normalize_keys(self,data):
        """
        阿里云和 openai 的模型返回结果不一致，处理一下
        修改对象中非 `text` 的键为 `image_prompt`
        - 如果是字典，替换 `text` 以外的单个键为 `image_prompt`
        - 如果是列表，对列表中的每个对象递归处理
        """
        if isinstance(data, dict):
            # 如果是字典，处理键值
            if "text" in data:
                # 找到非 `text` 的键
                other_keys = [key for key in data.keys() if key != "text"]
                if len(other_keys) == 1:
                    data["image_prompt"] = data.pop(other_keys[0])
                elif len(other_keys) > 1:
                    raise ValueError(f"Unexpected extra keys: {other_keys}. Only one non-'text' key is allowed.")
            return data
        elif isinstance(data, list):
            # 如果是列表，对列表中的每个对象递归处理
            return [self.normalize_keys(item) for item in data]
        else:
            # 其他类型，直接返回
            raise TypeError("Input must be a dict or list of dicts")

    def _validate_story_response(self,response:Any) -> None:
        """验证故事生成响应

        Args:
            data: LLM 响应

        Raises:
            LLMResponseValidationError: 响应格式错误
        """
        if not isinstance(response, list):
           raise LLMResponseValidationError("Response must be an array")
        
        for i, scene in enumerate(response):
            if not isinstance(scene, dict):
                raise LLMResponseValidationError(f"story item {i} must be an object")
            if "image_prompt" not in scene:
                raise LLMResponseValidationError(f"Scene {i} missing 'image_prompt' field")
            if "text" not in scene:
                raise LLMResponseValidationError(f"Scene {i} missing 'text' field")
            
            if not isinstance(scene["image_prompt"], str):
                raise LLMResponseValidationError(f"Scene {i} 'image_prompt' must be a string")
            if not isinstance(scene["text"], str):
                raise LLMResponseValidationError(f"Scene {i} 'text' must be a string")

    async def _generate_response(self, *, text_llm_provider: str = None, text_llm_model: str = None, messages: List[Dict[str, str]], response_format: str = "json_object") -> any:
        """生成 LLM 响应

        Args:
            messages: 消息列表
            response_format: 响应格式，默认为 json_object

        Returns:
            Dict[str, Any]: 解析后的响应

        Raises:
            Exception: 请求失败或解析失败时抛出异常
        """
        if text_llm_provider == "":
            text_llm_provider = settings.text_provider
        if text_llm_provider == "aliyun":
            text_client = aliyun_text_client
        elif text_llm_provider == "openai":
            text_client = self.openai_client
        elif text_llm_provider == "deepseek":
            text_client = deepseek_client
        elif text_llm_provider == "ollama":
            text_client = ollama_client
        
        if text_llm_model == "":
            text_llm_model = settings.text_llm_model
            
        response = text_client.chat.completions.create(
            model=text_llm_model,
            messages=messages,
            response_format={"type": response_format}
        )
        
        try:
          content = response.choices[0].message.content 
          result = json.loads(content)
          return result
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            raise e
        
    async def _get_story_prompt(self,story_prompt: str = None, language: Language = Language.CHINESE_CN, segments: int = 3, ) -> str:
        """_summary_

        Args:
            story_prompt (str, optional): 故事提示. Defaults to None.
            language (Language, optional): 故事语言. Defaults to Language.CHINESE_CN.
            segments (int, optional): 故事分段数. Defaults to 3.

        Returns:
            str: 完整的提示词
        """
        languageValue = LANGUAGE_NAMES[language]
        if story_prompt:
            base_prompt = f"讲一个故事，主题是:{story_prompt}"
        
        return f"""
        {base_prompt}. The story needs to be divided into {segments} scenes, and each scene must include descriptive text and an image prompt.

        Please return the result in the following JSON format, where the key `list` contains an array of objects:

        **Expected JSON format**:
        {{
            "list": [
                {{
                    "text": "Descriptive text for the scene",
                    "image_prompt": "Detailed image generation prompt, described in English"
                }},
                {{
                    "text": "Another scene description text",
                    "image_prompt": "Another detailed image generation prompt in English"
                }}
            ]
        }}
        
        **Requirements**
        1. The root object must contain a key named `list`, and its value must be an array of scene objects.
        2. Each object in the `list` array must include:
            - `text`: A descriptive text for the scene, written in {languageValue}.
            - `image_prompt`: A detailed prompt for generating an image, written in English.
        3. Ensure the JSON format matches the above example exactly. Avoid extra fields or incorrect key names like `cimage_prompt` or `inage_prompt`.

        **Important**:
        - If there is only one scene, the array under `list` should contain a single object.
        - The output must be a valid JSON object. Do not include explanations, comments, or additional content outside the JSON.

        Example output:
        {{
            "list": [
                {{
                    "text": "Scene description text",
                    "image_prompt": "Detailed image generation prompt in English"
                }}
            ]
        }}
        """