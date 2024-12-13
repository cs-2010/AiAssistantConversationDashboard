import os
from datetime import datetime
from pathlib import Path
import functools

# Third-party imports
import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import html
import re

#######################
# Constants & Styling #
#######################

# Constants
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_MONGO_TIMEOUT = 30000

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

######################
# Database Functions #
######################

def get_mongodb_uri() -> str:
    """Retrieve MongoDB URI from environment variables."""
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise ValueError("MONGO_URI environment variable is not set. Please check your .env file.")
    return str(uri).strip()

# Initialize MongoDB client
try:
    MONGO_URI = get_mongodb_uri()
    client = MongoClient(
        MONGO_URI,
        connectTimeoutMS=DEFAULT_MONGO_TIMEOUT,
        socketTimeoutMS=DEFAULT_MONGO_TIMEOUT,
        serverSelectionTimeoutMS=DEFAULT_MONGO_TIMEOUT,
        waitQueueTimeoutMS=DEFAULT_MONGO_TIMEOUT,
        retryWrites=True,
        tls=True,
    )
except Exception as e:
    st.error(f"Error creating MongoDB client: {str(e)}")
    raise

def get_database(database_name: str):
    """Get a MongoDB database instance."""
    return client[database_name]

#########################
# Data Helper Functions #
#########################

# Compile regular expressions for escape_html_preserve_markdown
_code_block_regex = re.compile(r'```[\s\S]*?```|`[^`]+`')
_html_tag_regex = re.compile(r'</?(div|span|p)[^>]*>')
_bold_regex = re.compile(r'\*\*(.+?)\*\*|__(.+?)__')
_italic_regex = re.compile(r'\*(.+?)\*|_(.+?)_')

@functools.lru_cache(maxsize=128)
def escape_html_preserve_markdown(text: str) -> str:
    """Escape HTML while preserving markdown formatting.
    
    Args:
        text (str): Text to escape
        
    Returns:
        str: Escaped text with preserved markdown
    """
    try:
        # Store code blocks temporarily
        code_blocks = []
        def save_code_block(match):
            code_blocks.append(match.group(0))
            return f"CODE_BLOCK_{len(code_blocks)-1}_PLACEHOLDER"
        
        # Save code blocks before processing
        processed = re.sub(_code_block_regex, save_code_block, text)
        
        # Replace HTML tags with their escaped versions
        processed = processed.replace('&', '&amp;')\
                           .replace('<', '<')\
                           .replace('>', '>')\
                           .replace('"', '"')\
                           .replace("'", '&#39;')
        
        # Clean up any remaining problematic tags
        processed = re.sub(_html_tag_regex, '', processed)
        
        # Restore code blocks with proper formatting
        def format_code_block(match):
            index = int(match.group(1))
            block = code_blocks[index]
            if block.startswith('```'):
                # Multi-line code block
                code_content = block[3:-3].strip()  # Remove ``` and trim
                language = code_content.split('\n')[0] if code_content else ''
                code = code_content[len(language):].strip() if language else code_content
                return f'''<div style="background-color: {CODE_BLOCK_STYLE['bg_color']}; border: 1px solid {CODE_BLOCK_STYLE['border_color']}; border-radius: 4px; margin: 8px 0; padding: 8px 12px; font-family: monospace; white-space: pre-wrap; color: {CODE_BLOCK_STYLE['text_color']};"><code class="language-{language}">{html.escape(code)}</code></div>'''
            else:
                # Inline code
                code = block[1:-1]  # Remove backticks
                return f'<code style="background-color: {CODE_BLOCK_STYLE["bg_color"]}; padding: 2px 4px; border-radius: 3px; font-family: monospace;">{html.escape(code)}</code>'
        
        processed = re.sub(r'CODE_BLOCK_(\d+)_PLACEHOLDER', format_code_block, processed)
        
        # Handle other markdown elements (bold, italic, etc.)
        processed = re.sub(_bold_regex, r'<strong>\1\2</strong>', processed)  # Bold
        processed = re.sub(_italic_regex, r'<em>\1\2</em>', processed)  # Italic
        
        return processed
    except Exception as e:
        return f'Error processing message content: {str(e)}'

