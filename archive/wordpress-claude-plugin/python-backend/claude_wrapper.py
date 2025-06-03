#!/usr/bin/env python3
"""
Wrapper for code-exec.py to make it suitable for web deployment
"""

import os
import sys
import json
import re
from typing import Optional, List, Dict, Any
from anthropic import Anthropic

# Import the original module
sys.path.append('/home/ben_anderson/projects/codeexec-test')
from code_exec import ClaudeWithCodeExecution

class ClaudeWrapper:
    """Web-friendly wrapper for ClaudeWithCodeExecution"""
    
    def __init__(self, api_key: str, model: str = "claude-opus-4-20250514"):
        """Initialize the wrapper with a simplified interface"""
        self.claude = ClaudeWithCodeExecution(api_key=api_key, model=model)
        self.last_response = ""
        
    def chat(self, user_input: str, use_code_execution: bool = True, file_attachments: List[Dict] = None) -> str:
        """Send a message and get a response (non-streaming)"""
        # Since the original implementation uses streaming and console output,
        # we need to capture the response differently
        
        # For now, we'll create a simplified version
        message_content = [{"type": "text", "text": user_input}]
        
        # Add file attachments if provided
        if file_attachments:
            for file_info in file_attachments:
                message_content.append({
                    "type": "file", 
                    "file": {"file_id": file_info['file_id']}
                })
        
        self.claude.conversation_history.append({"role": "user", "content": message_content})
        
        # Prepare tools
        tools = []
        if use_code_execution:
            tools.append({
                "type": "code_execution_20250522",
                "name": "code_execution"
            })
        
        try:
            # Use non-streaming API call
            response = self.claude.client.messages.create(
                model=self.claude.model,
                max_tokens=4096,
                messages=self.claude.conversation_history,
                tools=tools if tools else None
            )
            
            # Extract the response text
            assistant_message = ""
            code_outputs = []
            
            for content in response.content:
                if content.type == 'text':
                    assistant_message += content.text
                elif content.type == 'tool_use' and content.name == 'code_execution':
                    # Handle code execution
                    code_input = content.input.get('code', '')
                    assistant_message += f"\n\n[Executing code:\n```python\n{code_input}\n```]\n"
                    
                    # The actual execution result would be in tool_result
                    # For now, we'll add a placeholder
                    code_outputs.append({
                        'code': code_input,
                        'output': 'Code execution output would appear here'
                    })
            
            self.claude.add_message("assistant", assistant_message)
            self.last_response = assistant_message
            
            return assistant_message
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def stream_chat(self, user_input: str, use_code_execution: bool = True):
        """Generator for streaming responses"""
        # This would implement the streaming version
        # For now, return the response in chunks
        response = self.chat(user_input, use_code_execution)
        
        # Simulate streaming by yielding chunks
        words = response.split(' ')
        chunk = ""
        for i, word in enumerate(words):
            chunk += word + " "
            if i % 5 == 0:  # Yield every 5 words
                yield {
                    'type': 'text',
                    'content': chunk
                }
                chunk = ""
        
        if chunk:
            yield {
                'type': 'text',
                'content': chunk
            }
    
    def upload_file(self, file_path: str) -> Optional[str]:
        """Upload a file and return its ID"""
        return self.claude.upload_file(file_path)
    
    def extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """Extract code blocks from the response"""
        code_blocks = []
        
        # Find code blocks in the format ```python ... ```
        pattern = r'```python\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for code in matches:
            code_blocks.append({
                'code': code,
                'language': 'python',
                'output': None  # Would be populated with actual output
            })
        
        # Also find [Code Output] sections
        output_pattern = r'\[Code Output\]:\n(.*?)(?=\n\[|$)'
        output_matches = re.findall(output_pattern, text, re.DOTALL)
        
        # Match outputs to code blocks
        for i, output in enumerate(output_matches):
            if i < len(code_blocks):
                code_blocks[i]['output'] = output.strip()
        
        return code_blocks
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.claude.reset_conversation()
    
    def get_conversation_history(self) -> List[Dict]:
        """Get the conversation history"""
        return self.claude.conversation_history