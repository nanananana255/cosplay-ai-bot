from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from .queue import GenerationQueue
from bot.services.stability_api import generate_cosplay_image

app = FastAPI()
queue = GenerationQueue()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate")
async def generate_image(style: str, image: UploadFile = File(...)):
    image_bytes = await image.read()
    task_id = queue.add_task(image_bytes, style)
    return {"task_id": task_id}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    status = queue.get_status(task_id)
    return {"status": status}

# Worker для обработки очереди
async def process_queue():
    while True:
        task = queue.get_next_task()
        if task:
            try:
                result = await generate_cosplay_image(task['image'], task['style'])
                queue.set_result(task['id'], result)
            except Exception as e:
                queue.set_error(task['id'], str(e))
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(process_queue())