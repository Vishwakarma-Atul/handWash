from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import cv2
import numpy as np
import random, base64

from .app import inferance

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Define classes here
    classes = ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"]
    MAX_COUNT = 100

    await websocket.accept()
    class_counters = {cls: 0 for cls in classes}
    try:
        data = await websocket.receive_json()
        print("Received from client:", data)  # This will print the received message
        while True:
            
            # Simulate classification of 10 frames
            for _ in range(10):
                classified_class = random.choice(classes)
                class_counters[classified_class] = min(class_counters[classified_class] + 1, MAX_COUNT)
            
            all_complete = all(count >= MAX_COUNT for count in class_counters.values())
            await websocket.send_json({
                "status": "complete" if all_complete else "in_progress",
                "counters": class_counters,
                "message": "All steps are followed. Passed!" if all_complete else ""
            })
            print(f"Sent to client: {class_counters}")
            
            if all_complete:
                break
            
            await asyncio.sleep(0.2)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()

@app.websocket("/ws_model")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    infr = inferance()
    MAX_COUNT = 100

    try:
        while True:
            frame_data = await websocket.receive_text()
            # Remove the data URL prefix
            _, encoded = frame_data.split(',', 1)
            # Decode the base64 string
            nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
            # Decode the image
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            result = infr.predict(frame, MAX_COUNT=MAX_COUNT)
            print("result : ", result, infr.result)

            all_complete = all(count >= MAX_COUNT for count in infr.result.values())

            await websocket.send_json({
                "status": "complete" if all_complete else "in_progress",
                "counters": infr.result,
                "message": "All steps are followed. Passed!" if all_complete else "",
                "max_count": MAX_COUNT
            })
            print(f"Sent to client: {infr.result}")
            if all_complete: break

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
