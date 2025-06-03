#!/usr/bin/env python3
"""
Simplified bot for testing with Bot Framework Emulator
"""

import os
import logging
from aiohttp import web
from aiohttp.web import Request, Response
from botbuilder.core import (
    TurnContext, 
    MessageFactory, 
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings
)
from botbuilder.schema import Activity

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create adapter with empty credentials for local testing
settings = BotFrameworkAdapterSettings("", "")
adapter = BotFrameworkAdapter(settings)

# Define the main bot logic
async def on_message_activity(turn_context: TurnContext):
    """Handle messages"""
    # Get the user's message
    user_message = turn_context.activity.text
    
    # Simple echo for testing
    response = f"Echo: {user_message}"
    
    # For testing Claude integration
    if "claude" in user_message.lower():
        try:
            from src.core import ClaudeCore
            claude = ClaudeCore()
            result = claude.chat(user_message, use_code_execution=True)
            response = result.get('assistant_message', 'No response from Claude')
        except Exception as e:
            response = f"Error calling Claude: {str(e)}"
    
    await turn_context.send_activity(MessageFactory.text(response))

# Error handler
async def on_error(context: TurnContext, error: Exception):
    logger.error(f"Error: {error}")
    await context.send_activity(MessageFactory.text("Sorry, an error occurred."))

adapter.on_turn_error = on_error

# Define the main messaging endpoint handler
async def messages(req: Request) -> Response:
    if "application/json" in req.headers.get("Content-Type", ""):
        body = await req.json()
        activity = Activity().deserialize(body)
        auth_header = req.headers.get("Authorization", "")
        
        response = await adapter.process_activity(activity, auth_header, on_message_activity)
        
        if response:
            return web.json_response(response.body, status=response.status)
        return web.Response(status=201)
    else:
        return web.Response(status=415)

# Create the application
app = web.Application()
app.router.add_post("/api/messages", messages)

# Health check endpoint
async def health(req: Request) -> Response:
    return web.json_response({"status": "ok"})

app.router.add_get("/health", health)

if __name__ == "__main__":
    try:
        PORT = 3979  # Different port to avoid conflict
        logger.info(f"Starting simple bot on port {PORT}")
        logger.info("Connect with Bot Framework Emulator to http://localhost:3979/api/messages")
        logger.info("Leave App ID and Password empty for local testing")
        web.run_app(app, host="0.0.0.0", port=PORT)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise