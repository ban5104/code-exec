#!/usr/bin/env python3
"""
Debug bot to diagnose Bot Framework Emulator issues
"""

import os
import json
import logging
from aiohttp import web
from aiohttp.web import Request, Response

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the main messaging endpoint handler
async def messages(req: Request) -> Response:
    logger.info(f"Received request: {req.method} {req.path}")
    logger.info(f"Headers: {dict(req.headers)}")
    
    try:
        body = await req.json()
        logger.info(f"Body: {json.dumps(body, indent=2)}")
        
        # Extract activity type
        activity_type = body.get('type', 'unknown')
        logger.info(f"Activity type: {activity_type}")
        
        # Simple response based on activity type
        if activity_type == 'conversationUpdate':
            # Just acknowledge conversation updates
            return web.Response(status=200)
        
        elif activity_type == 'message':
            # Echo the message back
            text = body.get('text', '')
            logger.info(f"Message text: {text}")
            
            # Create a simple response activity
            response_activity = {
                "type": "message",
                "text": f"Echo: {text}",
                "from": body.get('recipient', {}),
                "recipient": body.get('from', {}),
                "conversation": body.get('conversation', {}),
                "replyToId": body.get('id')
            }
            
            # Try to send response back to emulator
            service_url = body.get('serviceUrl', '')
            if service_url:
                logger.info(f"Service URL: {service_url}")
                # In a real bot, we'd POST this back to the service URL
                # For now, just log it
                logger.info(f"Would send response: {json.dumps(response_activity, indent=2)}")
            
            return web.Response(status=200)
        
        else:
            logger.info(f"Unknown activity type: {activity_type}")
            return web.Response(status=200)
            
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return web.Response(status=500, text=str(e))

# Create the application
app = web.Application()
app.router.add_post("/api/messages", messages)

# Add OPTIONS handler for CORS
async def options_handler(req: Request) -> Response:
    return web.Response(status=200, headers={
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    })

app.router.add_options("/api/messages", options_handler)

# Health check endpoint
async def health(req: Request) -> Response:
    return web.json_response({"status": "ok", "message": "Debug bot is running"})

app.router.add_get("/health", health)
app.router.add_get("/", health)

if __name__ == "__main__":
    try:
        PORT = 3980  # Yet another port
        logger.info(f"Starting debug bot on port {PORT}")
        logger.info(f"Connect with Bot Framework Emulator to http://localhost:{PORT}/api/messages")
        logger.info("This bot will log all incoming requests for debugging")
        web.run_app(app, host="0.0.0.0", port=PORT)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise