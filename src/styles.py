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

CODE_BLOCK_STYLE = {
    'bg_color': '#f8f9fa',  # Light grey background
    'border_color': '#e9ecef',  # Slightly darker grey for border
    'text_color': '#212529'  # Dark grey for text
}

TOPIC_CAPSULE_STYLE = {
    'bg_color': '#f0f0f0',  # Light grey background
    'border_color': '#d0d0d0',  # Slightly darker grey for border
    'text_color': '#333333',  # Dark grey for text
    'padding': '2px 8px',
    'border_radius': '12px',
    'margin': '0 2px'
}
