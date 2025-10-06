from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from melo.api import TTS
import io
import logging
import time
from pydub import AudioSegment
import base64
from concurrent.futures import ThreadPoolExecutor
import asyncio
from contextlib import asynccontextmanager

from config import settings
from models import (
    TTSRequest, TTSResponse, HealthResponse, SpeakersResponse, APIInfo
)

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("melo-tts-api")

# App & Executor Setup
executor = ThreadPoolExecutor(max_workers=settings.MAX_WORKERS)
app = FastAPI(
    title="MeloTTS-API",
    description="High-performance Text-to-Speech API service powered by MeloTTS with multi-lingual support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model and state
tts_model = None
speakers = []
model_ready = False
startup_time = None

@asynccontextmanager
async def lifespan(_app: FastAPI):
    global tts_model, speakers, model_ready, startup_time
    startup_time = time.time()
    
    try:
        logger.info("🚀 Starting MeloTTS API...")
        logger.info("📊 Configuration: device=%s, language=%s", settings.get_device(), settings.LANGUAGE)
        
        # Load model
        logger.info("📥 Loading MeloTTS model...")
        tts_model = TTS(language=settings.LANGUAGE, device=settings.get_device())
        speakers = list(tts_model.hps.data.spk2id.keys())
        model_ready = True
        
        load_time = time.time() - startup_time
        logger.info("✅ Model loaded successfully in %.2fs", load_time)
        logger.info("🎤 Available speakers (%d): %s", len(speakers), speakers)
        
        yield
        
    except Exception as e:
        logger.error("❌ Failed to load model: %s", e)
        model_ready = False
        raise
    finally:
        logger.info("🛑 Shutting down MeloTTS API...")
        executor.shutdown(wait=True)
        logger.info("✅ Shutdown complete")

app.router.lifespan_context = lifespan

@app.get("/", response_model=APIInfo)
def root():
    """Get API information and status"""
    return APIInfo(
        name="MeloTTS-API",
        version="1.0.0",
        description="High-performance Text-to-Speech API service powered by MeloTTS",
        endpoints=["/tts", "/synthesize", "/speakers", "/health", "/docs"],
        supported_languages=["EN", "ES", "FR", "ZH", "JP", "KR"],
        max_text_length=settings.MAX_TEXT_LENGTH,
        supported_formats=["wav", "mp3"]
    )

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="ok" if model_ready else "loading",
        speakers_loaded=len(speakers) > 0,
        model_ready=model_ready,
        available_speakers=len(speakers),
        device=settings.get_device()
    )

@app.get("/speakers", response_model=SpeakersResponse)
def get_speakers():
    """Get available speakers grouped by language"""
    if not model_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not ready yet"
        )
    
    # Group speakers by language prefix
    language_groups = {}
    for speaker in speakers:
        lang = speaker.split('-')[0] if '-' in speaker else speaker
        if lang not in language_groups:
            language_groups[lang] = []
        language_groups[lang].append(speaker)
    
    return SpeakersResponse(
        speakers=speakers,
        total=len(speakers),
        languages=language_groups
    )

# ---------- Synthesis Helpers ----------
def generate_wav_audio(text: str, speaker: str, speed: float) -> io.BytesIO:
    """Generate WAV audio from text"""
    logger.info("🎵 Synthesizing (WAV) | speaker=%s, speed=%s, text='%s...'", speaker, speed, text[:30])
    
    if not model_ready:
        raise RuntimeError("Model is not ready")
    
    if speaker not in tts_model.hps.data.spk2id:
        raise ValueError(f"Speaker '{speaker}' not found")
    
    if len(text) > settings.MAX_TEXT_LENGTH:
        raise ValueError(f"Text too long. Maximum length: {settings.MAX_TEXT_LENGTH}")
    
    audio_io = io.BytesIO()
    tts_model.tts_to_file(text, tts_model.hps.data.spk2id[speaker], audio_io, speed=speed, format='wav')
    audio_io.seek(0)
    return audio_io

def generate_base64_mp3(text: str, speaker: str, speed: float) -> str:
    """Generate Base64 encoded MP3 audio from text"""
    logger.info("🎵 Synthesizing (MP3) | speaker=%s, speed=%s, text='%s...'", speaker, speed, text[:30])
    
    wav_io = generate_wav_audio(text, speaker, speed)
    audio_segment = AudioSegment.from_file(wav_io, format="wav")
    mp3_io = io.BytesIO()
    audio_segment.export(mp3_io, format="mp3")
    mp3_io.seek(0)
    return base64.b64encode(mp3_io.read()).decode("utf-8")

# ---------- Streaming Endpoint ----------
@app.post("/tts", response_class=StreamingResponse)
async def synthesize(request: TTSRequest):
    """Synthesize speech and stream as WAV audio"""
    if not model_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not ready yet"
        )
    
    try:
        loop = asyncio.get_event_loop()
        audio_io = await loop.run_in_executor(
            executor, 
            generate_wav_audio, 
            request.text, 
            request.speaker, 
            request.speed
        )
        return StreamingResponse(
            audio_io, 
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename=speech_{request.speaker}.wav"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error("❌ TTS synthesis failed: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Synthesis failed") from e

# ---------- Base64 MP3 Endpoint ----------
@app.post("/synthesize", response_model=TTSResponse)
async def synthesize_base64(request: TTSRequest):
    """Synthesize speech and return as Base64 encoded MP3"""
    if not model_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not ready yet"
        )
    
    try:
        loop = asyncio.get_event_loop()
        base64_audio = await loop.run_in_executor(
            executor, 
            generate_base64_mp3, 
            request.text, 
            request.speaker, 
            request.speed
        )
        
        return TTSResponse(
            audio_content=base64_audio,
            format="mp3",
            speaker=request.speaker,
            speed=request.speed
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error("❌ TTS synthesis failed: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Synthesis failed") from e