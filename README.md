# MeloTTS-API

A high-performance FastAPI-based Text-to-Speech (TTS) service powered by [MeloTTS](https://github.com/myshell-ai/MeloTTS), providing multi-lingual speech synthesis with support for multiple speakers and languages.

## 🌟 Features

- **Multi-lingual Support**: English (US, UK, Australian, Indian), Spanish, French, Chinese, Japanese, Korean
- **Multiple Speakers**: Various speaker voices for each language
- **RESTful API**: Clean FastAPI endpoints for easy integration
- **Multiple Output Formats**: WAV streaming and Base64 MP3 encoding
- **Docker Support**: Ready-to-deploy containerized application
- **Web Interface**: Built-in HTML demo interface
- **Real-time Processing**: Optimized for CPU real-time inference
- **CORS Enabled**: Cross-origin requests supported

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mello-tts-api-main
   ```

2. **Build and run with Docker**
   ```bash
   docker build -t melotts-api .
   docker run -p 8080:8080 melotts-api
   ```

3. **Access the service**
   - API: `http://localhost:8080`
   - Web Interface: `http://localhost:8080` (serves the HTML demo)
   - API Documentation: `http://localhost:8080/docs`

### Local Development

1. **Install dependencies**
   ```bash
   # Production dependencies
   pip install -r requirements.txt
   
   # Development dependencies (optional)
   pip install -r requirements.txt[dev]
   ```

2. **Initialize MeloTTS models**
   ```bash
   python MeloTTS/melo/init_downloads.py
   ```

3. **Run the server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```

## 📚 API Documentation

### Endpoints

#### `GET /`
- **Description**: Health check and basic info
- **Response**: `{"message": "MeloTTS API is running. Use /tts to synthesize speech."}`

#### `GET /health`
- **Description**: Detailed health status
- **Response**: `{"status": "ok", "speakers_loaded": true}`

#### `GET /speakers`
- **Description**: List available speakers
- **Response**: `{"speakers": ["EN-US", "EN-AU", "JP", ...]}`

#### `POST /tts`
- **Description**: Synthesize speech and stream as WAV
- **Content-Type**: `audio/wav`
- **Request Body**:
  ```json
  {
    "text": "Hello, world!",
    "speaker": "EN-US",
    "speed": 1.0
  }
  ```

#### `POST /synthesize`
- **Description**: Synthesize speech and return as Base64 MP3
- **Response**:
  ```json
  {
    "audio_content": "base64_encoded_mp3_data"
  }
  ```

### Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | string | required | Text to synthesize |
| `speaker` | string | "EN-US" | Speaker voice to use |
| `speed` | float | 1.0 | Speech speed (0.5-2.0) |

### Supported Speakers

| Language | Speakers |
|----------|----------|
| English | EN-US, EN-AU, EN-BR, EN_INDIA, EN-Default |
| Spanish | ES |
| French | FR |
| Chinese | ZH (supports mixed Chinese-English) |
| Japanese | JP |
| Korean | KR |

## 🛠️ Usage Examples

### cURL Examples

**Stream WAV audio:**
```bash
curl -X POST "http://localhost:8080/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test!", "speaker": "EN-US", "speed": 1.0}' \
  --output speech.wav
```

**Get Base64 MP3:**
```bash
curl -X POST "http://localhost:8080/synthesize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test!", "speaker": "EN-US", "speed": 1.0}'
```

### Python Example

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

# Decode and play audio
audio_data = base64.b64decode(response.json()["audio_content"])
audio = AudioSegment.from_mp3(BytesIO(audio_data))
audio.export("output.wav", format="wav")
```

### JavaScript Example

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

## 🏗️ Project Structure

```
MeloTTS-API/
├── main.py                 # FastAPI application
├── config.py              # Configuration settings
├── models.py              # Pydantic models
├── requirements.txt       # Python dependencies (prod + dev)
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Multi-service setup
├── Makefile               # Build and run commands
├── index.html             # Web demo interface
├── README.md              # This file
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── tests/                 # Test files
└── MeloTTS/               # MeloTTS library (submodule)
    ├── melo/              # Core TTS implementation
    ├── docs/              # MeloTTS documentation
    └── setup.py           # MeloTTS package setup
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8080 | Server port |
| `CUDA_VISIBLE_DEVICES` | - | GPU device selection |

### Model Configuration

The service automatically downloads and initializes MeloTTS models on first startup. Models are cached locally for faster subsequent startups.

## 🐳 Docker Details

The Dockerfile includes:
- Python 3.9 slim base image
- System dependencies (ffmpeg, libsndfile1, etc.)
- Automatic model download and initialization
- Optimized for production deployment

### Docker Build Arguments

```dockerfile
# Build with specific Python version
FROM python:3.9-slim

# Expose port
EXPOSE 8080

# Set environment
ENV PORT=8080
```

## 🔧 Development

### Prerequisites

- Python 3.9+
- CUDA (optional, for GPU acceleration)
- Docker (optional)

### Setup Development Environment

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd mello-tts-api-main
   pip install -r requirements.txt
   ```

2. **Install MeloTTS in development mode**
   ```bash
   cd MeloTTS
   pip install -e .
   cd ..
   ```

3. **Run tests**
   ```bash
   python -m pytest MeloTTS/test/
   ```

### Code Structure

- `main.py`: FastAPI application with TTS endpoints
- `MeloTTS/`: Core TTS library and models
- `index.html`: Web interface for testing
- `Dockerfile`: Container configuration

## 🚀 Deployment

### Cloud Deployment

The service is designed for easy cloud deployment:

1. **Google Cloud Run**: Use the provided Dockerfile
2. **AWS ECS/Fargate**: Container-ready
3. **Azure Container Instances**: Direct deployment
4. **Kubernetes**: Use the Docker image

### Production Considerations

- **GPU Support**: Enable CUDA for faster inference
- **Scaling**: Use load balancers for multiple instances
- **Caching**: Consider Redis for model caching
- **Monitoring**: Add health checks and metrics

## 📄 License

This project uses the MeloTTS library, which is licensed under the MIT License. See [MeloTTS LICENSE](MeloTTS/LICENSE) for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Documentation**: Check the [MeloTTS documentation](MeloTTS/docs/)
- **API Docs**: Visit `/docs` when the server is running

## 🙏 Acknowledgments

- [MeloTTS](https://github.com/myshell-ai/MeloTTS) - The core TTS library
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [MyShell.ai](https://myshell.ai) - Original MeloTTS development

---

**Note**: This API service is built on top of MeloTTS, a high-quality multi-lingual text-to-speech library developed by MIT and MyShell.ai.
