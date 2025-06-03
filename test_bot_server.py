#!/usr/bin/env python3
"""
Test the bot server with proper Bot Framework messages
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime

BOT_URL = "http://localhost:3978"

async def send_bot_message(text):
    """Send a message to the bot in Bot Framework format"""
    activity = {
        "type": "message",
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "channelId": "emulator",
        "from": {
            "id": "user1",
            "name": "Test User"
        },
        "conversation": {
            "id": "conv1"
        },
        "recipient": {
            "id": "bot1",
            "name": "Claude Bot"
        },
        "text": text,
        "serviceUrl": BOT_URL,
        "channelData": {
            "clientActivityID": str(uuid.uuid4())
        }
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{BOT_URL}/api/messages",
                json=activity,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"\nSent: {text}")
                print(f"Status: {response.status}")
                
                # Bot Framework typically returns 201 for success
                if response.status in [200, 201, 202]:
                    print("✓ Message accepted")
                    
                    # The bot might send activities back through serviceUrl
                    # In emulator mode, we'd need to set up an endpoint to receive them
                    print("Note: Bot responses would be sent to serviceUrl in real Teams/Emulator")
                else:
                    text = await response.text()
                    print(f"✗ Error: {text}")
                    
        except aiohttp.ClientError as e:
            print(f"✗ Connection error: {e}")
            return False
    
    return True

async def test_health():
    """Test health endpoint"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BOT_URL}/health") as response:
                print("Health check:")
                print(f"Status: {response.status}")
                data = await response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                return response.status == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False

async def main():
    """Run bot tests"""
    print("Bot Server Tests")
    print("=" * 50)
    
    # Check health
    print("\n1. Testing health endpoint...")
    health_ok = await test_health()
    if not health_ok:
        print("\n⚠️  Bot server not running! Start it with: python app.py")
        return
    
    # Test messages
    print("\n2. Testing message handling...")
    
    # Test various messages
    test_messages = [
        "/help",
        "Hello Claude!",
        "What is 2 + 2?",
        "/nocode Explain Python decorators",
        "/reset",
        "/files"
    ]
    
    for msg in test_messages:
        await send_bot_message(msg)
        await asyncio.sleep(1)  # Give bot time to process
    
    print("\n" + "=" * 50)
    print("Tests complete!")
    print("\nNote: To see bot responses, use Bot Framework Emulator at:")
    print(f"  URL: {BOT_URL}/api/messages")
    print("  Leave App ID and Password empty for local testing")

if __name__ == "__main__":
    asyncio.run(main())