#!/usr/bin/env python3
"""
Microsoft Teams Bot implementation for Claude Code Execution Assistant
This module handles Teams events, file downloads, and orchestrates calls to claude_core
"""

import os
import logging
import aiohttp
from typing import Dict, List, Any, Optional
from botbuilder.core import (
    TurnContext, 
    MessageFactory, 
    CardFactory,
    ActivityHandler,
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings
)
from botbuilder.schema import (
    Activity,
    ChannelAccount,
    ConversationParameters,
    Attachment,
    AttachmentData
)
from botbuilder.core.conversation_state import ConversationState
from botbuilder.core.user_state import UserState
from botbuilder.azure import CosmosDbPartitionedStorage
from botframework.connector.auth import MicrosoftAppCredentials

# Import our core logic
from ..core import ClaudeCore
from ..ui import TeamsFormatter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeExecutionBot(ActivityHandler):
    """Bot that handles Claude code execution in Teams"""
    
    def __init__(self, conversation_state: ConversationState, user_state: UserState):
        """Initialize the bot with conversation and user state"""
        self.conversation_state = conversation_state
        self.user_state = user_state
        
        # Initialize Claude core
        self.claude_core = ClaudeCore()
        
        # Initialize Teams formatter
        self.formatter = TeamsFormatter()
        
        # Track conversation contexts
        self.conversation_contexts = {}
    
    async def on_message_activity(self, turn_context: TurnContext) -> None:
        """Handle incoming messages from Teams"""
        try:
            # Get conversation ID for context tracking
            conversation_id = turn_context.activity.conversation.id
            
            # Get or create conversation context
            if conversation_id not in self.conversation_contexts:
                self.conversation_contexts[conversation_id] = {
                    'claude_instance': ClaudeCore(),
                    'pending_files': []
                }
            
            context = self.conversation_contexts[conversation_id]
            claude = context['claude_instance']
            
            # Extract message text
            user_message = turn_context.activity.text or ""
            
            # Check for file attachments
            file_attachments = []
            if hasattr(turn_context.activity, 'attachments') and turn_context.activity.attachments:
                # Send typing indicator while processing files
                await self._send_typing_indicator(turn_context)
                
                # Process attachments
                for attachment in turn_context.activity.attachments:
                    if attachment.content_type and not attachment.content_type.startswith('image/'):
                        # Download and upload non-image files to Anthropic
                        file_info = await self._process_attachment(turn_context, attachment, claude)
                        if file_info:
                            file_attachments.append(file_info)
            
            # Determine if code execution should be enabled
            use_code_execution = not user_message.lower().startswith('/nocode')
            if user_message.lower().startswith('/nocode'):
                user_message = user_message[7:].strip()
            
            # Handle special commands
            if user_message.lower() == '/reset':
                claude.reset_conversation()
                await turn_context.send_activity(MessageFactory.text("✅ Conversation history cleared."))
                return
            
            elif user_message.lower() == '/files':
                files = claude.list_files()
                if files:
                    card = self.formatter.create_files_list_card(files)
                    await turn_context.send_activity(MessageFactory.attachment(card))
                else:
                    await turn_context.send_activity(MessageFactory.text("📁 No files uploaded yet."))
                return
            
            elif user_message.lower() == '/help':
                help_card = self.formatter.create_help_card()
                await turn_context.send_activity(MessageFactory.attachment(help_card))
                return
            
            # Send typing indicator while processing with Claude
            await self._send_typing_indicator(turn_context)
            
            # Get response from Claude
            response_data = claude.chat(
                user_input=user_message,
                use_code_execution=use_code_execution,
                file_attachments_info=file_attachments
            )
            
            # Format and send response
            await self._send_formatted_response(turn_context, response_data, user_message)
            
        except Exception as e:
            logger.error(f"Error in on_message_activity: {str(e)}")
            error_message = f"❌ An error occurred: {str(e)}"
            await turn_context.send_activity(MessageFactory.text(error_message))
    
    async def _send_typing_indicator(self, turn_context: TurnContext) -> None:
        """Send typing indicator to show bot is processing"""
        typing_activity = MessageFactory.text("")
        typing_activity.type = "typing"
        await turn_context.send_activity(typing_activity)
    
    async def _process_attachment(self, turn_context: TurnContext, attachment: Attachment, 
                                  claude: ClaudeCore) -> Optional[Dict[str, str]]:
        """Download attachment from Teams and upload to Anthropic"""
        try:
            # Get the attachment data
            connector = turn_context.adapter.create_connector_client(
                turn_context.activity.service_url
            )
            
            # Download attachment
            attachment_data = await connector.attachments.get_attachment_info(
                attachment.name
            )
            
            # Download file content
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.content_url) as response:
                    if response.status == 200:
                        file_content = await response.read()
                        
                        # Save temporarily
                        temp_path = f"/tmp/{attachment.name}"
                        with open(temp_path, 'wb') as f:
                            f.write(file_content)
                        
                        # Upload to Anthropic
                        file_id = claude.upload_file(temp_path)
                        
                        # Clean up temp file
                        os.remove(temp_path)
                        
                        if file_id:
                            return {
                                'file_id': file_id,
                                'file_name': attachment.name
                            }
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing attachment: {str(e)}")
            return None
    
    async def _send_formatted_response(self, turn_context: TurnContext, 
                                       response_data: Dict[str, Any], 
                                       user_query: str) -> None:
        """Send formatted response based on the type of output"""
        
        # Check if this is a simple text response
        if (not response_data.get('tool_used') and 
            not response_data.get('web_searches') and 
            not response_data.get('generated_figures')):
            # Simple text response
            await turn_context.send_activity(
                MessageFactory.text(response_data['assistant_message'])
            )
        else:
            # Create job details for report
            job_details = {
                'description': user_query[:100] + "..." if len(user_query) > 100 else user_query,
                'client': turn_context.activity.from_property.name or "Teams User",
                'job_reference': f"TEAMS-{turn_context.activity.id[:8]}",
                'project': "Code Execution Assistant",
                'by': "Claude AI Assistant"
            }
            
            # Create detailed report card
            report_card = self.formatter.create_detailed_report_card(
                response_data, 
                job_details
            )
            
            # Send the card
            await turn_context.send_activity(MessageFactory.attachment(report_card))
            
            # If there are generated figures, we might need to handle them separately
            # depending on Teams' capabilities
            if response_data.get('generated_figures'):
                for figure in response_data['generated_figures']:
                    # In a real implementation, you'd upload these to a accessible location
                    # and include URLs in the card
                    logger.info(f"Generated figure: {figure['figure_name']}")
    
    async def on_members_added_activity(self, members_added: List[ChannelAccount], 
                                        turn_context: TurnContext) -> None:
        """Welcome new members"""
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                welcome_card = self.formatter.create_welcome_card()
                await turn_context.send_activity(MessageFactory.attachment(welcome_card))
    
    async def on_turn(self, turn_context: TurnContext) -> None:
        """Handle bot turn - save state after each turn"""
        await super().on_turn(turn_context)
        
        # Save any state changes
        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)


