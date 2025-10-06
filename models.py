"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any

class TTSRequest(BaseModel):
    """Request model for TTS synthesis"""
    text: str = Field(..., min_length=1, max_length=1000, description="Text to synthesize")
    speaker: str = Field(default="EN-US", description="Speaker voice to use")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed (0.5-2.0)")
    
    @validator('text')
    def validate_text(cls, v):
        """Validate text input"""
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()
    
    @validator('speed')
    def validate_speed(cls, v):
        """Validate speed parameter"""
        if not 0.5 <= v <= 2.0:
            raise ValueError("Speed must be between 0.5 and 2.0")
        return v

class TTSResponse(BaseModel):
    """Response model for base64 TTS synthesis"""
    audio_content: str = Field(..., description="Base64 encoded audio content")
    format: str = Field(default="mp3", description="Audio format")
    duration: Optional[float] = Field(None, description="Audio duration in seconds")
    speaker: str = Field(..., description="Speaker used for synthesis")
    speed: float = Field(..., description="Speed used for synthesis")

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    speakers_loaded: bool = Field(..., description="Whether speakers are loaded")
    model_ready: bool = Field(..., description="Whether model is ready")
    available_speakers: int = Field(..., description="Number of available speakers")
    device: str = Field(..., description="Device being used for inference")

class SpeakersResponse(BaseModel):
    """Speakers list response model"""
    speakers: List[str] = Field(..., description="List of available speakers")
    total: int = Field(..., description="Total number of speakers")
    languages: Dict[str, List[str]] = Field(..., description="Speakers grouped by language")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

class APIInfo(BaseModel):
    """API information response model"""
    name: str = Field(..., description="API name")
    version: str = Field(..., description="API version")
    description: str = Field(..., description="API description")
    endpoints: List[str] = Field(..., description="Available endpoints")
    supported_languages: List[str] = Field(..., description="Supported languages")
    max_text_length: int = Field(..., description="Maximum text length")
    supported_formats: List[str] = Field(..., description="Supported audio formats")
