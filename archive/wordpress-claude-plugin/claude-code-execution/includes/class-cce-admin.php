<?php
/**
 * Admin Interface Class
 */

class CCE_Admin {
    
    public function init() {
        // Add admin menu
        add_action('admin_menu', array($this, 'add_admin_menu'));
        
        // Register settings
        add_action('admin_init', array($this, 'register_settings'));
    }
    
    public function add_admin_menu() {
        add_menu_page(
            'Claude Code Execution',
            'Claude AI',
            'manage_options',
            'cce-settings',
            array($this, 'settings_page'),
            'dashicons-format-chat',
            30
        );
        
        add_submenu_page(
            'cce-settings',
            'Settings',
            'Settings',
            'manage_options',
            'cce-settings',
            array($this, 'settings_page')
        );
        
        add_submenu_page(
            'cce-settings',
            'Conversations',
            'Conversations',
            'manage_options',
            'cce-conversations',
            array($this, 'conversations_page')
        );
    }
    
    public function register_settings() {
        // Register settings
        register_setting('cce_settings_group', 'cce_api_key');
        register_setting('cce_settings_group', 'cce_model');
        register_setting('cce_settings_group', 'cce_enable_code_execution');
        register_setting('cce_settings_group', 'cce_python_backend_url');
        register_setting('cce_settings_group', 'cce_client_api_key');
        
        // Add settings sections
        add_settings_section(
            'cce_main_settings',
            'Main Settings',
            array($this, 'main_settings_section'),
            'cce-settings'
        );
        
        // Add settings fields
        add_settings_field(
            'cce_api_key',
            'Anthropic API Key',
            array($this, 'api_key_field'),
            'cce-settings',
            'cce_main_settings'
        );
        
        add_settings_field(
            'cce_model',
            'Claude Model',
            array($this, 'model_field'),
            'cce-settings',
            'cce_main_settings'
        );
        
        add_settings_field(
            'cce_enable_code_execution',
            'Enable Code Execution',
            array($this, 'code_execution_field'),
            'cce-settings',
            'cce_main_settings'
        );
        
        add_settings_field(
            'cce_python_backend_url',
            'Python Backend URL',
            array($this, 'backend_url_field'),
            'cce-settings',
            'cce_main_settings'
        );
        
        add_settings_field(
            'cce_client_api_key',
            'Client API Key',
            array($this, 'client_api_key_field'),
            'cce-settings',
            'cce_main_settings'
        );
    }
    
