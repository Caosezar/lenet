"""Pydantic models for API communication"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from enum import Enum


class BlendshapeData(BaseModel):
    """Individual blendshape value"""
    category_name: str
    score: float


class ExpressionResultResponse(BaseModel):
    """Response from expression prediction"""
    user_id: str
    expression: str
    confidence: float = Field(..., ge=0, le=100, description="Confidence percentage 0-100")
    latency_ms: float
    timestamp_ms: int
    blendshapes_count: int
    top_blendshapes: Optional[List[Dict[str, float]]] = Field(
        default=None,
        description="Top 5 active blendshapes"
    )


class RegisterExpressionRequest(BaseModel):
    """Request to register a new expression"""
    user_id: str
    label: str
    blendshapes: List[Dict[str, float]]


class RegisterExpressionResponse(BaseModel):
    """Response after expression registration"""
    success: bool
    message: str
    user_id: str
    label: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str


class FrameProcessingRequest(BaseModel):
    """WebSocket frame processing request"""
    frame_base64: str
    action: str = "predict"  # 'predict' or 'register'
    label: Optional[str] = None
    user_id: str = "Usuario Principal"


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
