#!/usr/bin/env python3
"""
Test suite for Microsoft Teams bot implementation
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import os
import sys
# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from botbuilder.core import TurnContext, MessageFactory
from botbuilder.schema import Activity, ChannelAccount, ConversationAccount
from src.bot import CodeExecutionBot
from src.ui import TeamsFormatter


class TestCodeExecutionBot(unittest.TestCase):
    """Test cases for CodeExecutionBot"""
    
    def setUp(self):
        """Set up test environment"""
        self.conversation_state = Mock()
        self.user_state = Mock()
        self.bot = CodeExecutionBot(self.conversation_state, self.user_state)
    
    def create_mock_turn_context(self, text="", attachments=None):
        """Create a mock turn context for testing"""
        activity = Activity(
            type="message",
            text=text,
            from_property=ChannelAccount(id="user123", name="Test User"),
            conversation=ConversationAccount(id="conv123"),
            recipient=ChannelAccount(id="bot123"),
            id="msg123",
            service_url="https://test.service.url",
            attachments=attachments or []
        )
        
        turn_context = Mock(spec=TurnContext)
        turn_context.activity = activity
        turn_context.send_activity = AsyncMock()
        turn_context.adapter = Mock()
        turn_context.adapter.create_connector_client = Mock()
        
        return turn_context
    
    @patch('bot.ClaudeCore')
    async def test_simple_message(self, mock_claude_class):
        """Test handling a simple message"""
        # Setup mock
        mock_claude = Mock()
        mock_claude.chat.return_value = {
            "assistant_message": "Hello! I can help you with that.",
            "tool_used": None,
            "executed_code": None,
            "code_output": None,
            "generated_figures": [],
            "code_errors": None,
            "web_searches": [],
            "files_accessed": []
        }
        mock_claude_class.return_value = mock_claude
        
        # Create context
        turn_context = self.create_mock_turn_context("Hello Claude")
        
        # Test
        await self.bot.on_message_activity(turn_context)
        
        # Verify
        turn_context.send_activity.assert_called()
        sent_activity = turn_context.send_activity.call_args[0][0]
        self.assertIn("Hello! I can help you with that.", sent_activity.text)
    
    async def test_help_command(self):
        """Test /help command"""
        turn_context = self.create_mock_turn_context("/help")
        
        await self.bot.on_message_activity(turn_context)
        
        turn_context.send_activity.assert_called()
        sent_activity = turn_context.send_activity.call_args[0][0]
        self.assertIsNotNone(sent_activity.attachments)
        self.assertEqual(len(sent_activity.attachments), 1)
    
    async def test_reset_command(self):
        """Test /reset command"""
        turn_context = self.create_mock_turn_context("/reset")
        
        # Add conversation to context
        self.bot.conversation_contexts['conv123'] = {
            'claude_instance': Mock(),
            'pending_files': []
        }
        
        await self.bot.on_message_activity(turn_context)
        
        # Verify reset was called
        self.bot.conversation_contexts['conv123']['claude_instance'].reset_conversation.assert_called_once()
        
        # Verify response
        turn_context.send_activity.assert_called()
        sent_activity = turn_context.send_activity.call_args[0][0]
        self.assertIn("Conversation history cleared", sent_activity.text)
    
    async def test_files_command_empty(self):
        """Test /files command with no files"""
        turn_context = self.create_mock_turn_context("/files")
        
        # Setup claude instance
        self.bot.conversation_contexts['conv123'] = {
            'claude_instance': Mock(list_files=Mock(return_value=[])),
            'pending_files': []
        }
        
        await self.bot.on_message_activity(turn_context)
        
        turn_context.send_activity.assert_called()
        sent_activity = turn_context.send_activity.call_args[0][0]
        self.assertIn("No files uploaded yet", sent_activity.text)
    
    async def test_nocode_prefix(self):
        """Test /nocode prefix disables code execution"""
        turn_context = self.create_mock_turn_context("/nocode analyze this data")
        
        # Setup mock claude
        mock_claude = Mock()
        mock_claude.chat.return_value = {
            "assistant_message": "Analysis complete",
            "tool_used": None,
            "executed_code": None,
            "code_output": None,
            "generated_figures": [],
            "code_errors": None,
            "web_searches": [],
            "files_accessed": []
        }
        
        self.bot.conversation_contexts['conv123'] = {
            'claude_instance': mock_claude,
            'pending_files': []
        }
        
        await self.bot.on_message_activity(turn_context)
        
        # Verify claude.chat was called with use_code_execution=False
        mock_claude.chat.assert_called_once()
        call_args = mock_claude.chat.call_args
        self.assertEqual(call_args[1]['user_input'], "analyze this data")
        self.assertFalse(call_args[1]['use_code_execution'])
    
    async def test_typing_indicator(self):
        """Test typing indicator is sent"""
        turn_context = self.create_mock_turn_context("Hello")
        
        await self.bot._send_typing_indicator(turn_context)
        
        turn_context.send_activity.assert_called()
        sent_activity = turn_context.send_activity.call_args[0][0]
        self.assertEqual(sent_activity.type, "typing")
    
    async def test_members_added(self):
        """Test welcome message for new members"""
        turn_context = self.create_mock_turn_context()
        
        # New member (not the bot)
        new_member = ChannelAccount(id="newuser123", name="New User")
        
        await self.bot.on_members_added_activity([new_member], turn_context)
        
        turn_context.send_activity.assert_called()
        sent_activity = turn_context.send_activity.call_args[0][0]
        self.assertIsNotNone(sent_activity.attachments)


class TestTeamsFormatter(unittest.TestCase):
    """Test cases for TeamsFormatter"""
    
    def setUp(self):
        """Set up test environment"""
        self.formatter = TeamsFormatter()
    
    def test_create_simple_text_card(self):
        """Test creating a simple text card"""
        text = "This is a simple message"
        attachment = self.formatter.create_simple_text_card(text)
        
        self.assertIsNotNone(attachment)
        self.assertEqual(attachment.content_type, "application/vnd.microsoft.card.adaptive")
        
        # Check card content
        card = attachment.content
        self.assertEqual(card['type'], "AdaptiveCard")
        self.assertEqual(card['body'][0]['text'], text)
    
    def test_create_help_card(self):
        """Test creating help card"""
        attachment = self.formatter.create_help_card()
        
        self.assertIsNotNone(attachment)
        card = attachment.content
        
        # Check structure
        self.assertEqual(card['type'], "AdaptiveCard")
        self.assertTrue(len(card['body']) > 0)
        self.assertIn("Help", card['body'][0]['text'])
        
        # Check for actions
        self.assertIn('actions', card)
        self.assertTrue(len(card['actions']) > 0)
    
    def test_create_welcome_card(self):
        """Test creating welcome card"""
        attachment = self.formatter.create_welcome_card()
        
        self.assertIsNotNone(attachment)
        card = attachment.content
        
        # Check structure
        self.assertEqual(card['type'], "AdaptiveCard")
        self.assertIn("Welcome", card['body'][0]['text'])
    
    def test_create_error_card(self):
        """Test creating error card"""
        error_msg = "Something went wrong"
        attachment = self.formatter.create_error_card(error_msg)
        
        self.assertIsNotNone(attachment)
        card = attachment.content
        
        # Check error styling
        self.assertEqual(card['body'][0]['style'], "attention")
        # Check error message is included
        card_text = str(card)
        self.assertIn(error_msg, card_text)
    
    def test_create_files_list_card(self):
        """Test creating files list card"""
        files = [
            {
                'file_name': 'test.pdf',
                'file_type': 'PDF Document',
                'file_id': 'file123'
            },
            {
                'file_name': 'data.csv',
                'file_type': 'CSV Data',
                'file_id': 'file456'
            }
        ]
        
        attachment = self.formatter.create_files_list_card(files)
        
        self.assertIsNotNone(attachment)
        card = attachment.content
        
        # Check title
        self.assertIn("Uploaded Files", card['body'][0]['text'])
        
        # Check files are listed
        card_text = str(card)
        self.assertIn('test.pdf', card_text)
        self.assertIn('data.csv', card_text)
    
    def test_create_detailed_report_card(self):
        """Test creating detailed report card"""
        response_data = {
            "assistant_message": "I've analyzed your data and created a visualization.",
            "tool_used": "code_execution",
            "executed_code": "import matplotlib.pyplot as plt\nplt.plot([1,2,3])",
            "code_output": "Plot saved to figure.png",
            "generated_figures": [{"figure_name": "figure.png", "path_or_url": "/tmp/figure.png"}],
            "code_errors": None,
            "web_searches": [
                {
                    "query": "matplotlib documentation",
                    "results": [
                        {
                            "title": "Matplotlib Docs",
                            "url": "https://matplotlib.org",
                            "published": "2024-01-01"
                        }
                    ]
                }
            ],
            "files_accessed": []
        }
        
        job_details = {
            'description': 'Create a data visualization',
            'client': 'Test User',
            'job_reference': 'TEAMS-12345',
            'project': 'Data Analysis',
            'by': 'Claude AI'
        }
        
        attachment = self.formatter.create_detailed_report_card(response_data, job_details)
        
        self.assertIsNotNone(attachment)
        card = attachment.content
        
        # Check structure
        self.assertEqual(card['type'], "AdaptiveCard")
        self.assertEqual(card['version'], "1.3")
        
        # Check content sections
        card_text = str(card)
        self.assertIn("Analysis Results", card_text)
        self.assertIn("matplotlib.pyplot", card_text)  # Code
        self.assertIn("Plot saved", card_text)  # Output
        self.assertIn("figure.png", card_text)  # Figure
        self.assertIn("Sources", card_text)  # Sources section
        self.assertIn("Matplotlib Docs", card_text)  # Source title
    
    def test_report_card_with_errors(self):
        """Test report card with errors"""
        response_data = {
            "assistant_message": "There was an error in execution.",
            "tool_used": "code_execution",
            "executed_code": "print(undefined_variable)",
            "code_output": None,
            "generated_figures": [],
            "code_errors": "NameError: name 'undefined_variable' is not defined",
            "web_searches": [],
            "files_accessed": []
        }
        
        job_details = {
            'description': 'Test with error',
            'client': 'Test User',
            'job_reference': 'TEAMS-67890',
            'project': 'Error Test',
            'by': 'Claude AI'
        }
        
        attachment = self.formatter.create_detailed_report_card(response_data, job_details)
        
        self.assertIsNotNone(attachment)
        card = attachment.content
        
        # Check error section exists
        card_text = str(card)
        self.assertIn("Errors", card_text)
        self.assertIn("NameError", card_text)
        
        # Check error container has attention style
        error_containers = [item for item in card['body'] 
                           if item.get('type') == 'Container' 
                           and item.get('style') == 'attention']
        self.assertTrue(len(error_containers) > 0)


def run_async_test(coro):
    """Helper to run async tests"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


if __name__ == '__main__':
    # Run async tests
    unittest.main()