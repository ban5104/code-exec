jQuery(document).ready(function($) {
    let conversationId = $('.cce-chat-container').data('conversation-id');
    let uploadedFiles = [];
    
    // Send message function
    function sendMessage() {
        const message = $('#cce-message-input').val().trim();
        if (!message && uploadedFiles.length === 0) return;
        
        // Disable input and button
        $('#cce-message-input').prop('disabled', true);
        $('#cce-send-btn').prop('disabled', true);
        $('#cce-loading').show();
        
        // Add user message to chat
        if (message) {
            addMessage('user', message);
        }
        
        // Prepare data
        const data = {
            action: 'cce_send_message',
            nonce: cce_ajax.nonce,
            message: message,
            conversation_id: conversationId,
            use_code_execution: $('#cce-code-execution').is(':checked'),
            uploaded_files: uploadedFiles
        };
        
        // Send AJAX request
        $.post(cce_ajax.ajax_url, data, function(response) {
            if (response.success) {
                // Add assistant response
                addMessage('assistant', response.response, response.code_blocks);
                
                // Clear uploaded files
                uploadedFiles = [];
                updateUploadedFilesDisplay();
            } else {
                addMessage('system', 'Error: ' + response.error);
            }
        }).fail(function() {
            addMessage('system', 'Failed to send message. Please try again.');
        }).always(function() {
            // Re-enable input and button
            $('#cce-message-input').val('').prop('disabled', false);
            $('#cce-send-btn').prop('disabled', false);
            $('#cce-loading').hide();
            $('#cce-message-input').focus();
        });
    }
    
    // Add message to chat
    function addMessage(role, content, codeBlocks) {
        const messagesContainer = $('#cce-messages');
        
        let avatar = '👤';
        if (role === 'assistant') avatar = '🤖';
        if (role === 'system') avatar = '⚠️';
        
        const messageHtml = `
            <div class="cce-message ${role}">
                <div class="cce-message-avatar">${avatar}</div>
                <div class="cce-message-content">
                    ${formatMessage(content, codeBlocks)}
                </div>
            </div>
        `;
        
        messagesContainer.append(messageHtml);
        messagesContainer.scrollTop(messagesContainer[0].scrollHeight);
    }
    
    // Format message content
    function formatMessage(content, codeBlocks) {
        // Convert markdown-style code blocks
        content = content.replace(/```(\w+)?\n([\s\S]*?)```/g, function(match, lang, code) {
            return `<pre class="cce-code-block"><code>${escapeHtml(code)}</code></pre>`;
        });
        
        // Convert inline code
        content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Convert line breaks
        content = content.replace(/\n/g, '<br>');
        
        // Add code execution outputs if present
        if (codeBlocks && codeBlocks.length > 0) {
            codeBlocks.forEach(function(block) {
                if (block.output) {
                    content += `<div class="cce-code-output"><strong>Output:</strong><pre>${escapeHtml(block.output)}</pre></div>`;
                }
            });
        }
        
        return content;
    }
    
    // Escape HTML
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
    
    // Handle file upload
    $('#cce-file-input').change(function() {
        const file = this.files[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append('action', 'cce_upload_file');
        formData.append('nonce', cce_ajax.nonce);
        formData.append('file', file);
        
        $('#cce-loading').show();
        
        $.ajax({
            url: cce_ajax.ajax_url,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    uploadedFiles.push({
                        file_id: response.file_id,
                        file_name: file.name
                    });
                    updateUploadedFilesDisplay();
                    addMessage('system', `File uploaded: ${file.name}`);
                } else {
                    addMessage('system', `Failed to upload file: ${response.error}`);
                }
            },
            error: function() {
                addMessage('system', 'File upload failed. Please try again.');
            },
            complete: function() {
                $('#cce-loading').hide();
                $('#cce-file-input').val('');
            }
        });
    });
    
    // Update uploaded files display
    function updateUploadedFilesDisplay() {
        const container = $('#cce-uploaded-files');
        container.empty();
        
        uploadedFiles.forEach(function(file, index) {
            container.append(`
                <div class="cce-uploaded-file">
                    📄 ${file.file_name}
                    <span class="cce-remove-file" data-index="${index}">✖</span>
                </div>
            `);
        });
    }
    
    // Remove uploaded file
    $(document).on('click', '.cce-remove-file', function() {
        const index = $(this).data('index');
        uploadedFiles.splice(index, 1);
        updateUploadedFilesDisplay();
    });
    
    // Send message on button click
    $('#cce-send-btn').click(sendMessage);
    
    // Send message on Enter (but not Shift+Enter)
    $('#cce-message-input').keydown(function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Clear chat
    $('.cce-clear-chat').click(function() {
        if (confirm('Clear conversation history?')) {
            $('#cce-messages').empty();
            conversationId = 'conv_' + Math.random().toString(36).substr(2, 12);
            $('.cce-chat-container').data('conversation-id', conversationId);
            addMessage('system', 'Conversation cleared. Starting new conversation.');
        }
    });
    
    // Initialize
    addMessage('assistant', 'Hello! I\'m Claude, your AI assistant with code execution capabilities. How can I help you today?');
});