#!/usr/bin/env python3
"""
MeloTTS API Test Script

This script tests the MeloTTS API endpoints to ensure they're working correctly.
"""

import requests
import json
import base64
import time
import sys
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8080"
TEST_TEXT = "Hello, this is a test of the MeloTTS API. How does it sound?"
TEST_SPEAKERS = ["EN-US", "EN-AU", "JP"]
TEST_SPEEDS = [0.8, 1.0, 1.2]

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health check passed: {data}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_speakers():
    """Test the speakers endpoint"""
    print("\n🔍 Testing speakers endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/speakers", timeout=10)
        response.raise_for_status()
        data = response.json()
        speakers = data.get("speakers", [])
        print(f"✅ Found {len(speakers)} speakers: {speakers}")
        return speakers
    except Exception as e:
        print(f"❌ Speakers check failed: {e}")
        return []

def test_tts_streaming(speaker, speed=1.0):
    """Test the streaming TTS endpoint"""
    print(f"\n🔍 Testing TTS streaming (speaker: {speaker}, speed: {speed})...")
    try:
        payload = {
            "text": TEST_TEXT,
            "speaker": speaker,
            "speed": speed
        }
        
        response = requests.post(
            f"{API_BASE_URL}/tts",
            json=payload,
            timeout=30,
            stream=True
        )
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if 'audio/wav' not in content_type:
            print(f"⚠️  Unexpected content type: {content_type}")
        
        # Save audio file for verification
        output_file = f"test_output_{speaker}_{speed}.wav"
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = Path(output_file).stat().st_size
        print(f"✅ TTS streaming successful - saved {file_size} bytes to {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ TTS streaming failed: {e}")
        return False

def test_tts_base64(speaker, speed=1.0):
    """Test the base64 TTS endpoint"""
    print(f"\n🔍 Testing TTS base64 (speaker: {speaker}, speed: {speed})...")
    try:
        payload = {
            "text": TEST_TEXT,
            "speaker": speaker,
            "speed": speed
        }
        
        response = requests.post(
            f"{API_BASE_URL}/synthesize",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        audio_content = data.get("audio_content")
        
        if not audio_content:
            print("❌ No audio content in response")
            return False
        
        # Decode and save audio
        try:
            audio_data = base64.b64decode(audio_content)
            output_file = f"test_output_{speaker}_{speed}.mp3"
            with open(output_file, 'wb') as f:
                f.write(audio_data)
            
            file_size = len(audio_data)
            print(f"✅ TTS base64 successful - saved {file_size} bytes to {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to decode base64 audio: {e}")
            return False
        
    except Exception as e:
        print(f"❌ TTS base64 failed: {e}")
        return False

def test_invalid_speaker():
    """Test with an invalid speaker"""
    print("\n🔍 Testing invalid speaker...")
    try:
        payload = {
            "text": TEST_TEXT,
            "speaker": "INVALID-SPEAKER",
            "speed": 1.0
        }
        
        response = requests.post(
            f"{API_BASE_URL}/tts",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ Invalid speaker correctly rejected")
            return True
        else:
            print(f"❌ Expected 400 error, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Invalid speaker test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 MeloTTS API Test Suite")
    print("=" * 50)
    
    # Test basic connectivity
    if not test_health():
        print("\n❌ API is not responding. Make sure the server is running.")
        sys.exit(1)
    
    # Get available speakers
    speakers = test_speakers()
    if not speakers:
        print("\n❌ No speakers available. Check model loading.")
        sys.exit(1)
    
    # Test with available speakers
    test_speakers_to_use = [s for s in TEST_SPEAKERS if s in speakers]
    if not test_speakers_to_use:
        test_speakers_to_use = speakers[:2]  # Use first 2 available speakers
    
    print(f"\n🎯 Testing with speakers: {test_speakers_to_use}")
    
    # Run tests
    passed_tests = 0
    total_tests = 0
    
    # Test streaming TTS
    for speaker in test_speakers_to_use:
        for speed in TEST_SPEEDS:
            total_tests += 1
            if test_tts_streaming(speaker, speed):
                passed_tests += 1
    
    # Test base64 TTS
    for speaker in test_speakers_to_use:
        for speed in TEST_SPEEDS:
            total_tests += 1
            if test_tts_base64(speaker, speed):
                passed_tests += 1
    
    # Test error handling
    total_tests += 1
    if test_invalid_speaker():
        passed_tests += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! API is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