def format_timestamp(timestamp) -> str:
    """Format Unix timestamp to human-readable datetime string."""
    try:
        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp/1000).strftime(DATETIME_FORMAT)
        return timestamp
    except:
        return 'N/A'

def fetch_conversation_data(conversation_id: str) -> tuple:
    """Fetch conversation data from MongoDB."""
    try:
        if not isinstance(conversation_id, str):
            raise ValueError(f"Invalid conversation ID: {conversation_id}. Please provide a single conversation ID as a string.")
        
        app_db = get_database("muse-application")
        feedback_db = get_database("muse-assistant-feedback")
        
        # Get conversation details
        conversation_details = app_db.conversations.find_one({
            "$or": [{"id": conversation_id}, {"conversation_id": conversation_id}]
        })
        
        if not conversation_details:
            st.warning(f"Debug: Could not find conversation with id: {conversation_id}")
            st.warning(f"Available collections: {', '.join(app_db.list_collection_names())}")
            return None, None, None, None
        
        # Get analytics data
        analytics_data = feedback_db.analytics.find_one({"conversation_id": conversation_id})
        if not analytics_data:
            return None, None, None, None
        
        # Get context entries
        context_entries = []
        messages = analytics_data.get("message_history", [])
        context_ids = {msg.get("context_id") for msg in messages if msg.get("context_id")}
        
        if context_ids:
            # Convert set to list for MongoDB query
            context_ids_list = list(context_ids)
            context_entries = list(app_db.context.find(
                {"id": {"$in": context_ids_list}},
                projection={"_id": 0, "id": 1, "data": 1, "timestamp": 1}
            ))
        
        return conversation_details, analytics_data, context_entries, messages
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None, None, None, None

#############################
# Display Helper Functions #
#############################

def get_sentiment_widget(sentiment: str) -> str:
    """Generate HTML for sentiment indicator widget using emojis.
    
    Args:
        sentiment (str): Sentiment value ('positive', 'neutral', or 'negative')
        
    Returns:
        str: HTML string for sentiment widget
    """
    sentiment_emojis = {
        'positive': '😊',
        'neutral': '😐',
        'negative': '😔'
    }
    emoji = sentiment_emojis.get(sentiment, sentiment_emojis['neutral'])
    return emoji

def format_topic_capsule(topic: str) -> str:
    """Format a single topic as a capsule.
    
    Args:
        topic (str): Topic to format
        
    Returns:
        str: HTML string for topic capsule
    """
    return f'<span style="background-color: {TOPIC_CAPSULE_STYLE["bg_color"]}; color: {TOPIC_CAPSULE_STYLE["text_color"]}; padding: {TOPIC_CAPSULE_STYLE["padding"]}; border-radius: {TOPIC_CAPSULE_STYLE["border_radius"]}; border: 1px solid {TOPIC_CAPSULE_STYLE["border_color"]}; margin: {TOPIC_CAPSULE_STYLE["margin"]};">{topic}</span>'

def get_unity_topics_widget(topics: list) -> str:
    """Generate HTML for Unity topics widget.
    
    Args:
        topics (list): List of Unity topics
        
    Returns:
        str: HTML string for Unity topics widget
    """
    if not topics:
        return ''
    
    formatted_topics = [format_topic_capsule(topic) for topic in topics]
    return f'🎮 {" ".join(formatted_topics)}'

def get_external_knowledge_widget(classification: dict) -> str:
    """Generate HTML for external knowledge widget with tooltip.
    
    Args:
        classification (dict): Classification data containing external_knowledge
        
    Returns:
        str: HTML string for external knowledge widget
    """
    knowledge_level = classification.get('external_knowledge', 'none')
    knowledge_emojis = {
        'none': '📝',
        'intermediate': '📚',
        'advanced': '🎓'
    }
    emoji = knowledge_emojis.get(knowledge_level, knowledge_emojis['none'])
    return f'{emoji} {knowledge_level}'

