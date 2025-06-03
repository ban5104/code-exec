#!/usr/bin/env python3
"""
Test suite for claude_core module
Tests the core functionality without UI dependencies
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.core import ClaudeCore


class TestClaudeCore(unittest.TestCase):
    """Test cases for ClaudeCore class"""
    
    def setUp(self):
        """Set up test environment"""
        self.api_key = "test-api-key"
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': self.api_key}):
            self.claude = ClaudeCore(api_key=self.api_key)
    
    def test_initialization(self):
        """Test ClaudeCore initialization"""
        self.assertEqual(self.claude.api_key, self.api_key)
        self.assertEqual(self.claude.model, "claude-opus-4-20250514")
        self.assertEqual(len(self.claude.conversation_history), 0)
        self.assertEqual(len(self.claude.uploaded_files), 0)
    
    def test_initialization_no_api_key(self):
        """Test initialization without API key raises error"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                ClaudeCore()
    
    def test_get_file_type(self):
        """Test file type detection"""
        test_cases = [
            ("test.pdf", "PDF Document"),
            ("test.txt", "Text Document"),
            ("test.xlsx", "Excel Spreadsheet"),
            ("test.xls", "Excel Spreadsheet"),
            ("test.csv", "CSV Data"),
            ("test.json", "JSON Data"),
            ("test.png", "Image"),
            ("test.jpg", "Image"),
            ("test.jpeg", "Image"),
            ("test.unknown", "Unknown")
        ]
        
        for filename, expected_type in test_cases:
            with self.subTest(filename=filename):
                self.assertEqual(self.claude.get_file_type(filename), expected_type)
    
    def test_add_message(self):
        """Test adding messages to conversation history"""
        self.claude.add_message("user", "Hello")
        self.claude.add_message("assistant", "Hi there!")
        
        self.assertEqual(len(self.claude.conversation_history), 2)
        self.assertEqual(self.claude.conversation_history[0], {"role": "user", "content": "Hello"})
        self.assertEqual(self.claude.conversation_history[1], {"role": "assistant", "content": "Hi there!"})
    
    def test_track_web_search(self):
        """Test web search tracking"""
        query = "test query"
        results = [
            {"title": "Result 1", "url": "http://example.com/1", "published": "2024-01-01"},
            {"title": "Result 2", "url": "http://example.com/2", "published": "2024-01-02"}
        ]
        
        self.claude.track_web_search(query, results)
        
        self.assertEqual(len(self.claude.web_searches), 1)
        self.assertEqual(self.claude.web_searches[0]['query'], query)
        self.assertEqual(self.claude.web_searches[0]['results'], results)
        self.assertIn('timestamp', self.claude.web_searches[0])
    
    def test_track_file_access(self):
        """Test file access tracking"""
        file_name = "test.txt"
        action = "uploaded"
        
        self.claude.track_file_access(file_name, action)
        
        self.assertEqual(len(self.claude.files_accessed), 1)
        self.assertEqual(self.claude.files_accessed[0]['file_name'], file_name)
        self.assertEqual(self.claude.files_accessed[0]['action'], action)
        self.assertIn('timestamp', self.claude.files_accessed[0])
    
    def test_parse_search_results_json(self):
        """Test parsing JSON search results"""
        # Test with results in 'results' key
        json_text = '{"results": [{"title": "Test", "url": "http://test.com", "published": "2024-01-01"}]}'
        results = self.claude.parse_search_results(json_text)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Test")
        
        # Test with results in 'web.results' key
        json_text = '{"web": {"results": [{"title": "Test2", "url": "http://test2.com", "date": "2024-01-02"}]}}'
        results = self.claude.parse_search_results(json_text)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Test2")
        self.assertEqual(results[0]['published'], "2024-01-02")
    
    def test_parse_search_results_fallback(self):
        """Test search results parsing fallback"""
        # Test with invalid JSON
        results = self.claude.parse_search_results("not json")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Search completed')
        self.assertEqual(results[0]['url'], 'N/A')
    
    def test_reset_conversation(self):
        """Test conversation reset"""
        self.claude.add_message("user", "Hello")
        self.claude.reset_conversation()
        self.assertEqual(len(self.claude.conversation_history), 0)
    
    def test_set_model(self):
        """Test model setting"""
        new_model = "claude-3-5-sonnet-20241022"
        self.claude.set_model(new_model)
        self.assertEqual(self.claude.model, new_model)
    
    def test_list_files(self):
        """Test listing uploaded files"""
        # Mock uploaded files
        self.claude.uploaded_files = {
            "test.pdf": {
                "file_id": "file123",
                "file_path": "/path/to/test.pdf",
                "file_type": "PDF Document"
            },
            "data.csv": {
                "file_id": "file456",
                "file_path": "/path/to/data.csv",
                "file_type": "CSV Data"
            }
        }
        
        files = self.claude.list_files()
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]['file_name'], "test.pdf")
        self.assertEqual(files[0]['file_id'], "file123")
    
    def test_get_files_by_type(self):
        """Test getting files by type"""
        # Mock uploaded files
        self.claude.uploaded_files = {
            "test.pdf": {"file_id": "file123", "file_path": "/path/to/test.pdf", "file_type": "PDF Document"},
            "data.csv": {"file_id": "file456", "file_path": "/path/to/data.csv", "file_type": "CSV Data"},
            "report.pdf": {"file_id": "file789", "file_path": "/path/to/report.pdf", "file_type": "PDF Document"}
        }
        
        pdf_files = self.claude.get_files_by_type("PDF")
        self.assertEqual(len(pdf_files), 2)
        
        csv_files = self.claude.get_files_by_type("CSV")
        self.assertEqual(len(csv_files), 1)
    
    def test_attach_all_files_of_type(self):
        """Test attaching all files of a specific type"""
        # Mock uploaded files
        self.claude.uploaded_files = {
            "test.pdf": {"file_id": "file123", "file_path": "/path/to/test.pdf", "file_type": "PDF Document"},
            "data.csv": {"file_id": "file456", "file_path": "/path/to/data.csv", "file_type": "CSV Data"}
        }
        
        attachments = self.claude.attach_all_files_of_type("PDF")
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0]['file_id'], "file123")
        self.assertEqual(attachments[0]['file_name'], "test.pdf")
    
    def test_import_existing_file(self):
        """Test importing existing file"""
        file_id = "existing123"
        filename = "existing.pdf"
        
        result = self.claude.import_existing_file(file_id, filename)
        
        self.assertEqual(result, file_id)
        self.assertIn(filename, self.claude.uploaded_files)
        self.assertEqual(self.claude.uploaded_files[filename]['file_id'], file_id)
        self.assertEqual(self.claude.uploaded_files[filename]['file_type'], 'PDF Document')
    
    @patch('src.core.claude_core.requests.get')
    def test_list_api_files(self, mock_get):
        """Test listing API files"""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {
                    'id': 'file123',
                    'filename': 'test.pdf',
                    'size_bytes': 1048576,
                    'created_at': '2024-01-01T00:00:00Z'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        files = self.claude.list_api_files()
        
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['file_id'], 'file123')
        self.assertEqual(files[0]['filename'], 'test.pdf')
        self.assertEqual(files[0]['size_mb'], 1.0)
    
    @patch('src.core.claude_core.Anthropic')
    def test_chat_basic(self, mock_anthropic_class):
        """Test basic chat functionality"""
        # Create mock client
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        # Create mock stream events
        mock_events = [
            Mock(type="content_block_delta", delta=Mock(text="Hello, I can help you with that.")),
            Mock(type="message_stop")
        ]
        
        # Configure the mock stream
        mock_client.messages.create.return_value = iter(mock_events)
        
        # Initialize ClaudeCore with mocked client
        claude = ClaudeCore(api_key=self.api_key)
        
        # Test chat
        response = claude.chat("Hello", use_code_execution=False)
        
        self.assertEqual(response['assistant_message'], "Hello, I can help you with that.")
        self.assertIsNone(response['tool_used'])
        self.assertIsNone(response['executed_code'])
        self.assertIsNone(response['code_output'])
        self.assertEqual(len(response['generated_figures']), 0)
        self.assertIsNone(response['code_errors'])
        self.assertEqual(len(response['web_searches']), 0)
    
    @patch('src.core.claude_core.open', new_callable=unittest.mock.mock_open, read_data=b'test file content')
    @patch('src.core.claude_core.Anthropic')
    def test_upload_file(self, mock_anthropic_class, mock_open):
        """Test file upload functionality"""
        # Create mock client
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        # Mock file upload response
        mock_file_upload = Mock(id='file123')
        mock_client.files.create.return_value = mock_file_upload
        
        # Initialize ClaudeCore with mocked client
        claude = ClaudeCore(api_key=self.api_key)
        
        # Test upload
        file_path = "/path/to/test.pdf"
        result = claude.upload_file(file_path)
        
        self.assertEqual(result, 'file123')
        self.assertIn('test.pdf', claude.uploaded_files)
        self.assertEqual(claude.uploaded_files['test.pdf']['file_id'], 'file123')
        self.assertEqual(claude.uploaded_files['test.pdf']['file_type'], 'PDF Document')
    
    @patch('src.core.claude_core.Anthropic')
    def test_delete_file(self, mock_anthropic_class):
        """Test file deletion"""
        # Create mock client
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        # Initialize ClaudeCore with mocked client
        claude = ClaudeCore(api_key=self.api_key)
        
        # Add a file to uploaded_files
        claude.uploaded_files['test.pdf'] = {
            'file_id': 'file123',
            'file_path': '/path/to/test.pdf',
            'file_type': 'PDF Document'
        }
        
        # Test delete
        result = claude.delete_file('test.pdf')
        
        self.assertTrue(result)
        self.assertNotIn('test.pdf', claude.uploaded_files)
        mock_client.files.delete.assert_called_once_with('file123')
    
    def test_delete_file_not_found(self):
        """Test deleting non-existent file"""
        result = self.claude.delete_file('nonexistent.pdf')
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()