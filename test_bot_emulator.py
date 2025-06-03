#!/usr/bin/env python3
"""Test script to diagnose Bot Framework Emulator connection issues"""

import requests
import json
import uuid
from datetime import datetime

# Create a proper Bot Framework activity
activity = {
    "type": "message",
    "id": str(uuid.uuid4()),
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "localTimestamp": datetime.now().isoformat() + "Z",
    "channelId": "emulator",
    "from": {
        "id": "user1",
        "name": "User"
    },
    "conversation": {
        "id": str(uuid.uuid4())
    },
    "recipient": {
        "id": "bot",
        "name": "Bot"
    },
    "text": "Hello, how are you?",
    "textFormat": "plain",
    "locale": "en-US",
    "serviceUrl": "http://localhost:63455"
}

# Test the endpoint
url = "http://localhost:3978/api/messages"
headers = {
    "Content-Type": "application/json",
    "Authorization": ""  # Empty for local testing
}

print(f"Testing bot endpoint: {url}")
print(f"Activity: {json.dumps(activity, indent=2)}")

try:
    response = requests.post(url, json=activity, headers=headers)
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    if response.text:
        print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")