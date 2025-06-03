<?php
/**
 * Plugin Name: Claude Code Execution
 * Plugin URI: https://example.com/claude-code-execution
 * Description: Integrates Claude AI with code execution capabilities into WordPress
 * Version: 1.0.0
 * Author: Your Name
 * License: GPL-2.0+
 * License URI: http://www.gnu.org/licenses/gpl-2.0.txt
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('CCE_VERSION', '1.0.0');
define('CCE_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('CCE_PLUGIN_URL', plugin_dir_url(__FILE__));

// Include required files
require_once CCE_PLUGIN_DIR . 'includes/class-cce-api.php';
require_once CCE_PLUGIN_DIR . 'includes/class-cce-admin.php';
require_once CCE_PLUGIN_DIR . 'includes/class-cce-shortcode.php';

// Initialize the plugin
add_action('plugins_loaded', 'cce_init_plugin');

function cce_init_plugin() {
    // Initialize API endpoints
    $api = new CCE_API();
    $api->init();
    
    // Initialize admin interface
    if (is_admin()) {
        $admin = new CCE_Admin();
        $admin->init();
    }
    
    // Initialize shortcode
    $shortcode = new CCE_Shortcode();
    $shortcode->init();
}

// Activation hook
register_activation_hook(__FILE__, 'cce_activate_plugin');

function cce_activate_plugin() {
    // Create database tables if needed
    cce_create_tables();
    
    // Set default options
    add_option('cce_api_key', '');
    add_option('cce_model', 'claude-opus-4-20250514');
    add_option('cce_enable_code_execution', true);
    add_option('cce_python_backend_url', '');
    
    // Flush rewrite rules
    flush_rewrite_rules();
}

// Deactivation hook
register_deactivation_hook(__FILE__, 'cce_deactivate_plugin');

function cce_deactivate_plugin() {
    // Clean up
    flush_rewrite_rules();
}

// Create database tables
function cce_create_tables() {
    global $wpdb;
    
    $charset_collate = $wpdb->get_charset_collate();
    
    // Table for storing conversation history
    $table_name = $wpdb->prefix . 'cce_conversations';
    
    $sql = "CREATE TABLE $table_name (
        id bigint(20) NOT NULL AUTO_INCREMENT,
        user_id bigint(20) NOT NULL,
        conversation_id varchar(100) NOT NULL,
        message_role varchar(20) NOT NULL,
        message_content longtext NOT NULL,
        created_at datetime DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY  (id),
        KEY user_id (user_id),
        KEY conversation_id (conversation_id)
    ) $charset_collate;";
    
    require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
    dbDelta($sql);
}

// Enqueue scripts and styles
add_action('wp_enqueue_scripts', 'cce_enqueue_scripts');

function cce_enqueue_scripts() {
    // Only enqueue on pages with our shortcode
    global $post;
    if (is_a($post, 'WP_Post') && has_shortcode($post->post_content, 'claude_chat')) {
        // Enqueue styles
        wp_enqueue_style('cce-styles', CCE_PLUGIN_URL . 'assets/css/cce-styles.css', array(), CCE_VERSION);
        
        // Enqueue scripts
        wp_enqueue_script('cce-script', CCE_PLUGIN_URL . 'assets/js/cce-script.js', array('jquery'), CCE_VERSION, true);
        
        // Localize script
        wp_localize_script('cce-script', 'cce_ajax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('cce_nonce')
        ));
    }
}