#!/usr/bin/env python3
"""
Azure App Service entry point for Claude Code Execution Teams Bot
"""

import os
import sys
import logging
from aiohttp import web
from aiohttp.web import Request, Response
from botbuilder.core import TurnContext
from botbuilder.schema import Activity

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import our bot components
from src.bot import adapter, bot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_messages(req: Request) -> Response:
    """Handle incoming messages from Teams"""
    if req.headers.get("Content-Type") == "application/json":
        body = await req.json()
        activity = Activity().deserialize(body)
        auth_header = req.headers.get("Authorization", "")
        
        try:
            invoke_response = await adapter.process_activity(
                activity, auth_header, bot.on_turn
            )
            if invoke_response:
                return web.json_response(
                    data=invoke_response.body,
                    status=invoke_response.status
                )
            return web.Response(status=201)
        except Exception as e:
            logger.error(f"Error: {e}")
            return web.Response(status=500)
    else:
        return web.Response(status=415)

# Health check endpoint
async def health_check(request):
    return web.Response(text="OK", status=200)

# Create the application
app = web.Application()
app.router.add_post("/api/messages", handle_messages)
app.router.add_get("/", health_check)

if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 3978))
        logger.info(f"Starting bot on port {port}")
        web.run_app(app, host="0.0.0.0", port=port)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        raise