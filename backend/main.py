from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define classes here
classes = ["Class1", "Class2", "Class3", "Class4", "Class5"]
MAX_COUNT = 100

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    class_counters = {cls: 0 for cls in classes}
    try:
        while True:
            # Simulate classification of 10 frames
            for _ in range(10):
                classified_class = random.choice(classes)
                class_counters[classified_class] = min(class_counters[classified_class] + 1, MAX_COUNT)
            
            all_complete = all(count >= MAX_COUNT for count in class_counters.values())
            await websocket.send_json({
                "status": "complete" if all_complete else "in_progress",
                "counters": class_counters,
                "message": "All classes have reached 100. Test passed!" if all_complete else ""
            })
            print(f"Sent to client: {class_counters}")
            
            if all_complete:
                break
            
            await asyncio.sleep(0.2)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()

@app.get("/")
async def root():
    return {"message": "Classification server is running"}


### prod 
## uvicorn main:app --host 0.0.0.0 --port 4550 --workers 4

### dev
## uvicorn main:app --host 0.0.0.0 --port 4550 --reload
