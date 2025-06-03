<?php
/**
 * API Handler Class
 */

class CCE_API {
    
    public function init() {
        // Register AJAX handlers
        add_action('wp_ajax_cce_send_message', array($this, 'handle_send_message'));
        add_action('wp_ajax_nopriv_cce_send_message', array($this, 'handle_send_message'));
        
        add_action('wp_ajax_cce_upload_file', array($this, 'handle_file_upload'));
        add_action('wp_ajax_nopriv_cce_upload_file', array($this, 'handle_file_upload'));
        
        // Register REST API endpoints
        add_action('rest_api_init', array($this, 'register_rest_routes'));
    }
    
    public function register_rest_routes() {
        register_rest_route('cce/v1', '/chat', array(
            'methods' => 'POST',
            'callback' => array($this, 'rest_send_message'),
            'permission_callback' => array($this, 'check_permissions')
        ));
        
        register_rest_route('cce/v1', '/upload', array(
            'methods' => 'POST',
            'callback' => array($this, 'rest_upload_file'),
            'permission_callback' => array($this, 'check_permissions')
        ));
    }
    
    public function check_permissions() {
        // Check if user is logged in or has valid API key
        return is_user_logged_in() || $this->validate_api_key();
    }
    
    private function validate_api_key() {
        $headers = getallheaders();
        $api_key = isset($headers['X-CCE-API-Key']) ? $headers['X-CCE-API-Key'] : '';
        $stored_key = get_option('cce_client_api_key');
        
        return !empty($api_key) && $api_key === $stored_key;
    }
    
    public function handle_send_message() {
        // Verify nonce
        if (!wp_verify_nonce($_POST['nonce'], 'cce_nonce')) {
            wp_die('Security check failed');
        }
        
        $message = sanitize_textarea_field($_POST['message']);
        $conversation_id = sanitize_text_field($_POST['conversation_id']);
        $use_code_execution = isset($_POST['use_code_execution']) ? (bool)$_POST['use_code_execution'] : true;
        
        // Call Python backend
        $response = $this->call_python_backend('chat', array(
            'message' => $message,
            'conversation_id' => $conversation_id,
            'use_code_execution' => $use_code_execution
        ));
        
        wp_send_json($response);
    }
    
    public function handle_file_upload() {
        // Verify nonce
        if (!wp_verify_nonce($_POST['nonce'], 'cce_nonce')) {
            wp_die('Security check failed');
        }
        
        if (!isset($_FILES['file'])) {
            wp_send_json_error('No file uploaded');
        }
        
        $file = $_FILES['file'];
        
        // Validate file
        $allowed_types = array('pdf', 'txt', 'csv', 'xlsx', 'xls', 'json', 'png', 'jpg', 'jpeg');
        $file_ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
        
        if (!in_array($file_ext, $allowed_types)) {
            wp_send_json_error('File type not allowed');
        }
        
        // Call Python backend to upload file
        $response = $this->call_python_backend('upload', array(
            'file_path' => $file['tmp_name'],
            'file_name' => $file['name']
        ));
        
        wp_send_json($response);
    }
    
    private function call_python_backend($endpoint, $data) {
        $backend_url = get_option('cce_python_backend_url');
        
        if (empty($backend_url)) {
            return array(
                'success' => false,
                'error' => 'Python backend URL not configured'
            );
        }
        
        $url = $backend_url . '/' . $endpoint;
        
        // Add API key to data
        $data['api_key'] = get_option('cce_api_key');
        $data['model'] = get_option('cce_model');
        
        $response = wp_remote_post($url, array(
            'body' => json_encode($data),
            'headers' => array(
                'Content-Type' => 'application/json'
            ),
            'timeout' => 300 // 5 minutes timeout for long responses
        ));
        
        if (is_wp_error($response)) {
            return array(
                'success' => false,
                'error' => $response->get_error_message()
            );
        }
        
        $body = wp_remote_retrieve_body($response);
        return json_decode($body, true);
    }
    
    public function rest_send_message($request) {
        $params = $request->get_json_params();
        
        $message = sanitize_textarea_field($params['message']);
        $conversation_id = sanitize_text_field($params['conversation_id']);
        $use_code_execution = isset($params['use_code_execution']) ? (bool)$params['use_code_execution'] : true;
        
        // Store conversation in database
        $this->store_message($conversation_id, 'user', $message);
        
        // Call Python backend
        $response = $this->call_python_backend('chat', array(
            'message' => $message,
            'conversation_id' => $conversation_id,
            'use_code_execution' => $use_code_execution
        ));
        
        if ($response['success']) {
            // Store assistant response
            $this->store_message($conversation_id, 'assistant', $response['response']);
        }
        
        return new WP_REST_Response($response, 200);
    }
    
    public function rest_upload_file($request) {
        $files = $request->get_file_params();
        
        if (empty($files['file'])) {
            return new WP_REST_Response(array(
                'success' => false,
                'error' => 'No file uploaded'
            ), 400);
        }
        
        $file = $files['file'];
        
        // Validate file
        $allowed_types = array('pdf', 'txt', 'csv', 'xlsx', 'xls', 'json', 'png', 'jpg', 'jpeg');
        $file_ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
        
        if (!in_array($file_ext, $allowed_types)) {
            return new WP_REST_Response(array(
                'success' => false,
                'error' => 'File type not allowed'
            ), 400);
        }
        
        // Call Python backend to upload file
        $response = $this->call_python_backend('upload', array(
            'file_path' => $file['tmp_name'],
            'file_name' => $file['name']
        ));
        
        return new WP_REST_Response($response, 200);
    }
    
    private function store_message($conversation_id, $role, $content) {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'cce_conversations';
        $user_id = get_current_user_id();
        
        $wpdb->insert(
            $table_name,
            array(
                'user_id' => $user_id,
                'conversation_id' => $conversation_id,
                'message_role' => $role,
                'message_content' => $content
            ),
            array('%d', '%s', '%s', '%s')
        );
    }
}