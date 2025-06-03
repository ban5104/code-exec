#!/usr/bin/env python3
"""
Claude Core Module - UI-agnostic implementation of Claude with Code Execution
This module provides the core logic for interacting with Claude API, handling
code execution, web searches, and file management without any UI dependencies.
"""

import os
import json
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
from anthropic import Anthropic
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeCore:
    """Core Claude functionality without UI dependencies."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-opus-4-20250514"):
        """Initialize Claude client with code execution tool support."""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Set it as an environment variable or pass it to the constructor.")
        
        self.client = Anthropic(
            api_key=self.api_key,
            default_headers={
                "anthropic-beta": "code-execution-2025-05-22,files-api-2025-04-14"
            }
        )
        
        self.conversation_history = []
        self.model = model
        self.uploaded_files = {}  # Store file IDs and their info
        self.web_searches = []  # Track web search queries and results
        self.files_accessed = []  # Track files accessed during conversations
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.conversation_history.append({"role": role, "content": content})
    
    def get_file_type(self, file_path: str) -> str:
        """Determine file type based on extension."""
        ext = os.path.splitext(file_path)[1].lower()
        file_type_map = {
            '.pdf': 'PDF Document',
            '.txt': 'Text Document', 
            '.xlsx': 'Excel Spreadsheet',
            '.xls': 'Excel Spreadsheet',
            '.csv': 'CSV Data',
            '.json': 'JSON Data',
            '.png': 'Image',
            '.jpg': 'Image',
            '.jpeg': 'Image'
        }
        return file_type_map.get(ext, 'Unknown')
    
    def upload_file(self, file_path: str) -> Optional[str]:
        """Upload a file using the Files API. Returns file_id if successful."""
        try:
            with open(file_path, 'rb') as file:
                file_upload = self.client.files.create(
                    file=file,
                    purpose="user_request"
                )
            
            file_name = os.path.basename(file_path)
            file_type = self.get_file_type(file_path)
            self.uploaded_files[file_name] = {
                'file_id': file_upload.id,
                'file_path': file_path,
                'file_type': file_type
            }
            
            logger.info(f"Uploaded file: {file_name} ({file_type}) - ID: {file_upload.id}")
            return file_upload.id
            
        except Exception as e:
            logger.error(f"Error uploading file {file_path}: {e}")
            return None
    
    def delete_file(self, file_name: str) -> bool:
        """Delete an uploaded file. Returns True if successful."""
        if file_name not in self.uploaded_files:
            logger.error(f"File '{file_name}' not found in uploaded files.")
            return False
            
        try:
            file_id = self.uploaded_files[file_name]['file_id']
            self.client.files.delete(file_id)
            del self.uploaded_files[file_name]
            logger.info(f"Deleted file: {file_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file {file_name}: {e}")
            return False
    
    def list_files(self) -> List[Dict[str, Any]]:
        """Return list of uploaded files with their metadata."""
        return [
            {
                'file_name': name,
                'file_type': info.get('file_type', 'Unknown'),
                'file_id': info['file_id'],
                'file_path': info['file_path']
            }
            for name, info in self.uploaded_files.items()
        ]
    
    def track_web_search(self, query: str, results: list = None) -> None:
        """Track a web search query and its results."""
        search_entry = {
            'query': query,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'results': results or []
        }
        self.web_searches.append(search_entry)
    
    def track_file_access(self, file_name: str, action: str = "accessed") -> None:
        """Track when a file is accessed or used."""
        access_entry = {
            'file_name': file_name,
            'action': action,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.files_accessed.append(access_entry)
    
    def parse_search_results(self, result_text: str) -> List[Dict[str, str]]:
        """Parse web search results from tool output."""
        results = []
        try:
            # Try to parse as JSON first
            if result_text.strip().startswith('{') or result_text.strip().startswith('['):
                data = json.loads(result_text)
                
                # Handle different JSON structures
                if isinstance(data, dict):
                    if 'results' in data:
                        search_results = data['results']
                    elif 'web' in data and 'results' in data['web']:
                        search_results = data['web']['results']
                    else:
                        search_results = [data]
                else:
                    search_results = data
                
                # Extract title, URL, and date from each result
                for item in search_results[:10]:  # Limit to 10 results
                    result_item = {
                        'title': item.get('title', item.get('name', 'N/A')),
                        'url': item.get('url', item.get('link', 'N/A')),
                        'published': item.get('published', item.get('date', item.get('timestamp', 'N/A')))
                    }
                    results.append(result_item)
            else:
                # Fallback: create a simple result entry
                results.append({
                    'title': 'Search completed',
                    'url': 'N/A',
                    'published': 'N/A'
                })
        except:
            # If parsing fails, create a generic entry
            results.append({
                'title': 'Search completed',
                'url': 'N/A', 
                'published': 'N/A'
            })
        
        return results
    
    def chat(self, user_input: str, use_code_execution: bool = True, 
             file_attachments_info: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Send a message to Claude and get a structured response.
        
        Args:
            user_input: The user's message
            use_code_execution: Whether to enable code execution tool
            file_attachments_info: List of dicts with 'file_id' and 'file_name'
            
        Returns:
            Dictionary with structured response data:
            {
                "assistant_message": str,
                "tool_used": "code_execution" | "web_search" | None,
                "executed_code": str | None,
                "code_output": str | None,
                "generated_figures": List[Dict[str, str]],
                "code_errors": str | None,
                "web_searches": List[Dict[str, Any]],
                "files_accessed": List[Dict[str, str]]
            }
        """
        # Prepare message content
        message_content = [{"type": "text", "text": user_input}]
        
        # Add file attachments if provided
        if file_attachments_info:
            for file_info in file_attachments_info:
                message_content.append({
                    "type": "file", 
                    "file": {"file_id": file_info['file_id']}
                })
                # Track file access
                file_name = file_info.get('file_name', file_info.get('file_id', 'Unknown file'))
                self.track_file_access(file_name, "attached to message")
        
        self.conversation_history.append({"role": "user", "content": message_content})
        
        # Prepare tools based on user preference
        tools = []
        if use_code_execution:
            tools.append({
                "type": "code_execution_20250522",
                "name": "code_execution"
            })
        
        # Initialize response structure
        response_data = {
            "assistant_message": "",
            "tool_used": None,
            "executed_code": None,
            "code_output": None,
            "generated_figures": [],
            "code_errors": None,
            "web_searches": [],
            "files_accessed": list(self.files_accessed)  # Include current file access history
        }
        
        try:
            # Use streaming
            # Build kwargs for API call
            kwargs = {
                "model": self.model,
                "max_tokens": 4096,
                "messages": self.conversation_history,
                "stream": True
            }
            
            # Only add tools if there are any
            if tools:
                kwargs["tools"] = tools
            
            stream = self.client.messages.create(**kwargs)
            
            # Process the streaming response
            assistant_message = ""
            current_tool_input = ""
            in_code_block = False
            web_search_detected = False
            current_search_query = ""
            
            for event in stream:
                if event.type == "content_block_start":
                    if hasattr(event, 'content_block'):
                        if event.content_block.type == "server_tool_use" and event.content_block.name == "code_execution":
                            in_code_block = True
                            response_data["tool_used"] = "code_execution"
                        elif hasattr(event.content_block, 'name') and 'search' in event.content_block.name.lower():
                            web_search_detected = True
                            response_data["tool_used"] = "web_search"
                            
                elif event.type == "content_block_delta":
                    if hasattr(event, 'delta'):
                        if hasattr(event.delta, 'text'):
                            # Regular text
                            assistant_message += event.delta.text
                        elif hasattr(event.delta, 'partial_json'):
                            # Tool use with partial JSON
                            if in_code_block and event.delta.partial_json:
                                try:
                                    # Extract code from partial JSON
                                    if '"code": "' in event.delta.partial_json:
                                        start = event.delta.partial_json.find('"code": "') + 9
                                        code_part = event.delta.partial_json[start:]
                                        code_part = code_part.rstrip('"}')
                                        code_part = code_part.encode('utf-8').decode('unicode_escape')
                                        current_tool_input += code_part
                                    elif event.delta.partial_json not in ['', '{"code": "', '"}']:
                                        code_part = event.delta.partial_json.rstrip('"}')
                                        code_part = code_part.encode('utf-8').decode('unicode_escape')
                                        current_tool_input += code_part
                                except:
                                    pass
                            elif web_search_detected and event.delta.partial_json:
                                # Extract search query
                                try:
                                    if '"query"' in event.delta.partial_json:
                                        import re
                                        query_match = re.search(r'"query"\s*:\s*"([^"]+)"', event.delta.partial_json)
                                        if query_match:
                                            current_search_query = query_match.group(1)
                                except:
                                    pass
                                    
                elif event.type == "content_block_stop":
                    if in_code_block:
                        response_data["executed_code"] = current_tool_input
                        assistant_message += f"\n\n[Executed code:\n```python\n{current_tool_input}\n```]"
                        in_code_block = False
                        current_tool_input = ""
                        
                elif event.type == "server_tool_result":
                    # Handle server tool results
                    if hasattr(event, 'result'):
                        if web_search_detected:
                            # Handle web search results
                            try:
                                if hasattr(event.result, 'content') and event.result.content:
                                    result_text = event.result.content
                                    search_results = self.parse_search_results(result_text)
                                    if current_search_query:
                                        self.track_web_search(current_search_query, search_results)
                                        response_data["web_searches"].append({
                                            "query": current_search_query,
                                            "results": search_results
                                        })
                                        current_search_query = ""
                                    web_search_detected = False
                            except:
                                pass
                        else:
                            # Handle code execution results
                            if hasattr(event.result, 'stdout'):
                                if event.result.stdout:
                                    response_data["code_output"] = event.result.stdout
                                    assistant_message += f"\n[Code Output]:\n{event.result.stdout}"
                                    
                                    # Check for generated figures
                                    # Look for patterns like "Figure saved to:" or "Plot saved as:"
                                    import re
                                    figure_patterns = [
                                        r'(?:Figure|Plot|Graph|Chart|Image)\s+saved\s+(?:to|as):\s*(.+)',
                                        r'Saved\s+(?:figure|plot|graph|chart|image)\s+to:\s*(.+)',
                                        r'(?:Generated|Created)\s+(.+\.(?:png|jpg|jpeg|svg|pdf))'
                                    ]
                                    
                                    for pattern in figure_patterns:
                                        matches = re.findall(pattern, event.result.stdout, re.IGNORECASE)
                                        for match in matches:
                                            figure_path = match.strip()
                                            figure_name = os.path.basename(figure_path)
                                            response_data["generated_figures"].append({
                                                "figure_name": figure_name,
                                                "path_or_url": figure_path
                                            })
                                            
                            if hasattr(event.result, 'stderr') and event.result.stderr:
                                response_data["code_errors"] = event.result.stderr
                                assistant_message += f"\n[Errors]:\n{event.result.stderr}"
            
            response_data["assistant_message"] = assistant_message
            self.add_message("assistant", assistant_message)
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return {
                "assistant_message": f"Error: {str(e)}",
                "tool_used": None,
                "executed_code": None,
                "code_output": None,
                "generated_figures": [],
                "code_errors": None,
                "web_searches": [],
                "files_accessed": list(self.files_accessed)
            }
    
    def reset_conversation(self) -> None:
        """Reset the conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared.")
    
    def set_model(self, model: str) -> None:
        """Change the model being used."""
        self.model = model
        logger.info(f"Model changed to: {model}")
    
    def get_files_by_type(self, file_type: str) -> List[Dict[str, Any]]:
        """Get all uploaded files of a specific type."""
        return [
            {
                'file_name': name,
                'file_id': info['file_id'],
                'file_path': info['file_path'],
                'file_type': info.get('file_type', 'Unknown')
            }
            for name, info in self.uploaded_files.items() 
            if info.get('file_type', '').lower().find(file_type.lower()) != -1
        ]
    
    def attach_all_files_of_type(self, file_type: str) -> List[Dict[str, str]]:
        """Get file attachments for all files of a specific type."""
        matching_files = self.get_files_by_type(file_type)
        return [
            {'file_id': file_info['file_id'], 'file_name': file_info['file_name']} 
            for file_info in matching_files
        ]
    
    def import_existing_file(self, file_id: str, filename: str, file_type: str = None) -> str:
        """Import an already uploaded file by its ID."""
        if not file_type:
            file_type = self.get_file_type(filename)
        
        self.uploaded_files[filename] = {
            'file_id': file_id,
            'file_path': f'[Already uploaded] {filename}',
            'file_type': file_type
        }
        logger.info(f"Imported existing file: {filename} ({file_type}) - ID: {file_id}")
        return file_id
    
    def list_api_files(self) -> List[Dict[str, Any]]:
        """List all files in your Anthropic account."""
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "anthropic-beta": "files-api-2025-04-14"
            }
            
            response = requests.get("https://api.anthropic.com/v1/files", headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            files = []
            for file in data.get('data', []):
                files.append({
                    'filename': file['filename'],
                    'file_id': file['id'],
                    'size_mb': round(file['size_bytes'] / 1024 / 1024, 2),
                    'created_at': file['created_at'].split('T')[0]
                })
            
            return files
            
        except Exception as e:
            logger.error(f"Error listing API files: {e}")
            return []