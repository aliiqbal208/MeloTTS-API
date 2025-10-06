# MeloTTS API Documentation

## Overview

The MeloTTS API provides a RESTful interface for text-to-speech synthesis using the MeloTTS library. It supports multiple languages and speakers with both streaming and base64-encoded audio output formats.

## Base URL

```
http://localhost:8080
```

## Authentication

Currently, no authentication is required. All endpoints are publicly accessible.

## Endpoints

### 1. API Information

#### `GET /`

Get basic API information and status.

**Response:**
```json
{
  "name": "MeloTTS API",
  "version": "1.0.0",
  "description": "High-performance Text-to-Speech API using MeloTTS",
  "endpoints": ["/tts", "/synthesize", "/speakers", "/health", "/docs"],
  "supported_languages": ["EN", "ES", "FR", "ZH", "JP", "KR"],
  "max_text_length": 1000,
  "supported_formats": ["wav", "mp3"]
}
```

### 2. Health Check

#### `GET /health`

Check the health status of the API and model.

**Response:**
```json
{
  "status": "ok",
  "speakers_loaded": true,
  "model_ready": true,
  "available_speakers": 5,
  "device": "cuda"
}
```

**Status Values:**
- `ok`: API is fully operational
- `loading`: Model is still loading

### 3. Available Speakers

#### `GET /speakers`

Get a list of available speakers grouped by language.

**Response:**
```json
{
  "speakers": ["EN-US", "EN-AU", "JP", "ES", "FR"],
  "total": 5,
  "languages": {
    "EN": ["EN-US", "EN-AU"],
    "JP": ["JP"],
    "ES": ["ES"],
    "FR": ["FR"]
  }
}
```

### 4. Text-to-Speech (Streaming)

#### `POST /tts`

Synthesize speech and stream as WAV audio.

**Request Body:**
```json
{
  "text": "Hello, world!",
  "speaker": "EN-US",
  "speed": 1.0
}
```

**Parameters:**
- `text` (string, required): Text to synthesize (1-1000 characters)
- `speaker` (string, optional): Speaker voice (default: "EN-US")
- `speed` (float, optional): Speech speed 0.5-2.0 (default: 1.0)

**Response:**
- Content-Type: `audio/wav`
- Body: WAV audio data

**Example:**
```bash
curl -X POST "http://localhost:8080/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!", "speaker": "EN-US", "speed": 1.0}' \
  --output speech.wav
```

### 5. Text-to-Speech (Base64)

#### `POST /synthesize`

Synthesize speech and return as Base64 encoded MP3.

**Request Body:**
```json
{
  "text": "Hello, world!",
  "speaker": "EN-US",
  "speed": 1.0
}
```

**Response:**
```json
{
  "audio_content": "base64_encoded_mp3_data",
  "format": "mp3",
  "speaker": "EN-US",
  "speed": 1.0
}
```

**Example:**
```bash
curl -X POST "http://localhost:8080/synthesize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!", "speaker": "EN-US", "speed": 1.0}'
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Speaker 'INVALID-SPEAKER' not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "text"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

### 503 Service Unavailable
```json
{
  "detail": "Model is not ready yet"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Synthesis failed"
}
```

## Supported Languages and Speakers

| Language | Speakers | Description |
|----------|----------|-------------|
| English | EN-US, EN-AU, EN-BR, EN_INDIA, EN-Default | Various English accents |
| Spanish | ES | Spanish |
| French | FR | French |
| Chinese | ZH | Chinese (supports mixed Chinese-English) |
| Japanese | JP | Japanese |
| Korean | KR | Korean |

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production deployments.

## CORS

Cross-Origin Resource Sharing (CORS) is enabled for all origins by default. Configure `CORS_ORIGINS` environment variable for production.

## Examples

### Python

```python
import requests
import base64
from io import BytesIO
from pydub import AudioSegment

# Synthesize speech
response = requests.post("http://localhost:8080/synthesize", json={
    "text": "Hello, this is a test!",
    "speaker": "EN-US",
    "speed": 1.0
})

# Decode and save audio
audio_data = base64.b64decode(response.json()["audio_content"])
audio = AudioSegment.from_mp3(BytesIO(audio_data))
audio.export("output.wav", format="wav")
```

### JavaScript

```javascript
async function synthesizeSpeech(text, speaker = "EN-US", speed = 1.0) {
  const response = await fetch("http://localhost:8080/synthesize", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ text, speaker, speed })
  });
  
  const data = await response.json();
  const audioBlob = base64ToBlob(data.audio_content, "audio/mp3");
  const audioUrl = URL.createObjectURL(audioBlob);
  
  // Play audio
  const audio = new Audio(audioUrl);
  audio.play();
}

function base64ToBlob(base64, mimeType) {
  const byteCharacters = atob(base64);
  const byteArrays = [];
  for (let i = 0; i < byteCharacters.length; i += 512) {
    const slice = byteCharacters.slice(i, i + 512);
    const byteNumbers = new Array(slice.length);
    for (let j = 0; j < slice.length; j++) {
      byteNumbers[j] = slice.charCodeAt(j);
    }
    byteArrays.push(new Uint8Array(byteNumbers));
  }
  return new Blob(byteArrays, { type: mimeType });
}
```

### cURL

```bash
# Get available speakers
curl http://localhost:8080/speakers

# Synthesize speech (streaming)
curl -X POST "http://localhost:8080/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!", "speaker": "EN-US", "speed": 1.0}' \
  --output speech.wav

# Synthesize speech (base64)
curl -X POST "http://localhost:8080/synthesize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!", "speaker": "EN-US", "speed": 1.0}'
```

## Configuration

The API can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8080 | Server port |
| `DEVICE` | auto | Device for inference (auto, cpu, cuda, mps) |
| `LANGUAGE` | EN | Default language |
| `MAX_WORKERS` | 4 | Number of worker threads |
| `MAX_TEXT_LENGTH` | 1000 | Maximum text length |
| `DEFAULT_SPEAKER` | EN-US | Default speaker |
| `DEFAULT_SPEED` | 1.0 | Default speed |
| `CORS_ORIGINS` | * | CORS allowed origins |
| `LOG_LEVEL` | INFO | Logging level |