def display_message(item: dict, item_type: str = 'message') -> None:
    """Display a message or context with appropriate styling.
    
    Args:
        item (dict): Message or context data to display
        item_type (str): Type of item ('message' or 'context')
    """
    if item_type == 'message':
        role = item.get('role', 'unknown').lower()
        content = item.get('content', 'No content')
        timestamp = format_timestamp(item.get('timestamp', 'N/A'))
        colors = USER_COLORS if role == 'user' else ASSISTANT_COLORS
        
        # Get sentiment, Unity topics, and external knowledge from front_desk_classification_results
        classification = item.get('front_desk_classification_results', {})
        sentiment = classification.get('sentiment', 'neutral').lower()
        unity_topics = classification.get('unity_topics', [])
        
        sentiment_widget = get_sentiment_widget(sentiment)
        unity_topics_widget = get_unity_topics_widget(unity_topics)
        external_knowledge_widget = get_external_knowledge_widget(classification)
        
        # Create single-line header with all elements
        header_html = f"{colors['icon']} {role.title()} | {sentiment_widget} {unity_topics_widget} | {external_knowledge_widget} | {timestamp}"
        
        message_html = f"""<div style="background-color: {colors['bg_color']}; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid {colors['border_color']}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"><div style="margin-bottom: 8px; color: {colors['header_color']}; font-weight: 500;">{header_html}</div><div style="color: {colors['text_color']}; background-color: {colors['content_bg']}; padding: 10px; border-radius: 5px;">{escape_html_preserve_markdown(content)}</div></div>"""
        
        st.markdown(message_html, unsafe_allow_html=True)
    else:  # context
        timestamp = format_timestamp(item.get('timestamp', 'N/A'))
        colors = CONTEXT_COLORS
        
        context_html = f"""<div style="background-color: {colors['bg_color']}; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid {colors['border_color']}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"><div style="margin-bottom: 8px; color: {colors['header_color']}; font-weight: 500;"><strong>{colors['icon']} Context Used</strong> | {timestamp}</div><details><summary style="color: {colors['header_color']}; font-weight: 500; cursor: pointer; padding: 5px;">View Context Data</summary><div style="color: {colors['text_color']}; margin-top: 10px; padding: 10px; border-radius: 5px; background-color: {colors['content_bg']};">{escape_html_preserve_markdown(str(item.get('data', 'No data available')))}</div></details></div>"""
        
        st.markdown(context_html, unsafe_allow_html=True)

def display_conversation_overview(conversation_details: dict, messages: list):
    """Display conversation overview in columns."""
    if not conversation_details:
        st.warning("No conversation details found")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("💭 Overview")
        st.write("ID:", conversation_details.get('id', conversation_details.get('conversation_id', 'Unknown')))
        st.write("Schema:", "v2" if 'history' in conversation_details else 
                          "v1" if 'message_history' in conversation_details else "Unknown")
        
        for field in ['created', 'updated']:
            if value := conversation_details.get(field):
                st.write(f"{field.capitalize()}:", format_timestamp(value))

    with col2:
        st.subheader("📊 Message Statistics")
        if messages:
            # Message counts by role
            role_counts = {}
            sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
            complexity_counts = {'none': 0, 'intermediate': 0, 'advanced': 0}
        
            for msg in messages:
                # Count by role
                role = msg.get('role', 'unknown').lower()
                role_counts[role] = role_counts.get(role, 0) + 1
                
                # Only count sentiment and complexity for user messages
                if role == 'user':
                    classification = msg.get('front_desk_classification_results', {})
                    sentiment = classification.get('sentiment', 'neutral').lower()
                    sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
                    
                    knowledge_level = classification.get('external_knowledge', 'none')
                    complexity_counts[knowledge_level] = complexity_counts.get(knowledge_level, 0) + 1
        
            # Display message counts in a compact format
            st.write(f"Total: {len(messages)} | User: {role_counts.get('user', 0)} | Assistant: {role_counts.get('assistant', 0)} | Other: {sum(role_counts.values()) - role_counts.get('user', 0) - role_counts.get('assistant', 0)}")
            
            # Display sentiment analysis
            st.write(f"Sentiment: 😊 Positive: {sentiment_counts['positive']} | 😐 Neutral: {sentiment_counts['neutral']} | 😔 Negative: {sentiment_counts['negative']}")
            
            # Display complexity analysis
            st.write(f"Complexity: 📝 Basic: {complexity_counts['none']} | 📚 Intermediate: {complexity_counts['intermediate']} | 🎓 Advanced: {complexity_counts['advanced']}")
            
        else:
            st.write("No messages found")

    with col3:
        st.subheader("🏷️ Metadata")
        first_msg = messages[0] if messages else {}
        
        # Display status indicators
        for status, (field, check) in {
            'Internal Unity': ('is_internal_unity', bool),
            'OPT Status': ('opt_status', lambda x: x.lower() == 'in')
        }.items():
            value = first_msg.get(field, False)
            st.write(f"{status}:", "✅" if (value and check(value)) else "❌")

        # Display classification data
        if messages:
            # Get language from first message
            if class_data := first_msg.get('front_desk_classification_results', {}):
                if lang := class_data.get('user_language'):
                    # Get flag emoji for the language
                    flag = LANGUAGE_FLAGS.get(lang.lower(), LANGUAGE_FLAGS['unknown'])
                    st.write("Language:", f"{flag} {lang}")
            
            # Collect all unique topics from all messages
            all_topics = set()
            for msg in messages:
                if class_data := msg.get('front_desk_classification_results', {}):
                    if topics := class_data.get('unity_topics'):
                        all_topics.update(topics)
            
            if all_topics:
                topics_html = " ".join([format_topic_capsule(topic) for topic in sorted(all_topics)])
                st.markdown(f"Topics: {topics_html}", unsafe_allow_html=True)

