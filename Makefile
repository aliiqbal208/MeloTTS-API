# MeloTTS-API Makefile

.PHONY: help install dev-install run test clean docker-build docker-run docker-compose-up docker-compose-down

# Default target
help:
	@echo "MeloTTS-API - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  install        Install production dependencies"
	@echo "  dev-install    Install development dependencies"
	@echo "  run            Run the API server locally"
	@echo "  test           Run API tests"
	@echo "  clean          Clean up generated files"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build   Build Docker image"
	@echo "  docker-run     Run Docker container"
	@echo "  docker-compose-up    Start with docker-compose"
	@echo "  docker-compose-down  Stop docker-compose"
	@echo ""
	@echo "Utilities:"
	@echo "  format         Format code with black"
	@echo "  lint           Lint code with flake8"
	@echo "  type-check     Type check with mypy"

# Installation
install:
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✅ Production dependencies installed"

dev-install:
	pip install -r requirements.txt[dev]
	@echo "✅ Development dependencies installed"

# Running
run:
	@echo "🚀 Starting MeloTTS-API server..."
	python main.py

run-dev:
	@echo "🚀 Starting MeloTTS-API server in development mode..."
	uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# Testing
test:
	@echo "🧪 Running API tests..."
	python scripts/test_api.py

test-local:
	@echo "🧪 Running local tests..."
	python -m pytest tests/ -v

# Code quality
format:
	@echo "🎨 Formatting code..."
	black *.py scripts/ tests/
	@echo "✅ Code formatted"

lint:
	@echo "🔍 Linting code..."
	flake8 *.py scripts/ tests/
	@echo "✅ Linting complete"

type-check:
	@echo "🔍 Type checking..."
	mypy *.py scripts/
	@echo "✅ Type checking complete"

# Docker
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t melotts-api .
	@echo "✅ Docker image built"

docker-run: docker-build
	@echo "🐳 Running Docker container..."
	docker run -p 8080:8080 --name melotts-api-container melotts-api

docker-compose-up:
	@echo "🐳 Starting services with docker-compose..."
	docker-compose up -d
	@echo "✅ Services started"

docker-compose-down:
	@echo "🐳 Stopping services..."
	docker-compose down
	@echo "✅ Services stopped"

# Cleanup
clean:
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.wav" -delete
	find . -type f -name "*.mp3" -delete
	find . -type f -name "test_output_*" -delete
	@echo "✅ Cleanup complete"

# Development setup
setup-dev: dev-install
	@echo "🔧 Setting up development environment..."
	python -m venv venv
	@echo "✅ Development environment ready"
	@echo "💡 Activate with: source venv/bin/activate"

# Production setup
setup-prod: install
	@echo "🔧 Setting up production environment..."
	python MeloTTS/melo/init_downloads.py
	@echo "✅ Production environment ready"

# Health check
health:
	@echo "🏥 Checking API health..."
	curl -s http://localhost:8080/health | python -m json.tool

# Show logs
logs:
	@echo "📋 Showing container logs..."
	docker logs melotts-api-container -f

# Stop container
stop:
	@echo "🛑 Stopping container..."
	docker stop melotts-api-container || true
	docker rm melotts-api-container || true
	@echo "✅ Container stopped"