    public function settings_page() {
        ?>
        <div class="wrap">
            <h1>Claude Code Execution Settings</h1>
            
            <?php if (isset($_GET['settings-updated'])) : ?>
                <div class="notice notice-success is-dismissible">
                    <p>Settings saved successfully!</p>
                </div>
            <?php endif; ?>
            
            <form method="post" action="options.php">
                <?php settings_fields('cce_settings_group'); ?>
                <?php do_settings_sections('cce-settings'); ?>
                <?php submit_button(); ?>
            </form>
            
            <hr>
            
            <h2>Usage Instructions</h2>
            <p>To add the Claude chat interface to any page or post, use the shortcode:</p>
            <code>[claude_chat]</code>
            
            <h3>Python Backend Setup</h3>
            <p>You need to set up a Python backend server to handle the Claude API calls. Here's how:</p>
            <ol>
                <li>Deploy the Python backend script (provided separately) to a server</li>
                <li>Enter the backend URL above (e.g., https://your-server.com/claude-api)</li>
                <li>Make sure the backend has access to the Anthropic API</li>
            </ol>
            
            <h3>Security</h3>
            <p>The Client API Key is used to secure REST API access. Share this key only with trusted applications.</p>
        </div>
        <?php
    }
    
    public function conversations_page() {
        global $wpdb;
        $table_name = $wpdb->prefix . 'cce_conversations';
        
        // Get unique conversations
        $conversations = $wpdb->get_results("
            SELECT DISTINCT conversation_id, user_id, MIN(created_at) as started_at, COUNT(*) as message_count
            FROM $table_name
            GROUP BY conversation_id, user_id
            ORDER BY started_at DESC
            LIMIT 50
        ");
        
        ?>
        <div class="wrap">
            <h1>Conversation History</h1>
            
            <table class="wp-list-table widefat fixed striped">
                <thead>
                    <tr>
                        <th>Conversation ID</th>
                        <th>User</th>
                        <th>Started</th>
                        <th>Messages</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($conversations as $conv) : ?>
                        <?php $user = get_user_by('id', $conv->user_id); ?>
                        <tr>
                            <td><?php echo esc_html($conv->conversation_id); ?></td>
                            <td><?php echo $user ? esc_html($user->display_name) : 'Guest'; ?></td>
                            <td><?php echo esc_html($conv->started_at); ?></td>
                            <td><?php echo esc_html($conv->message_count); ?></td>
                            <td>
                                <a href="?page=cce-conversations&view=<?php echo esc_attr($conv->conversation_id); ?>" class="button button-small">View</a>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        <?php
        
        // Show conversation details if requested
        if (isset($_GET['view'])) {
            $this->show_conversation_details($_GET['view']);
        }
    }
    
    private function show_conversation_details($conversation_id) {
        global $wpdb;
        $table_name = $wpdb->prefix . 'cce_conversations';
        
        $messages = $wpdb->get_results($wpdb->prepare("
            SELECT * FROM $table_name
            WHERE conversation_id = %s
            ORDER BY created_at ASC
        ", $conversation_id));
        
        ?>
        <hr>
        <h2>Conversation: <?php echo esc_html($conversation_id); ?></h2>
        <div class="cce-conversation-details">
            <?php foreach ($messages as $msg) : ?>
                <div class="cce-message <?php echo esc_attr($msg->message_role); ?>">
                    <strong><?php echo ucfirst(esc_html($msg->message_role)); ?>:</strong>
                    <pre><?php echo esc_html($msg->message_content); ?></pre>
                    <small><?php echo esc_html($msg->created_at); ?></small>
                </div>
            <?php endforeach; ?>
        </div>
        <style>
            .cce-message {
                margin: 10px 0;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            .cce-message.user {
                background-color: #f0f8ff;
            }
            .cce-message.assistant {
                background-color: #f0fff0;
            }
            .cce-message pre {
                white-space: pre-wrap;
                word-wrap: break-word;
            }
        </style>
        <?php
    }
    
    public function main_settings_section() {
        echo '<p>Configure your Claude AI integration settings below:</p>';
    }
    
    public function api_key_field() {
        $value = get_option('cce_api_key');
        echo '<input type="password" name="cce_api_key" value="' . esc_attr($value) . '" class="regular-text" />';
        echo '<p class="description">Your Anthropic API key</p>';
    }
    
    public function model_field() {
        $value = get_option('cce_model');
        $models = array(
            'claude-opus-4-20250514' => 'Claude Opus 4',
            'claude-3-5-sonnet-20241022' => 'Claude 3.5 Sonnet',
            'claude-3-5-haiku-20241022' => 'Claude 3.5 Haiku',
            'claude-3-opus-20240229' => 'Claude 3 Opus'
        );
        
        echo '<select name="cce_model">';
        foreach ($models as $model_id => $model_name) {
            $selected = ($value == $model_id) ? 'selected' : '';
            echo '<option value="' . esc_attr($model_id) . '" ' . $selected . '>' . esc_html($model_name) . '</option>';
        }
        echo '</select>';
    }
    
    public function code_execution_field() {
        $value = get_option('cce_enable_code_execution');
        echo '<input type="checkbox" name="cce_enable_code_execution" value="1" ' . checked(1, $value, false) . ' />';
        echo '<p class="description">Enable code execution capabilities</p>';
    }
    
    public function backend_url_field() {
        $value = get_option('cce_python_backend_url');
        echo '<input type="url" name="cce_python_backend_url" value="' . esc_attr($value) . '" class="regular-text" />';
        echo '<p class="description">URL of your Python backend server (e.g., https://your-server.com/claude-api)</p>';
    }
    
    public function client_api_key_field() {
        $value = get_option('cce_client_api_key');
        if (empty($value)) {
            $value = wp_generate_password(32, false);
            update_option('cce_client_api_key', $value);
        }
        echo '<input type="text" name="cce_client_api_key" value="' . esc_attr($value) . '" class="regular-text" readonly />';
        echo '<p class="description">API key for external applications to access the REST API</p>';
    }
}