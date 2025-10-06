"""
Unit tests for MeloTTS API
"""

import pytest
import requests
import json
from unittest.mock import patch, MagicMock
import io
import base64

# Test configuration
API_BASE_URL = "http://localhost:8080"

class TestMeloTTSAPI:
    """Test cases for MeloTTS API endpoints"""
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{API_BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "speakers_loaded" in data
        assert "model_ready" in data
        assert "available_speakers" in data
        assert "device" in data
    
    def test_speakers_endpoint(self):
        """Test speakers endpoint"""
        response = requests.get(f"{API_BASE_URL}/speakers")
        assert response.status_code == 200
        
        data = response.json()
        assert "speakers" in data
        assert "total" in data
        assert "languages" in data
        assert isinstance(data["speakers"], list)
        assert isinstance(data["languages"], dict)
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = requests.get(f"{API_BASE_URL}/")
        assert response.status_code == 200
        
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert "endpoints" in data
        assert "supported_languages" in data
    
    def test_tts_endpoint_invalid_speaker(self):
        """Test TTS endpoint with invalid speaker"""
        payload = {
            "text": "Hello, world!",
            "speaker": "INVALID-SPEAKER",
            "speed": 1.0
        }
        
        response = requests.post(f"{API_BASE_URL}/tts", json=payload)
        assert response.status_code == 400
    
    def test_synthesize_endpoint_invalid_speaker(self):
        """Test synthesize endpoint with invalid speaker"""
        payload = {
            "text": "Hello, world!",
            "speaker": "INVALID-SPEAKER",
            "speed": 1.0
        }
        
        response = requests.post(f"{API_BASE_URL}/synthesize", json=payload)
        assert response.status_code == 400
    
    def test_tts_endpoint_empty_text(self):
        """Test TTS endpoint with empty text"""
        payload = {
            "text": "",
            "speaker": "EN-US",
            "speed": 1.0
        }
        
        response = requests.post(f"{API_BASE_URL}/tts", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_synthesize_endpoint_empty_text(self):
        """Test synthesize endpoint with empty text"""
        payload = {
            "text": "",
            "speaker": "EN-US",
            "speed": 1.0
        }
        
        response = requests.post(f"{API_BASE_URL}/synthesize", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_tts_endpoint_invalid_speed(self):
        """Test TTS endpoint with invalid speed"""
        payload = {
            "text": "Hello, world!",
            "speaker": "EN-US",
            "speed": 3.0  # Invalid speed
        }
        
        response = requests.post(f"{API_BASE_URL}/tts", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_synthesize_endpoint_invalid_speed(self):
        """Test synthesize endpoint with invalid speed"""
        payload = {
            "text": "Hello, world!",
            "speaker": "EN-US",
            "speed": 3.0  # Invalid speed
        }
        
        response = requests.post(f"{API_BASE_URL}/synthesize", json=payload)
        assert response.status_code == 422  # Validation error

class TestMeloTTSAPIIntegration:
    """Integration tests for MeloTTS API"""
    
    def test_full_tts_workflow(self):
        """Test complete TTS workflow with valid data"""
        # First, get available speakers
        speakers_response = requests.get(f"{API_BASE_URL}/speakers")
        assert speakers_response.status_code == 200
        
        speakers_data = speakers_response.json()
        available_speakers = speakers_data["speakers"]
        
        if not available_speakers:
            pytest.skip("No speakers available for testing")
        
        # Test with first available speaker
        speaker = available_speakers[0]
        payload = {
            "text": "Hello, this is a test!",
            "speaker": speaker,
            "speed": 1.0
        }
        
        # Test streaming endpoint
        tts_response = requests.post(f"{API_BASE_URL}/tts", json=payload)
        if tts_response.status_code == 503:
            pytest.skip("Model not ready for testing")
        
        assert tts_response.status_code == 200
        assert tts_response.headers["content-type"] == "audio/wav"
        assert len(tts_response.content) > 0
        
        # Test base64 endpoint
        synthesize_response = requests.post(f"{API_BASE_URL}/synthesize", json=payload)
        assert synthesize_response.status_code == 200
        
        data = synthesize_response.json()
        assert "audio_content" in data
        assert "format" in data
        assert "speaker" in data
        assert "speed" in data
        
        # Verify base64 content can be decoded
        try:
            audio_data = base64.b64decode(data["audio_content"])
            assert len(audio_data) > 0
        except Exception as e:
            pytest.fail(f"Failed to decode base64 audio: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
