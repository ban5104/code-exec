#!/usr/bin/env python3
"""
Simple test to interact with the bot locally
"""

import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

async def test_bot():
    """Test bot directly without HTTP"""
    from src.core import ClaudeCore
    from src.ui import TeamsFormatter
    
    print("Testing bot components directly...")
    
    # Test ClaudeCore
    claude = ClaudeCore()
    formatter = TeamsFormatter()
    
    # Test simple message
    print("\n1. Testing simple message:")
    response = claude.chat("Hello, can you help me?", use_code_execution=False)
    print(f"Response: {response['assistant_message'][:100]}...")
    
    # Test help command formatting
    print("\n2. Testing help card:")
    help_card = formatter.create_help_card()
    print(f"Help card created: {help_card.content_type}")
    
    # Test code execution
    print("\n3. Testing code execution:")
    response = claude.chat("What is 2 + 2? Show me with Python code.", use_code_execution=True)
    print(f"Response: {response['assistant_message'][:100]}...")
    if response.get('executed_code'):
        print(f"Code executed: {response['executed_code']}")
        print(f"Output: {response.get('code_output', 'No output')}")
    
    # Test report card formatting
    print("\n4. Testing report card:")
    job_details = {
        'description': 'Test calculation',
        'client': 'Test User',
        'job_reference': 'TEST-001',
        'project': 'Testing',
        'by': 'Claude AI'
    }
    report_card = formatter.create_detailed_report_card(response, job_details)
    print(f"Report card created: {report_card.content_type}")

if __name__ == "__main__":
    asyncio.run(test_bot())