def create_app():
    """Create and configure the bot application"""
    # Load configuration
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    
    # Create adapter settings - empty strings for local development
    logger.info(f"App ID: {'Set' if APP_ID else 'Not set (local mode)'}")
    logger.info(f"App Password: {'Set' if APP_PASSWORD else 'Not set (local mode)'}")
    
    settings = BotFrameworkAdapterSettings(
        app_id=APP_ID,
        app_password=APP_PASSWORD
    )
    
    # Create the Bot Framework Adapter
    adapter = BotFrameworkAdapter(settings)
    
    # Create storage for state management
    # In production, use CosmosDB or other persistent storage
    from botbuilder.core import MemoryStorage
    memory_storage = MemoryStorage()  # Use proper MemoryStorage implementation
    
    # Create the conversation state
    conversation_state = ConversationState(memory_storage)
    user_state = UserState(memory_storage)
    
    # Create the bot
    bot = CodeExecutionBot(conversation_state, user_state)
    
    # Error handler
    async def on_error(context: TurnContext, error: Exception):
        logger.error(f"Error: {error}")
        logger.error(f"Error type: {type(error).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Don't try to send error messages if it's a connection error
        if "ConnectionError" not in str(type(error).__name__):
            try:
                await context.send_activity(
                    MessageFactory.text("❌ Sorry, an error occurred. Please try again.")
                )
            except:
                pass
    
    adapter.on_turn_error = on_error
    
    return adapter, bot


# For Azure Functions or other hosting
adapter, bot = create_app()


async def messages(req):
    """Handle incoming messages - Azure Functions entry point"""
    if "application/json" in req.headers.get("Content-Type", ""):
        body = await req.json()
    else:
        return {"status": 415}
    
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")
    
    try:
        response = await adapter.process_activity(activity, auth_header, bot.on_turn)
        if response:
            return {"status": response.status, "body": response.body}
        return {"status": 201}
    except Exception as e:
        logger.error(f"Error processing activity: {e}")
        return {"status": 500}


# For local development with aiohttp
if __name__ == "__main__":
    from aiohttp import web
    from aiohttp.web import Request, Response
    
    async def handle_messages(req: Request) -> Response:
        """Handle incoming messages for aiohttp"""
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
    
    # Create the application
    app = web.Application()
    app.router.add_post("/api/messages", handle_messages)
    
    # Start the server
    try:
        web.run_app(app, host="0.0.0.0", port=3978)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        raise