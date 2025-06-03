#!/usr/bin/env python3
"""
Main entry point for the Claude Code Execution Teams Bot
This file is configured for Azure App Service deployment
"""

import os
import logging
from aiohttp import web
from aiohttp.web import Request, Response
from botbuilder.core import TurnContext
from botbuilder.schema import Activity

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use system environment variables

# Import our bot components
from src.bot.bot import adapter, bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def handle_messages(req: Request) -> Response:
    """Handle incoming messages from Teams"""
    if req.headers.get("Content-Type") == "application/json":
        body = await req.json()
        activity = Activity().deserialize(body)
        auth_header = req.headers.get("Authorization", "")
        
        try:
            logger.info(f"Received activity type: {activity.type}")
            logger.info(f"Auth header present: {bool(auth_header)}")
            logger.info(f"Activity: {activity}")
            
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
            logger.error(f"Error processing activity: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return web.Response(status=500, text=str(e))
    else:
        return web.Response(status=415, text="Unsupported Media Type")


async def health_check(req: Request) -> Response:
    """Health check endpoint for monitoring"""
    return web.json_response({
        "status": "healthy",
        "service": "Claude Code Execution Bot",
        "version": "1.0.0",
        "timestamp": str(os.popen('date').read().strip())
    })


def create_app() -> web.Application:
    """Create the aiohttp application"""
    app = web.Application()
    
    # Add routes
    app.router.add_post("/api/messages", handle_messages)
    app.router.add_get("/health", health_check)
    app.router.add_get("/", health_check)  # Root endpoint for Azure
    
    # Add a test endpoint
    async def test_endpoint(req: Request) -> Response:
        """Test endpoint to verify bot is working"""
        return web.json_response({
            "status": "Bot is running",
            "endpoints": {
                "messages": "/api/messages",
                "health": "/health"
            },
            "configuration": {
                "ANTHROPIC_API_KEY": "Set" if os.environ.get("ANTHROPIC_API_KEY") else "Not set",
                "MicrosoftAppId": "Set" if os.environ.get("MicrosoftAppId") else "Not set (OK for local)"
            }
        })
    
    app.router.add_get("/test", test_endpoint)
    
    # Add a simple message endpoint for testing
    async def test_message_endpoint(req: Request) -> Response:
        """Simple endpoint to test bot without Bot Framework auth"""
        try:
            body = await req.json()
            message = body.get('message', '')
            
            # Create a minimal claude instance and get response
            from src.core import ClaudeCore
            claude = ClaudeCore()
            
            # Get response from Claude
            response_data = claude.chat(
                user_input=message,
                use_code_execution=True,
                file_attachments_info=[]
            )
            
            return web.json_response({
                'response': response_data.get('assistant_message', 'No response'),
                'tool_used': response_data.get('tool_used', False),
                'generated_figures': response_data.get('generated_figures', [])
            })
            
        except Exception as e:
            logger.error(f"Error in test endpoint: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    app.router.add_post("/api/test-message", test_message_endpoint)
    app.router.add_options("/api/test-message", lambda req: web.Response(headers={
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }))
    
    # Add middleware for logging and CORS
    async def log_middleware(app, handler):
        async def middleware_handler(request):
            logger.info(f"{request.method} {request.path}")
            try:
                response = await handler(request)
                logger.info(f"Response: {response.status}")
                # Add CORS headers for local testing
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
                return response
            except Exception as e:
                logger.error(f"Request failed: {str(e)}")
                raise
        return middleware_handler
    
    app.middlewares.append(log_middleware)
    
    return app


if __name__ == "__main__":
    # Get port from environment or default to 3978
    PORT = int(os.environ.get("PORT", 3978))
    
    # Create and run the application
    app = create_app()
    
    logger.info(f"Starting bot server on port {PORT}")
    logger.info("Bot endpoint: /api/messages")
    logger.info("Health check: /health")
    
    # Check required environment variables
    required_vars = ["ANTHROPIC_API_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
        logger.warning("Bot may not function properly without these variables")
    
    # Run the app
    web.run_app(
        app, 
        host="0.0.0.0", 
        port=PORT,
        access_log=logger
    )