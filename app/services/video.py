import os
import json
import time
import requests
from typing import List, Dict, Any, Tuple

from http import HTTPStatus
from app.schemas.video import VideoGenerateRequest, StoryScene
from app.schemas.llm import StoryGenerationRequest
from app.services.llm import llm_service

import app.utils.utils as utils
import edge_tts
import uuid

from loguru import logger


async def generate_video(request: VideoGenerateRequest) -> str:
    """
    生成视频
    Args:
        request (video_schema.VideoGenerateRequest): 视频生成请求
    """
    try:
        # 测试模式下，从 story.json 中读取请求参数
        if request.test_mode:
            task_id = request.task_id or str(int(time.time()))
            task_dir = utils.task_dir(task_id)
            if not os.path.exists(task_dir):
                raise ValueError(f"Task directory {task_dir} does not exist.")
            story_file =  os.path.join(task_dir, "story.json")
            if not os.path.exists(story_file):
                raise ValueError(f"Story file {story_file} does not exist.")
            with open(story_file, "r", encoding="utf-8") as f:
                story_data = json.loads(f.read())
                print(f"story data:{story_data}")
            request = VideoGenerateRequest(**story_data)
            request.test_mode = True
            scenes = [StoryScene(**scene) for scene in story_data.get("scenes", [])]
        else:
            req = StoryGenerationRequest(
                resolution=request.resolution,
                story_prompt=request.story_prompt,
                language=request.language,
                segments=request.segments,
                text_llm_provider=request.text_llm_provider,
                text_llm_model=request.text_llm_model,
                image_llm_provider=request.image_llm_provider,
                image_llm_model=request.image_llm_model
            )
            story_list = await llm_service.generate_story_with_images(request=req)
            scenes = [StoryScene(**scene) for scene in story_list]
            
            # 保存story.json文件
            story_data = request.model_dump()
            story_data["scenes"] = scenes
            taskid = request.task_id or str(int(time.time()))
            task_dir = utils.task_dir(taskid)
            os.makedirs(task_dir, exist_ok=True)
            story_file = os.path.join(task_dir, "story.json")
            for i, scene in enumerate(story_list, 1):
                if scene.get("url"):
                    image_path = os.join(task_dir, f"{i}.jpg")
                    try:
                        resp = requests.get(scene["url"])
                        if resp.status_code == HTTPStatus.OK:
                            with open(image_path, "wb") as f:
                                f.write(resp.content)
                            logger.info(f"Download image {i}.jpg success")
                    except Exception as e:
                        logger.error(f"Download image {i}.jpg failed: {e}")
                        continue   
            with open(story_file, "w", encoding="utf-8") as f:
                json.dump(story_data, f, ensure_ascii=False, indent=2)
        return await create_video_with_scenes(task_dir, scenes, request.voice_name, request.voice_rate, request.test_mode)
    except Exception as e:
        logger.error(f"Error generating video: {e}")
        raise e
    
async def create_video_with_scenes(task_dir: str, scenes: List[StoryScene], voice_name: str, voice_rate: float, test_mode: bool = False) -> str:
    """创建带有场景的视频

    Args:
        task_dir (str): 任务目录
        scenes (List[StoryScene]): 场景列表
        voice_name (str): 语音名称
        voice_rate (float): 语音速率
        test_mode (bool): 是否为测试模式，如果是则使用已有的图片、音频、字幕文件

    Returns:
        str: _description_
    """
    clips = []
    for i,scene in enumerate(scenes,1):
        try:
            # 获取文件路径
            image_file = os.path.join(task_dir, f"{i}.png")
            audio_file = os.path.join(task_dir, f"{i}.mp3")
            subtitle_file = os.path.join(task_dir, f"{i}.srt")
            
            # 测试模式下检查文件是否存在
            if test_mode:
                if not all(os.path.exists(path) for path in [image_file, audio_file, subtitle_file]):
                    logger.warning(f"Test mode: Required files not found for scene {i}")
                    continue
            else:
                # 正常模式下生成文件
                logger.info(f"Processing scene {i}")
                await generate_voice(
                    scene.text,
                    voice_name,
                    voice_rate,
                    audio_file,
                    subtitle_file
                )
                

        except Exception as e:
            logger.error(f"Error: {e}")
            raise e
    return ""

async def generate_voice(text: str, voice_name: str, voice_rate: float = 0, audio_file: str = None, subtitle_file: str = None) -> Tuple[str, str]:
    """生成语音和字幕

    Args:
        text (str): 文本内容
        voice_name (str): 语音名称
        voice_rate (float, optional): 语音速率. Defaults to 0.
        audio_file (str, optional): 语音文件路径. Defaults to None.
        subtitle_file (str, optional): 字幕文件路径. Defaults to None.

    Returns:
        Tuple[str, str]: 语音文件路径, 字幕文件路径
    """
    if audio_file is None:
        audio_file = f"temp_{uuid.uuid4()}.mp3"
    if subtitle_file is None:
        subtitle_file = f"temp_{uuid.uuid4()}.srt" 
    
    # 生成语音
    sub_maker = await edge_tts_voice(text, voice_name, audio_file, voice_rate) 
    # 生成字幕
    
    return audio_file


async def edge_tts_voice(text: str, voice_name: str, audio_file: str, voice_rate: float) -> str:
    """"使用Edge TTS"""
    rate_str = convert_rate_to_percent(voice_rate)
    for i in range(3):
        try:
            logger.info(f"start, voice name: {voice_name}, try: {i + 1}")
            
    
async def convert_rate_to_percent(voice_rate: float) -> str:
    if voice_rate == 1.0:
        return "+0%"
    percent = round((voice_rate - 1.0) * 100, 2)
    return f"+{percent}%" if percent > 0  else f"{percent}%"
