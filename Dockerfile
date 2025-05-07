FROM python:3.9-slim

WORKDIR /app

COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential libsndfile1 curl ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Download unidic (required by Mecab tokenizer in MeloTTS)
RUN python -m unidic download || true

# Download required NLTK data (used by some text preprocessors in MeloTTS)
RUN python -c "\
import nltk; \
nltk.download('punkt'); \
nltk.download('averaged_perceptron_tagger_eng'); \
nltk.download('stopwords');"

# Initialize MeloTTS models
RUN python MeloTTS/melo/init_downloads.py

# Set port
ENV PORT=8080
EXPOSE ${PORT}

# Start the server
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]