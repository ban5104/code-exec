#!/usr/bin/env python3
"""
Working bot for Bot Framework Emulator
Based on official Bot Framework Python SDK patterns
"""

import os
import logging
from aiohttp import web
from aiohttp.web import Request, Response
from botbuilder.core import (
    TurnContext, 
    MessageFactory, 
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    MemoryStorage,
    ConversationState,
    UserState
)
from botbuilder.schema import Activity, ActivityTypes

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot logic
class EchoBot:
    def __init__(self, conversation_state: ConversationState, user_state: UserState):
        self.conversation_state = conversation_state
        self.user_state = user_state

    async def on_message_activity(self, turn_context: TurnContext) -> None:
        """Handle message activities"""
        text = turn_context.activity.text
        
        # Simple echo or Claude integration
        if "claude" in text.lower():
            try:
                from src.core import ClaudeCore
                claude = ClaudeCore()
                result = claude.chat(text, use_code_execution=True)
                response = result.get('assistant_message', 'No response from Claude')
            except Exception as e:
                response = f"Error calling Claude: {str(e)}"
        else:
            response = f"Echo: {text}"
        
        await turn_context.send_activity(MessageFactory.text(response))

    async def on_members_added_activity(self, members_added, turn_context: TurnContext) -> None:
        """Welcome new members"""
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(MessageFactory.text("Hello! I'm the Bot Framework test bot."))

    async def on_turn(self, turn_context: TurnContext) -> None:
        """Handle bot turn"""
        if turn_context.activity.type == ActivityTypes.message:
            await self.on_message_activity(turn_context)
        elif turn_context.activity.type == ActivityTypes.members_added:
            await self.on_members_added_activity(
                turn_context.activity.members_added, turn_context
            )

        # Save state
        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)


# Create adapter and bot
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

# Create adapter with proper settings
SETTINGS = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Create storage and state
MEMORY_STORAGE = MemoryStorage()
CONVERSATION_STATE = ConversationState(MEMORY_STORAGE)
USER_STATE = UserState(MEMORY_STORAGE)

# Create the bot
BOT = EchoBot(CONVERSATION_STATE, USER_STATE)

# Error handler
async def on_error(context: TurnContext, error: Exception):
    logger.error(f"Error: {error}")
    try:
        await context.send_activity(MessageFactory.text("Sorry, an error occurred."))
    except:
        pass

ADAPTER.on_turn_error = on_error


# Main messaging endpoint
async def messages(req: Request) -> Response:
    if "application/json" in req.headers.get("Content-Type", ""):
        body = await req.json()
        activity = Activity().deserialize(body)
        auth_header = req.headers.get("Authorization", "")
        
        try:
            response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
            if response:
                return web.json_response(response.body, status=response.status)
            return web.Response(status=201)
        except Exception as e:
            logger.error(f"Error: {e}")
            return web.Response(status=500, text=str(e))
    else:
        return web.Response(status=415)


# Create application
APP = web.Application()
APP.router.add_post("/api/messages", messages)

# Health check
async def health(req: Request) -> Response:
    return web.json_response({"status": "ok", "bot": "emulator_bot"})

APP.router.add_get("/health", health)


if __name__ == "__main__":
    PORT = 3981
    logger.info(f"Starting bot on port {PORT}")
    logger.info(f"Bot URL: http://localhost:{PORT}/api/messages")
    logger.info("For Bot Framework Emulator:")
    logger.info("- Leave Microsoft App ID and Password empty")
    logger.info("- Use the URL above to connect")
    
    web.run_app(APP, host="0.0.0.0", port=PORT)