#!/usr/bin/env python3
"""
Test bot startup and configuration
"""

import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print("Testing bot startup...")
print("=" * 50)

# Check environment variables
print("\n1. Environment Variables:")
api_key = os.getenv('ANTHROPIC_API_KEY')
app_id = os.getenv('MicrosoftAppId')
app_pass = os.getenv('MicrosoftAppPassword')

print(f"   ANTHROPIC_API_KEY: {'✓ Set' if api_key else '✗ Not set'} ({len(api_key) if api_key else 0} chars)")
print(f"   MicrosoftAppId: {'✓ Set' if app_id else '✗ Not set'}")
print(f"   MicrosoftAppPassword: {'✓ Set' if app_pass else '✗ Not set'}")

# Test imports
print("\n2. Testing imports:")
try:
    from src.core import ClaudeCore
    print("   ✓ ClaudeCore imported")
except Exception as e:
    print(f"   ✗ ClaudeCore import failed: {e}")

try:
    from src.bot import CodeExecutionBot
    print("   ✓ CodeExecutionBot imported")
except Exception as e:
    print(f"   ✗ CodeExecutionBot import failed: {e}")

try:
    from src.ui import TeamsFormatter
    print("   ✓ TeamsFormatter imported")
except Exception as e:
    print(f"   ✗ TeamsFormatter import failed: {e}")

# Test ClaudeCore initialization
print("\n3. Testing ClaudeCore initialization:")
try:
    claude = ClaudeCore()
    print("   ✓ ClaudeCore initialized successfully")
except Exception as e:
    print(f"   ✗ ClaudeCore initialization failed: {e}")

# Test bot creation
print("\n4. Testing bot creation:")
try:
    from src.bot.bot import create_app
    adapter, bot = create_app()
    print("   ✓ Bot created successfully")
except Exception as e:
    print(f"   ✗ Bot creation failed: {e}")

print("\n" + "=" * 50)
print("Startup test complete!")