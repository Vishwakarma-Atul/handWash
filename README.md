# handWash - Hand Washing Detection and Validation System

An AI-powered system that detects hand washing steps recomended by WHO, using computer vision and deep learning. The system uses classification technique to identify hand washing stages and ensure proper hand hygiene compliance.

## Demo

[![Watch Demo](https://img.youtube.com/vi/zyu-qG_9AtE/maxresdefault.jpg)](https://youtu.be/zyu-qG_9AtE)

## Project Overview

HandWash is a full-stack application that:
- Detects camera ad generate real-time video streams
- Real time classifies hand washing steps
- Validates completion of all hand washing steps
- Provides real-time feedback via WebSocket connections
- Combines multiple frames for improved classification accuracy

## Architecture

```
handWash/
├── frontend/            # React web application
├── backend/             # FastAPI server with inference
│   ├── main.py          # WebSocket endpoints
│   ├── app.py           # Inference logic
│   ├── utils/           # Helper functions
│   │   ├── classifier.py       # Classification wrapper
│   │   └── frame_combiner.py   # Frame stitching/combining
│   └── models/          # Pre-trained models
└── train/               # Training code and scripts
```

## Features

### Backend (FastAPI)
- **Real-time inference**: WebSocket endpoint for live hand washing detection
- **Frame optimization**: Combines multiple frames to improve classification accuracy
- **Step tracking**: Counts occurrences of each hand washing step

### Frontend (React)
- Interactive UI for hand washing detection
- Real-time progress tracking
- Step completion indicators
- Live video feed integration

### Model
- **Framework**: YOLOv11 (Ultralytics)
- **Task**: Image classification of hand washing steps
- **Input**: Combined frames from video stream
- **Output**: Classification probabilities for each step + background

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- Docker and Docker Compose (optional)

### Installation

#### Backend Setup

1. Create python virtual environment.
2. Install Python dependencies.
   ```bash
   python3 -m venv /env/path/name
   source /env/path/name/bin/activate
   pip install -r requirements.txt
   ```

3. Ensure the model is in place:
   - Model file should be at: `backend/models/classifier/best.pt`

#### Frontend Setup

1. Navigate to frontend directory.
2. Install dependencies.
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

#### Option 1: Docker Compose (Recommended)

```bash
docker-compose up
```

This will start:
- Frontend on `http://localhost:3000`
- Backend on `http://localhost:4550`

#### Option 2: Manual Setup

**Terminal 1 - Backend:**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 4550 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

Access the application at `http://localhost:3000`

## API Endpoints

### WebSocket Endpoints

#### `/ws` - Demo WebSocket
- **Purpose**: Simulates hand washing detection with random step classification

#### `/ws_model` - Real Model Inference
- **Purpose**: Processes video frames and performs real hand washing detection
- **Input**: Base64-encoded video frames (JPEG)
- **Output**:
  ```json
  {
    "status": "in_progress" | "complete",
    "counters": {
      "Step 1": 12,
      "Step 2": 8,
      "Step 3": 5,
      "background": 15
    },
    "message": "All steps are followed. Passed!",
    "max_count": 25
  }
  ```

### REST Endpoints

#### `GET /`
- Returns server status

### Frame Combining

The system combines multiple frames to improve classification accuracy:

- **Mean method**: Simple average of pixel values
- **Weighted method**: Exponential Moving Average (EMA) with alpha=0.1

Configured in `backend/utils/frame_combiner.py`

## Dependencies

### Backend
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **PyTorch**: Deep learning framework
- **Ultralytics**: YOLOv11 implementation
- **OpenCV (cv2)**: Image processing
- **NumPy**: Numerical operations

### Frontend
- **React**: UI framework
- **Node.js**: Runtime


## Performance

- **Frame Processing**: ~5 frames combined per inference (20 fps input = 4 inferences/sec)
- **Inference Time**: ~6.25 seconds per step completion
- **Confidence Threshold**: 0.75 minimum for classification


## Contact

Project developed by: Vishwakarma Atul
Repository: https://github.com/Vishwakarma-Atul/handWash
