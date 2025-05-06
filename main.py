from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from melo.api import TTS
import io
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("melo-tts-api")

app = FastAPI(
    title="MeloTTS API",
    description="Text-to-Speech API using MeloTTS",
    version="1.0",
)

# Enable CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global TTS model and speaker list
tts_model = None
speakers = []

@app.on_event("startup")
def load_model():
    global tts_model, speakers
    try:
        logger.info("Loading MeloTTS model...")
        tts_model = TTS(language='EN', device='cuda')  # or 'auto'
        speakers = list(tts_model.hps.data.spk2id.keys())
        logger.info(f"Model loaded. Available speakers: {speakers}")
    except Exception as e:
        logger.exception("Failed to initialize MeloTTS.")
        raise RuntimeError(f"Startup failed: {e}")

@app.get("/")
def root():
    return {"message": "MeloTTS API is running. Use /tts to synthesize speech."}

@app.get("/health")
def health_check():
    return {"status": "ok", "speakers_loaded": len(speakers) > 0}

@app.get("/speakers")
def get_speakers():
    return {"speakers": speakers}

@app.get("/tts", response_class=StreamingResponse)
def synthesize(
    text: str = Query(..., description="Text to synthesize"),
    speaker: str = Query("EN-US", description="Speaker ID"),
    speed: float = Query(1.0, ge=0.1, le=5.0, description="Speech speed multiplier")
):
    try:
        if speaker not in tts_model.hps.data.spk2id:
            logger.warning(f"Speaker '{speaker}' not found.")
            return JSONResponse(status_code=400, content={"error": f"Speaker '{speaker}' not found."})

        logger.info(f"Generating audio | speaker={speaker}, speed={speed}, text='{text[:30]}...'")
        audio_io = io.BytesIO()
        tts_model.tts_to_file(text, tts_model.hps.data.spk2id[speaker], audio_io, speed=speed, format='wav')
        audio_io.seek(0)
        return StreamingResponse(audio_io, media_type="audio/wav")

    except Exception as e:
        logger.exception("Synthesis failed.")
        return JSONResponse(status_code=500, content={"error": str(e)})