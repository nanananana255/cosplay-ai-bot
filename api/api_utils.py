import logging
import json
import uuid
import requests
import redis
from datetime import datetime
from io import BytesIO
import asyncio

# Redis client setup
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    decode_responses=True
)

async def update_task_status(task_id: str, status: str, **kwargs):
    """Update task status in Redis"""
    try:
        task_data = redis_client.get(f"task:{task_id}")
        if task_data:
            task = json.loads(task_data)
            task["status"] = status
            task.update(kwargs)
            
            if status == TaskStatus.COMPLETED:
                task["completed_at"] = datetime.utcnow().isoformat()
            elif status == TaskStatus.FAILED:
                task["failed_at"] = datetime.utcnow().isoformat()
            
            redis_client.setex(
                f"task:{task_id}",
                timedelta(hours=24),
                json.dumps(task)
            )
    except Exception as e:
        logging.error(f"Error updating task status: {str(e)}")

async def process_image(task_id: str, image_url: str, style: str):
    """Process image with Stability AI"""
    try:
        await update_task_status(task_id, TaskStatus.PROCESSING)
        
        # 1. Download original image
        response = requests.get(image_url)
        if response.status_code != 200:
            raise Exception(f"Failed to download image: HTTP {response.status_code}")
        
        image_data = BytesIO(response.content)
        
        # 2. Prepare API request to Stability AI
        stability_url = f"https://api.stability.ai/v1/generation/{os.getenv('STABILITY_ENGINE_ID')}/text-to-image"
        
        headers = {
            "Authorization": f"Bearer {os.getenv('STABILITY_API_KEY')}",
            "Accept": "application/json"
        }
        
        # Get style configuration
        with open("styles.json") as f:
            styles = json.load(f)
        
        style_config = styles.get(style, styles["anime_samurai"])  # Default fallback
        
        data = {
            "text_prompts[0][text]": style_config["prompt"],
            "text_prompts[0][weight]": 1.0,
            "text_prompts[1][text]": style_config["negative_prompt"],
            "text_prompts[1][weight]": -1.0,
            "cfg_scale": style_config["cfg_scale"],
            "steps": style_config["steps"],
            "style_preset": style if style in ["anime", "photographic"] else None
        }
        
        files = {
            "init_image": ("input.png", image_data, "image/png"),
            "options": (None, json.dumps(data), "application/json")
        }
        
        # 3. Send to Stability AI
        response = requests.post(stability_url, headers=headers, files=files)
        
        if response.status_code != 200:
            error_msg = f"Stability AI error: {response.json().get('message', 'Unknown error')}"
            await update_task_status(
                task_id,
                TaskStatus.FAILED,
                error=error_msg
            )
            raise Exception(error_msg)
        
        # 4. Save result (in production you would upload to S3 or similar)
        result_path = f"results/{task_id}.png"
        with open(result_path, "wb") as f:
            f.write(response.content)
        
        result_url = f"{os.getenv('RESULT_BASE_URL')}/{result_path}"
        
        # 5. Update task status
        await update_task_status(
            task_id,
            TaskStatus.COMPLETED,
            result_url=result_url
        )
        
    except Exception as e:
        logging.error(f"Processing error for task {task_id}: {str(e)}")
        await update_task_status(
            task_id,
            TaskStatus.FAILED,
            error=str(e)
        )
        raise