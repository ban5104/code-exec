<?php
/**
 * Shortcode Handler Class
 */

class CCE_Shortcode {
    
    public function init() {
        add_shortcode('claude_chat', array($this, 'render_chat_interface'));
    }
    
    public function render_chat_interface($atts) {
        // Parse attributes
        $atts = shortcode_atts(array(
            'height' => '600px',
            'theme' => 'light',
            'show_upload' => 'true',
            'show_code_toggle' => 'true'
        ), $atts);
        
        // Generate unique conversation ID
        $conversation_id = 'conv_' . wp_generate_password(12, false);
        
        ob_start();
        ?>
        <div class="cce-chat-container" data-conversation-id="<?php echo esc_attr($conversation_id); ?>" style="height: <?php echo esc_attr($atts['height']); ?>">
            <div class="cce-chat-header">
                <h3>Claude AI Assistant</h3>
                <div class="cce-chat-controls">
                    <?php if ($atts['show_code_toggle'] === 'true') : ?>
                        <label class="cce-toggle">
                            <input type="checkbox" id="cce-code-execution" checked>
                            <span>Code Execution</span>
                        </label>
                    <?php endif; ?>
                    <button class="cce-clear-chat" title="Clear conversation">🗑️</button>
                </div>
            </div>
            
            <div class="cce-chat-messages" id="cce-messages"></div>
            
            <div class="cce-chat-input-area">
                <?php if ($atts['show_upload'] === 'true') : ?>
                    <div class="cce-file-upload">
                        <input type="file" id="cce-file-input" accept=".pdf,.txt,.csv,.xlsx,.xls,.json,.png,.jpg,.jpeg" style="display: none;">
                        <button class="cce-upload-btn" onclick="document.getElementById('cce-file-input').click()">📎 Upload File</button>
                        <div class="cce-uploaded-files" id="cce-uploaded-files"></div>
                    </div>
                <?php endif; ?>
                
                <div class="cce-input-wrapper">
                    <textarea id="cce-message-input" placeholder="Type your message here..." rows="3"></textarea>
                    <button id="cce-send-btn" class="cce-send-button">Send</button>
                </div>
            </div>
            
            <div class="cce-loading" id="cce-loading" style="display: none;">
                <div class="cce-spinner"></div>
                <span>Claude is thinking...</span>
            </div>
        </div>
        
        <style>
            .cce-chat-container {
                border: 1px solid #ddd;
                border-radius: 8px;
                display: flex;
                flex-direction: column;
                background: #fff;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .cce-chat-header {
                padding: 15px;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: #f8f9fa;
                border-radius: 8px 8px 0 0;
            }
            
            .cce-chat-header h3 {
                margin: 0;
                color: #333;
            }
            
            .cce-chat-controls {
                display: flex;
                gap: 10px;
                align-items: center;
            }
            
            .cce-toggle {
                display: flex;
                align-items: center;
                gap: 5px;
                cursor: pointer;
            }
            
            .cce-clear-chat {
                background: none;
                border: none;
                font-size: 20px;
                cursor: pointer;
                padding: 5px;
                border-radius: 4px;
                transition: background 0.2s;
            }
            
            .cce-clear-chat:hover {
                background: #e0e0e0;
            }
            
            .cce-chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #fafafa;
            }
            
            .cce-message {
                margin-bottom: 15px;
                display: flex;
                align-items: flex-start;
                gap: 10px;
            }
            
            .cce-message-avatar {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                color: white;
                flex-shrink: 0;
            }
            
            .cce-message.user .cce-message-avatar {
                background: #007cba;
            }
            
            .cce-message.assistant .cce-message-avatar {
                background: #4caf50;
            }
            
            .cce-message-content {
                flex: 1;
                background: white;
                padding: 10px 15px;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            .cce-message-content pre {
                background: #f5f5f5;
                padding: 10px;
                border-radius: 4px;
                overflow-x: auto;
            }
            
            .cce-message-content code {
                background: #f0f0f0;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: monospace;
            }
            
            .cce-code-block {
                background: #1e1e1e;
                color: #d4d4d4;
                padding: 15px;
                border-radius: 6px;
                margin: 10px 0;
                overflow-x: auto;
            }
            
            .cce-code-output {
                background: #f0f8ff;
                border: 1px solid #0066cc;
                padding: 10px;
                border-radius: 4px;
                margin: 10px 0;
            }
            
            .cce-chat-input-area {
                padding: 15px;
                border-top: 1px solid #eee;
                background: #f8f9fa;
                border-radius: 0 0 8px 8px;
            }
            
            .cce-file-upload {
                margin-bottom: 10px;
            }
            
            .cce-upload-btn {
                background: #007cba;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }
            
            .cce-upload-btn:hover {
                background: #005a87;
            }
            
            .cce-uploaded-files {
                margin-top: 10px;
                display: flex;
                flex-wrap: wrap;
                gap: 5px;
            }
            
            .cce-uploaded-file {
                background: #e3f2fd;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 12px;
                display: flex;
                align-items: center;
                gap: 5px;
            }
            
            .cce-remove-file {
                cursor: pointer;
                color: #666;
            }
            
            .cce-input-wrapper {
                display: flex;
                gap: 10px;
            }
            
            #cce-message-input {
                flex: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                resize: vertical;
                font-family: inherit;
            }
            
            .cce-send-button {
                background: #4caf50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
            }
            
            .cce-send-button:hover {
                background: #45a049;
            }
            
            .cce-send-button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            
            .cce-loading {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(255, 255, 255, 0.9);
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .cce-spinner {
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #007cba;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
        <?php
        
        return ob_get_clean();
    }
}