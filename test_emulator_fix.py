#!/usr/bin/env python3
"""Test script to verify bot endpoint with proper emulator format"""

import requests
import json
import uuid
from datetime import datetime

# Create a proper conversationUpdate activity (what emulator sends first)
conversation_update = {
    "type": "conversationUpdate",
    "id": str(uuid.uuid4()),
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "channelId": "emulator",
    "from": {
        "id": "http://localhost:63455",
        "name": "Bot Framework Emulator",
        "role": "user"
    },
    "conversation": {
        "id": str(uuid.uuid4())
    },
    "recipient": {
        "id": "bot",
        "name": "Bot",
        "role": "bot"
    },
    "membersAdded": [
        {
            "id": "user1",
            "name": "User"
        },
        {
            "id": "bot",
            "name": "Bot"
        }
    ],
    "serviceUrl": "http://localhost:63455"
}

# Test the endpoint
url = "http://localhost:3978/api/messages"
headers = {
    "Content-Type": "application/json"
}

print("Testing conversationUpdate activity...")
print(f"URL: {url}")

try:
    response = requests.post(url, json=conversation_update, headers=headers)
    print(f"\nResponse Status: {response.status_code}")
    if response.text:
        print(f"Response Body: {response.text}")
    
    if response.status_code in [200, 201, 202]:
        print("\n✅ ConversationUpdate handled successfully!")
        
        # Now test a message
        message_activity = {
            "type": "message",
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "channelId": "emulator",
            "from": {
                "id": "user1",
                "name": "User",
                "role": "user"
            },
            "conversation": {
                "id": conversation_update["conversation"]["id"]
            },
            "recipient": {
                "id": "bot",
                "name": "Bot",
                "role": "bot"
            },
            "text": "Hello, how are you?",
            "textFormat": "plain",
            "locale": "en-US",
            "serviceUrl": "http://localhost:63455"
        }
        
        print("\nTesting message activity...")
        msg_response = requests.post(url, json=message_activity, headers=headers)
        print(f"Message Response Status: {msg_response.status_code}")
        if msg_response.text:
            print(f"Message Response Body: {msg_response.text}")
            
except Exception as e:
    print(f"Error: {e}")