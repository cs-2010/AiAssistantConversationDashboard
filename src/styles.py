"""
Styling constants for the AI Assistant Conversation Dashboard.
"""

# Constants
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# Language flags mapping
LANGUAGE_FLAGS = {
    'arabic': '🇸🇦',
    'chinese': '🇨🇳',
    'dutch': '🇳🇱',
    'english': '🇬🇧',
    'french': '🇫🇷',
    'german': '🇩🇪',
    'italian': '🇮🇹',
    'japanese': '🇯🇵',
    'korean': '🇰🇷',
    'portuguese': '🇵🇹',
    'russian': '🇷🇺',
    'spanish': '🇪🇸',
    'turkish': '🇹🇷',
    'unknown': '❓'
}

# Color schemes for messages
USER_COLORS = {
    'bg_color': '#e3f2fd',
    'border_color': '#1976d2',
    'header_color': '#1976d2',
    'text_color': '#1565c0',
    'content_bg': 'rgba(25, 118, 210, 0.05)',
    'icon': '👤'
}

ASSISTANT_COLORS = {
    'bg_color': '#e8f5e9',
    'border_color': '#2e7d32',
    'header_color': '#2e7d32',
    'text_color': '#1b5e20',
    'content_bg': 'rgba(46, 125, 50, 0.05)',
    'icon': '🤖'
}

CONTEXT_COLORS = {
    'bg_color': '#f3e5f5',
    'border_color': '#9c27b0',
    'header_color': '#9c27b0',
    'text_color': '#6a1b9a',
    'content_bg': 'rgba(156, 39, 176, 0.05)',
    'icon': '🔍'
}

SYSTEM_COLORS = {
    'bg_color': '#f8f9fa',
    'border_color': '#dee2e6',
    'header_color': '#495057',
    'text_color': '#495057',
    'content_bg': 'rgba(73, 80, 87, 0.05)',
    'icon': '⚙️'
}

# Style for topic capsules
TOPIC_CAPSULE_STYLE = """
    display: inline-block;
    padding: 0.25em 0.5em;
    margin: 0.1em;
    border-radius: 1em;
    background-color: #e9ecef;
    color: #495057;
    font-size: 0.875em;
"""

# Style for code blocks
CODE_BLOCK_STYLE = """
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 0.25rem;
    padding: 1rem;
    margin: 1rem 0;
    font-family: monospace;
    white-space: pre-wrap;
    word-wrap: break-word;
"""
