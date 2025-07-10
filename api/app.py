from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api_utils import process_image
import logging
import uuid
import os
import redis
import json
from datetime import datetime, timedelta

app = FastAPI()

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    decode_responses=True
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@app.post("/generate")
async def generate_image(request: Request):
    data = await request.json()
    try:
        task_id = str(uuid.uuid4())
        style = data.get('style')
        image_url = data.get('image_url')
        user_id = data.get('user_id')
        
        if not all([style, image_url, user_id]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required parameters: style, image_url or user_id"
            )
        
        # Create task record in Redis
        task_data = {
            "task_id": task_id,
            "status": TaskStatus.PENDING,
            "created_at": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "style": style,
            "image_url": image_url,
            "result_url": None,
            "error": None
        }
        
        redis_client.setex(
            f"task:{task_id}",
            timedelta(hours=24),
            json.dumps(task_data)
        )
        
        # Start processing (in background)
        await process_image(task_id, image_url, style)
        
        return JSONResponse({
            "status": TaskStatus.PENDING,
            "task_id": task_id,
            "message": "Task accepted for processing"
        }, status_code=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        logging.error(f"Generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    try:
        task_data = redis_client.get(f"task:{task_id}")
        if not task_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
            
        task = json.loads(task_data)
        
        response = {
            "task_id": task_id,
            "status": task.get("status"),
            "created_at": task.get("created_at"),
            "user_id": task.get("user_id"),
            "style": task.get("style")
        }
        
        if task["status"] == TaskStatus.COMPLETED:
            response["result_url"] = task.get("result_url")
        elif task["status"] == TaskStatus.FAILED:
            response["error"] = task.get("error")
            
        return JSONResponse(response)
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid task data format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/user/tasks/{user_id}")
async def get_user_tasks(user_id: str, limit: int = 10):
    try:
        # This is a simplified example - in production you might want to use
        # Redis search or a separate database for this query
        all_keys = redis_client.keys("task:*")
        user_tasks = []
        
        for key in all_keys[:1000]:  # Limit scan for performance
            task_data = redis_client.get(key)
            if task_data:
                task = json.loads(task_data)
                if task.get("user_id") == user_id:
                    user_tasks.append({
                        "task_id": task.get("task_id"),
                        "status": task.get("status"),
                        "created_at": task.get("created_at"),
                        "style": task.get("style")
                    })
        
        # Sort by date and limit
        user_tasks.sort(key=lambda x: x["created_at"], reverse=True)
        return JSONResponse(user_tasks[:limit])
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)