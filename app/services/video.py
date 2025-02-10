import app.schemas.video as video_schema
import time

async def generate_video(request: video_schema.VideoGenerateRequest):
    """
    生成视频
    Args:
        request (video_schema.VideoGenerateRequest): 视频生成请求
    """
    try:
        # 测试模式下，从 story.json 中读取请求参数
        if request.test_mode:
            request.task_id or str(int(time.time()))