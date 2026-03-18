"""FastAPI server with WebSocket support for real-time expression processing"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import json
import base64
import time
import os
import mediapipe as mp
from pathlib import Path

from backend.api.models import (
    HealthResponse,
    ExpressionResultResponse,
    RegisterExpressionRequest,
    RegisterExpressionResponse,
    ErrorResponse,
)
from backend.api.core import FacialRecognitionAPI, ExpressionAPI

# Initialize FastAPI app
app = FastAPI(
    title="Expression Recognition API",
    description="Real-time facial expression recognition using MediaPipe",
    version="1.0.0"
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize APIs
face_api = FacialRecognitionAPI()
expression_api = ExpressionAPI()

# Initialize MediaPipe FaceLandmarker
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Model path
model_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'core',
    'face_landmarker.task'
)

print(f"[Backend] Looking for face_landmarker.task at: {model_path}")
print(f"[Backend] Model exists: {os.path.exists(model_path)}")

# Create MediaPipe landmarker options
options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE,
    output_face_blendshapes=True,
    output_facial_transformation_matrixes=False,
    num_faces=1
)

# Create landmarker
landmarker = None
try:
    landmarker = FaceLandmarker.create_from_options(options)
    print("[Backend] FaceLandmarker loaded successfully!")
except Exception as e:
    print(f"[Backend] ERROR: Could not load face_landmarker.task: {e}")
    import traceback
    traceback.print_exc()


# ============ HTTP ENDPOINTS ============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="ok", version="1.0.0")


@app.post("/register-expression", response_model=RegisterExpressionResponse)
async def register_expression(request: RegisterExpressionRequest):
    """Register a new expression for a user"""
    try:
        result = expression_api.register(
            request.user_id,
            request.label,
            request.blendshapes
        )
        return RegisterExpressionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/expressions/{user_id}")
async def get_expressions(user_id: str):
    """Get all registered expressions for a user"""
    if user_id not in expression_api.expressions:
        return {"expressions": []}
    return {
        "user_id": user_id,
        "expressions": list(expression_api.expressions[user_id].keys())
    }


# ============ WEBSOCKET ============

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


def base64_to_cv2(base64_str: str):
    """Convert base64 string to OpenCV image"""
    try:
        img_data = base64.b64decode(base64_str)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error decoding base64: {e}")
        return None


def process_frame(frame: np.ndarray, user_id: str = "Usuario Principal"):
    """
    Process a frame and detect expressions.
    
    Returns:
        Tuple of (result_dict, latency_ms)
    """
    start_time = time.time()
    
    if frame is None:
        return None, 0
    
    # Check if landmarker was loaded
    if landmarker is None:
        return {
            "user_id": user_id,
            "expression": "Erro: Modelo não carregado",
            "confidence": 0.0,
            "latency_ms": 0,
            "timestamp_ms": int(time.time() * 1000),
            "blendshapes_count": 0,
            "top_blendshapes": [],
            "error": "FaceLandmarker model not loaded"
        }, 0
    
    try:
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create MediaPipe image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Detect landmarks
        result = landmarker.detect(mp_image)
        
        latency_ms = (time.time() - start_time) * 1000
        
        if not result.face_landmarks or not result.face_blendshapes:
            return {
                "user_id": user_id,
                "expression": "Nenhum rosto detectado",
                "confidence": 0.0,
                "latency_ms": latency_ms,
                "timestamp_ms": int(time.time() * 1000),
                "blendshapes_count": 0,
                "top_blendshapes": [],
                "face_detected": False,
                "bounding_box": None,
                "landmarks": []
            }, latency_ms
        
        # Get blendshapes
        blendshapes = result.face_blendshapes[0]
        blendshape_dicts = [
            {"category_name": b.category_name, "score": b.score}
            for b in blendshapes
        ]
        
        # Get face landmarks coordinates for drawing
        landmarks = result.face_landmarks[0]
        h, w = rgb_frame.shape[:2]
        
        # Calculate bounding box from landmarks
        x_coords = [int(mark.x * w) for mark in landmarks]
        y_coords = [int(mark.y * h) for mark in landmarks]
        bbox = {
            "xmin": max(0, min(x_coords) - 10),
            "ymin": max(0, min(y_coords) - 30),
            "xmax": min(w, max(x_coords) + 10),
            "ymax": min(h, max(y_coords) + 10)
        }
        
        # Extract landmark coordinates (sample every 5th for performance)
        landmarks_list = [
            {"x": int(mark.x * w), "y": int(mark.y * h)}
            for i, mark in enumerate(landmarks)
            if i % 5 == 0  # Every 5th landmark for smoother rendering
        ]
        
        # Predict expression
        prediction = expression_api.predict(user_id, blendshape_dicts)
        
        return {
            "user_id": user_id,
            "expression": prediction["expression"],
            "confidence": prediction["confidence"],
            "latency_ms": latency_ms,
            "timestamp_ms": int(time.time() * 1000),
            "blendshapes_count": len(blendshape_dicts),
            "top_blendshapes": prediction["top_blendshapes"],
            "face_detected": True,
            "bounding_box": bbox,
            "landmarks": landmarks_list
        }, latency_ms
        
    except Exception as e:
        print(f"[Backend] Error processing frame: {e}")
        import traceback
        traceback.print_exc()
        return {
            "user_id": user_id,
            "expression": f"Erro: {str(e)[:50]}",
            "confidence": 0.0,
            "latency_ms": (time.time() - start_time) * 1000,
            "timestamp_ms": int(time.time() * 1000),
            "blendshapes_count": 0,
            "top_blendshapes": [],
            "error": str(e)
        }, (time.time() - start_time) * 1000


@app.websocket("/ws/process-video")
async def websocket_process_video(websocket: WebSocket):
    """
    WebSocket endpoint for real-time video frame processing.
    
    Expected message format:
    {
        "action": "predict" | "register",
        "frame_base64": "...",
        "user_id": "Usuario Principal",
        "label": "..." (only for register action)
    }
    """
    print("[WebSocket] Client connecting...")
    await manager.connect(websocket)
    print("[WebSocket] Client connected!")
    
    try:
        frame_count = 0
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            frame_count += 1
            
            action = message.get("action", "predict")
            frame_base64 = message.get("frame_base64", "")
            user_id = message.get("user_id", "Usuario Principal")
            label = message.get("label")
            
            if frame_count % 30 == 0:  # Log every 30 frames
                print(f"[WebSocket] Received {frame_count} frames from {user_id}")
            
            # Decode frame
            frame = base64_to_cv2(frame_base64)
            
            if action == "predict":
                if frame is None:
                    await websocket.send_json({
                        "error": "Invalid frame",
                        "user_id": user_id
                    })
                    continue
                
                result, latency = process_frame(frame, user_id)
                await websocket.send_json(result)
            
            elif action == "register":
                if not label:
                    await websocket.send_json({
                        "error": "Label required for registration",
                        "user_id": user_id
                    })
                    continue
                
                if frame is None:
                    await websocket.send_json({
                        "error": "Invalid frame for registration",
                        "user_id": user_id
                    })
                    continue
                
                # Process frame to get blendshapes
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                result = landmarker.detect(mp_image)
                
                if not result.face_blendshapes:
                    await websocket.send_json({
                        "error": "No face detected for registration",
                        "user_id": user_id
                    })
                    continue
                
                blendshapes = result.face_blendshapes[0]
                blendshape_dicts = [
                    {"category_name": b.category_name, "score": b.score}
                    for b in blendshapes
                ]
                
                # Register expression
                reg_result = expression_api.register(user_id, label, blendshape_dicts)
                await websocket.send_json({
                    "action": "register_response",
                    "success": reg_result["success"],
                    "message": reg_result["message"],
                    "user_id": user_id,
                    "label": label
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"[WebSocket] Client disconnected after {frame_count} frames")
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            await websocket.send_json({
                "error": f"Server error: {str(e)}"
            })
        except:
            pass
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
