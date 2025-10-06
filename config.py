"""
Configuration settings for MeloTTS API
"""

import os
from typing import List

class Settings:
    """Application settings"""
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))
    
    # Model settings
    DEVICE: str = os.getenv("DEVICE", "auto")  # auto, cpu, cuda, mps
    LANGUAGE: str = os.getenv("LANGUAGE", "EN")
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))
    
    # API settings
    MAX_TEXT_LENGTH: int = int(os.getenv("MAX_TEXT_LENGTH", "1000"))
    DEFAULT_SPEAKER: str = os.getenv("DEFAULT_SPEAKER", "EN-US")
    DEFAULT_SPEED: float = float(os.getenv("DEFAULT_SPEED", "1.0"))
    
    # CORS settings
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Model paths
    MODEL_CACHE_DIR: str = os.getenv("MODEL_CACHE_DIR", "./models")
    
    @classmethod
    def get_device(cls) -> str:
        """Get the appropriate device for model inference"""
        if cls.DEVICE == "auto":
            try:
                import torch
                if torch.cuda.is_available():
                    return "cuda"
                elif torch.backends.mps.is_available():
                    return "mps"
                else:
                    return "cpu"
            except ImportError:
                return "cpu"
        return cls.DEVICE

# Global settings instance
settings = Settings()
