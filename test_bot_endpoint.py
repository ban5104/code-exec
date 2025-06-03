#!/usr/bin/env python3
"""
Test script to verify bot endpoint is working
"""

import requests
import json
from datetime import datetime

# Bot endpoint
BOT_URL = "http://localhost:3978"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BOT_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_message_endpoint():
    """Test message endpoint with Bot Framework format"""
    print("\nTesting message endpoint...")
    
    # Create a Bot Framework activity
    activity = {
        "type": "message",
        "id": "test-message-1",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "channelId": "emulator",
        "from": {
            "id": "user1",
            "name": "Test User"
        },
        "conversation": {
            "id": "conversation1"
        },
        "recipient": {
            "id": "bot1",
            "name": "Claude Bot"
        },
        "text": "/help",
        "serviceUrl": "http://localhost:3978"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BOT_URL}/api/messages", 
            json=activity, 
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200] if response.text else 'No response body'}")
        return response.status_code in [200, 201, 202]
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run tests"""
    print("Bot Endpoint Tests")
    print("==================")
    
    # Test health
    health_ok = test_health()
    
    # Test message endpoint
    message_ok = test_message_endpoint()
    
    print("\nSummary:")
    print(f"Health endpoint: {'✓ PASS' if health_ok else '✗ FAIL'}")
    print(f"Message endpoint: {'✓ PASS' if message_ok else '✗ FAIL'}")
    
    if not health_ok or not message_ok:
        print("\n⚠️  Bot may not be running or configured properly")
        print("Make sure the bot is running with: python app.py")

if __name__ == "__main__":
    main()