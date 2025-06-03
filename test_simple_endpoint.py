#!/usr/bin/env python3
"""Test the simple endpoint"""

import requests
import json

# First test if bot is running
try:
    response = requests.get("http://localhost:3978/test")
    print("Bot status check:")
    print(json.dumps(response.json(), indent=2))
    print()
except Exception as e:
    print(f"❌ Bot doesn't seem to be running: {e}")
    print("Please start the bot with: python app.py")
    exit(1)

# Test the simple message endpoint
try:
    response = requests.post(
        "http://localhost:3978/api/test-message",
        json={"message": "Hello, can you help me with Python?"},
        headers={"Content-Type": "application/json"}
    )
    
    print("Test message response:")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data.get('response', 'No response')}")
        print(f"Tool used: {data.get('tool_used', False)}")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"❌ Error testing message endpoint: {e}")