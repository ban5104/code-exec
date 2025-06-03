#!/usr/bin/env python3
"""
Flask backend server for WordPress Claude plugin
This wraps the code-exec.py functionality
"""

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import json
import os
import sys
import tempfile
import uuid
from typing import Dict, Any
import logging

# Import the Claude module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from claude_wrapper import ClaudeWrapper

app = Flask(__name__)
CORS(app)  # Enable CORS for WordPress frontend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store conversation instances
conversations: Dict[str, ClaudeWrapper] = {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'claude-backend'})

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('api_key'):
            return jsonify({'success': False, 'error': 'API key required'}), 400
        
        if not data.get('message'):
            return jsonify({'success': False, 'error': 'Message required'}), 400
        
        conversation_id = data.get('conversation_id', str(uuid.uuid4()))
        use_code_execution = data.get('use_code_execution', True)
        model = data.get('model', 'claude-opus-4-20250514')
        uploaded_files = data.get('uploaded_files', [])
        
        # Get or create conversation instance
        if conversation_id not in conversations:
            conversations[conversation_id] = ClaudeWrapper(
                api_key=data['api_key'],
                model=model
            )
        
        claude = conversations[conversation_id]
        
        # Handle file attachments
        file_attachments = []
        for file_info in uploaded_files:
            file_attachments.append({
                'file_id': file_info['file_id'],
                'file_name': file_info.get('file_name', 'unknown')
            })
        
        # Get response from Claude
        response = claude.chat(
            user_input=data['message'],
            use_code_execution=use_code_execution,
            file_attachments=file_attachments
        )
        
        # Extract code blocks and outputs
        code_blocks = claude.extract_code_blocks(response)
        
        return jsonify({
            'success': True,
            'response': response,
            'code_blocks': code_blocks,
            'conversation_id': conversation_id
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    try:
        data = request.json
        
        if not data.get('api_key'):
            return jsonify({'success': False, 'error': 'API key required'}), 400
        
        # For WordPress integration, we'll need to handle file uploads differently
        # The file will be uploaded to WordPress first, then we'll process it
        file_path = data.get('file_path')
        file_name = data.get('file_name')
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'}), 400
        
        # Create a temporary Claude instance for file upload
        claude = ClaudeWrapper(api_key=data['api_key'])
        
        # Upload file using Claude's file API
        file_id = claude.upload_file(file_path)
        
        if file_id:
            return jsonify({
                'success': True,
                'file_id': file_id,
                'file_name': file_name
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to upload file'}), 500
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/stream-chat', methods=['POST'])
def stream_chat():
    """Handle streaming chat responses"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('api_key'):
            return jsonify({'success': False, 'error': 'API key required'}), 400
        
        if not data.get('message'):
            return jsonify({'success': False, 'error': 'Message required'}), 400
        
        conversation_id = data.get('conversation_id', str(uuid.uuid4()))
        use_code_execution = data.get('use_code_execution', True)
        model = data.get('model', 'claude-opus-4-20250514')
        
        # Get or create conversation instance
        if conversation_id not in conversations:
            conversations[conversation_id] = ClaudeWrapper(
                api_key=data['api_key'],
                model=model
            )
        
        claude = conversations[conversation_id]
        
        def generate():
            """Generate streaming response"""
            try:
                # Stream the response
                for chunk in claude.stream_chat(data['message'], use_code_execution):
                    yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        logger.error(f"Stream chat error: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/reset/<conversation_id>', methods=['POST'])
def reset_conversation(conversation_id):
    """Reset a conversation"""
    try:
        if conversation_id in conversations:
            del conversations[conversation_id]
        
        return jsonify({'success': True, 'message': 'Conversation reset'})
        
    except Exception as e:
        logger.error(f"Reset error: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/conversations', methods=['GET'])
def list_conversations():
    """List active conversations"""
    return jsonify({
        'success': True,
        'conversations': list(conversations.keys()),
        'count': len(conversations)
    })

# Cleanup old conversations periodically
def cleanup_old_conversations():
    """Remove conversations older than 1 hour"""
    # This would be implemented with timestamps
    pass

if __name__ == '__main__':
    # Configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Claude backend server on {host}:{port}")
    
    app.run(host=host, port=port, debug=debug)