def display_formatted_conversation(conversation: dict, contexts: list, messages: list) -> None:
    """Display conversation data in a formatted, user-friendly way."""
    display_conversation_overview(conversation, messages)
    
    if messages:
        st.subheader("💬 Message History")
        
        # Create a dictionary of contexts indexed by their IDs
        context_dict = {ctx['id']: ctx for ctx in contexts}
        
        # Sort messages by timestamp
        timeline = []
        for msg in messages:
            timeline.append(('message', msg.get('timestamp', 0), msg))
            # If message has context, add it to timeline
            if msg.get('context_id') and msg.get('context_id') in context_dict:
                timeline.append(('context', msg.get('timestamp', 0), context_dict[msg.get('context_id')]))
        
        # Sort timeline by timestamp
        timeline.sort(key=lambda x: x[1])
        
        # Display items in chronological order
        for item_type, _, item in timeline:
            display_message(item, item_type)
    else:
        st.warning("No messages found in the conversation")

####################
# Main Application #
####################

def main():
    """Main application entry point."""
    st.set_page_config(layout="wide")
    st.markdown("<h1 style='text-align: center'>🔍 Assistant Conversation Visualizer</h1>", unsafe_allow_html=True)
    
    # Center the input form
    _, col2, _ = st.columns([3, 2, 3])
    with col2:
        with st.form("conversation_form", clear_on_submit=False):
            conversation_id = st.text_input("Enter Conversation ID")
            submit_button = st.form_submit_button("Load")
    
    if submit_button and conversation_id:
        print(f"Raw input: {conversation_id}") # Added print statement
        with st.spinner('Loading conversation data...'):
            conversation_details, analytics_data, contexts, messages = fetch_conversation_data(conversation_id)
            
            if analytics_data:
                # Create tabs for raw and formatted data
                tab1, tab2 = st.tabs(["Raw Data", "Formatted View"])
                
                with tab1:
                    # Add some padding for the results
                    st.markdown("<div style='padding: 0 2rem'>", unsafe_allow_html=True)
                    
                    # Create three columns with proper spacing
                    col1, col2, col3 = st.columns([1, 1, 1], gap="large")
                    
                    # Column 1: Conversation Details from muse-application
                    with col1:
                        st.header("Conversation Details")
                        if conversation_details:
                            st.json(conversation_details)
                        else:
                            st.info("No conversation details found in muse-application")
                    
                    # Column 2: Context Entries
                    with col2:
                        st.header("Context Entries")
                        if contexts:
                            for i, context in enumerate(contexts, 1):
                                st.subheader(f"Context Entry {i}")
                                st.json(context)
                        else:
                            st.info("No context entries found")
                    
                    # Column 3: Message History from analytics
                    with col3:
                        st.header("Message History")
                        if messages:
                            st.json(analytics_data)
                        else:
                            st.info("No messages found")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with tab2:
                    display_formatted_conversation(conversation_details or {}, contexts, messages)
            else:
                st.error("No conversation found with this ID")

if __name__ == "__main__":
    main()
