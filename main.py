from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from melo.api import TTS
import io
import logging
from pydub import AudioSegment
import base64
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
import asyncio
from contextlib import asynccontextmanager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("melo-tts-api")

# App & Executor Setup
executor = ThreadPoolExecutor(max_workers=4)
app = FastAPI(
    title="MeloTTS API",
    description="Text-to-Speech API using MeloTTS",
    version="1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model
tts_model = None
speakers = []

class TTSRequest(BaseModel):
    text: str
    speaker: str = "EN-US"
    speed: float = 1.0

@asynccontextmanager
async def lifespan(app: FastAPI):
    global tts_model, speakers
    try:
        logger.info("Loading MeloTTS model...")
        tts_model = TTS(language='EN', device='cuda')  # or 'auto'
        speakers = list(tts_model.hps.data.spk2id.keys())
        logger.info(f"Model loaded. Available speakers: {speakers}")
        yield
    finally:
        logger.info("Shutting down ThreadPoolExecutor...")
        executor.shutdown(wait=True)

app.router.lifespan_context = lifespan

@app.get("/")
def root():
    return {"message": "MeloTTS API is running. Use /tts to synthesize speech."}

@app.get("/health")
def health_check():
    return {"status": "ok", "speakers_loaded": len(speakers) > 0}

@app.get("/speakers")
def get_speakers():
    return {"speakers": speakers}

# ---------- Synthesis Helpers ----------
def generate_wav_audio(text, speaker, speed):
    logger.info(f"Synthesizing (WAV) | speaker={speaker}, speed={speed}, text='{text[:30]}...'")
    audio_io = io.BytesIO()
    tts_model.tts_to_file(text, tts_model.hps.data.spk2id[speaker], audio_io, speed=speed, format='wav')
    audio_io.seek(0)
    return audio_io

def generate_base64_mp3(text, speaker, speed):
    logger.info(f"Synthesizing (MP3) | speaker={speaker}, speed={speed}, text='{text[:30]}...'")
    wav_io = generate_wav_audio(text, speaker, speed)
    audio_segment = AudioSegment.from_file(wav_io, format="wav")
    mp3_io = io.BytesIO()
    audio_segment.export(mp3_io, format="mp3")
    mp3_io.seek(0)
    return base64.b64encode(mp3_io.read()).decode("utf-8")

# ---------- Streaming Endpoint ----------
@app.post("/tts", response_class=StreamingResponse)
async def synthesize(request: TTSRequest):
    if request.speaker not in tts_model.hps.data.spk2id:
        return JSONResponse(status_code=400, content={"error": f"Speaker '{request.speaker}' not found."})
    
    loop = asyncio.get_event_loop()
    audio_io = await loop.run_in_executor(executor, generate_wav_audio, request.text, request.speaker, request.speed)
    return StreamingResponse(audio_io, media_type="audio/wav")

# ---------- Base64 MP3 Endpoint ----------
@app.post("/synthesize", response_model=dict)
async def synthesize_base64(request: TTSRequest):
    if request.speaker not in tts_model.hps.data.spk2id:
        return JSONResponse(status_code=400, content={"error": f"Speaker '{request.speaker}' not found."})

    loop = asyncio.get_event_loop()
    base64_audio = await loop.run_in_executor(executor, generate_base64_mp3, request.text, request.speaker, request.speed)
    return {"audio_content": base64_audio}