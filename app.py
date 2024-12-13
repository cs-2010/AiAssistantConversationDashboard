# Standard library imports
import os
from datetime import datetime
from pathlib import Path

# Third-party imports
import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import html
import re

# Constants
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_MONGO_TIMEOUT = 30000

def get_mongodb_uri() -> str:
    """Retrieve MongoDB URI from environment variables.

    Returns:
        str: MongoDB connection URI

    Raises:
        ValueError: If MONGO_URI environment variable is not set
    """
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise ValueError("MONGO_URI environment variable is not set. Please check your .env file.")
    return str(uri).strip()

# Initialize MongoDB client with connection options
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
    """Get a MongoDB database instance.

    Args:
        database_name (str): Name of the database to connect to

    Returns:
        Database: MongoDB database object
    """
    return client[database_name]

def fetch_conversation_data(conversation_id: str) -> tuple:
    """Fetch conversation data, contexts, and messages from MongoDB.

    Args:
        conversation_id (str): Unique identifier for the conversation

    Returns:
        tuple: (conversation_details, analytics_data, context_entries, messages) or (None, None, None, None) if not found
    """
    try:
        # Access databases
        app_db = get_database("muse-application")
        feedback_db = get_database("muse-assistant-feedback")
        
        # Get conversation details from muse-application
        # Try both id and conversation_id fields
        conversation_details = app_db.conversations.find_one({
            "$or": [
                {"id": conversation_id},
                {"conversation_id": conversation_id}
            ]
        })
        
        # Debug information
        if not conversation_details:
            st.warning(f"Debug: Could not find conversation in muse-application.conversations with id: {conversation_id}")
            # List available collections in muse-application
            collections = app_db.list_collection_names()
            st.warning(f"Debug: Available collections in muse-application: {', '.join(collections)}")
        
        # Get analytics data from muse-assistant-feedback
        analytics_data = feedback_db.analytics.find_one({
            "conversation_id": conversation_id
        })
        
        if not analytics_data:
            return None, None, None, None
            
        # Get all context data for this conversation
        context_entries = []
        if "message_history" in analytics_data:
            context_ids = {msg["context_id"] for msg in analytics_data["message_history"] 
                         if msg.get("context_id")}
            
            # Fetch all unique context entries
            context_entries = [
                context_data for context_id in context_ids
                if (context_data := app_db.context.find_one({"id": context_id}))
            ]
        
        messages = analytics_data.get("message_history", [])
        return conversation_details, analytics_data, context_entries, messages
        
    except Exception as e:
        st.error(f"Error in fetch_conversation_data: {str(e)}")
        return None, None, None, None

def escape_html_preserve_markdown(content: str) -> str:
    """Escape HTML characters while preserving markdown formatting.

    Args:
        content (str): Raw content containing markdown and possibly HTML

    Returns:
        str: HTML-escaped content with preserved markdown formatting
    """
    if not content:
        return ""
        
    # Save markdown code blocks
    code_blocks = []
    def save_code_block(match):
        code_blocks.append(match.group(0))
        return f"CODE_BLOCK_{len(code_blocks)-1}_"
    
    # Save inline code
    inline_codes = []
    def save_inline_code(match):
        inline_codes.append(match.group(0))
        return f"INLINE_CODE_{len(inline_codes)-1}_"
    
    # First, escape any existing div tags or other HTML
    content = re.sub(r'</?\s*div[^>]*>', '', content)  # Remove div tags
    content = re.sub(r'<br\s*/?>', '\n', content)  # Convert <br> to newlines
    
    # Save code blocks and inline code
    content = re.sub(r'```[\s\S]*?```', save_code_block, content)
    content = re.sub(r'`[^`]+`', save_inline_code, content)
    
    # Escape HTML while preserving common markdown characters
    content = html.escape(content)
    
    # Restore code blocks and inline code
    for i, block in enumerate(code_blocks):
        content = content.replace(f"CODE_BLOCK_{i}_", block)
    for i, code in enumerate(inline_codes):
        content = content.replace(f"INLINE_CODE_{i}_", code)
    
    return content

def format_timestamp(timestamp) -> str:
    """Format Unix timestamp to human-readable datetime string.

    Args:
        timestamp: Unix timestamp in milliseconds or existing datetime string

    Returns:
        str: Formatted datetime string
    """
    try:
        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp/1000).strftime(DATETIME_FORMAT)
        return timestamp
    except:
        return 'N/A'

def display_formatted_conversation(conversation: dict, contexts: list, messages: list) -> None:
    """Display conversation data in a formatted, user-friendly way.

    Args:
        conversation (dict): Conversation metadata and details
        contexts (list): List of context entries
        messages (list): List of conversation messages
    """
    # Create three columns for Overview, Statistics, and Metadata
    overview_col, stats_col, meta_col = st.columns(3)
    
    # Conversation Overview
    with overview_col:
        st.subheader("💭 Overview")
        st.info(f"**ID:** {conversation.get('conversation_id', 'N/A')}")
        st.info(f"**Schema:** v{conversation.get('schema_version', 'N/A')}")
        
        # The timestamps might be in message_history[0] for the first message
        first_msg = messages[0] if messages else {}
        last_msg = messages[-1] if messages else {}
        
        created_time = (
            format_timestamp(first_msg.get('timestamp')) if first_msg 
            else format_timestamp(conversation.get('created_at', 'N/A'))
        )
        updated_time = (
            format_timestamp(last_msg.get('timestamp')) if last_msg 
            else format_timestamp(conversation.get('last_updated_timestamp', 'N/A'))
        )
        st.info(f"**Created:** {created_time}")
        st.info(f"**Updated:** {updated_time}")
        
        # Add Internal Unity and OPT status from the first message's metadata
        if first_msg:
            is_internal = "✅" if first_msg.get('is_internal_unity') else "❌"
            opt_status = first_msg.get('opt_status', 'N/A')
            st.info(f"**Internal Unity:** {is_internal}  \n**OPT Status:** {opt_status}")
    
    # Message Statistics
    with stats_col:
        st.subheader("📊 Statistics")
        if messages:
            # Count messages by role
            role_counts = {}
            for msg in messages:
                role = msg.get('role', 'unknown').lower()
                role_counts[role] = role_counts.get(role, 0) + 1
            
            st.metric("Total Messages", len(messages))
            st.metric("User Messages", role_counts.get('user', 0))
            st.metric("Assistant Messages", role_counts.get('assistant', 0))
        else:
            st.info("No messages available")
    
    # Conversation Metadata
    with meta_col:
        st.subheader("🏷️ Metadata")
        if messages:
            # Get the first message with classification results
            for msg in messages:
                if class_results := msg.get('front_desk_classification_results'):
                    st.info(f"**Language:** {class_results.get('user_language', 'N/A')}")
                    unity_topics = class_results.get('unity_topics', [])
                    if unity_topics:
                        st.info(f"**Topics:** {', '.join(unity_topics[:2])}{'...' if len(unity_topics) > 2 else ''}")
                    break
        else:
            st.info("No metadata available")
    
    # Message History (full width)
    if messages:
        st.markdown("---")  # Add a separator
        st.subheader("💬 Conversation")
        
        for msg in messages:
            role = msg.get('role', 'unknown').lower()
            content = msg.get('content', 'No content')
            timestamp = format_timestamp(msg.get('timestamp', 'N/A'))
            
            # Create message container based on role
            if role == 'user':
                # For user messages, escape HTML in content
                escaped_content = escape_html_preserve_markdown(content)
                st.markdown(f"""
                    <div class="user-message">
                        <div class="message-header">
                            👤 User • {timestamp}
                        </div>
                        <div class="message-content">
                            {escaped_content}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # For system messages, escape HTML but preserve markdown
                escaped_content = escape_html_preserve_markdown(content)
                st.markdown(f"""
                    <div class="system-message">
                        <div class="message-header">
                            🤖 Assistant • {timestamp}
                        </div>
                        <div class="message-content">
                            {escaped_content}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # Context Entries
    if contexts:
        st.subheader("📚 Context Entries")
        for i, context in enumerate(contexts, 1):
            with st.expander(f"Context Entry {i}"):
                if 'content' in context:
                    st.markdown(f"**Content:** {context['content']}")
                if 'metadata' in context:
                    st.markdown("**Metadata:**")
                    for key, value in context['metadata'].items():
                        st.markdown(f"- {key}: {value}")
                if 'embedding' in context:
                    st.markdown(f"**Embedding Size:** {len(context['embedding'])}")
    else:
        st.info("No context entries available")

def main():
    """Main application entry point."""
    # Set page config to wide mode
    st.set_page_config(layout="wide")
    
    # Add CSS for the formatted view tab
    st.markdown("""
        <style>
        /* Style for the formatted view tab */
        [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:has([role="tab"][aria-selected="true"]:contains("Formatted View")) {
            margin: 0 20% !important;
            max-width: 800px !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }
        
        /* Message styles */
        .user-message {
            background-color: #e8f4f9;
            padding: 15px;
            border-radius: 15px;
            margin: 10px 0;
            border-left: 5px solid #2196F3;
        }
        .system-message {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 15px;
            margin: 10px 0;
            border-left: 5px solid #4CAF50;
        }
        .message-header {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 8px;
        }
        .message-content {
            margin-top: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Centered title with emoji
    st.markdown("<h1 style='text-align: center'>🔍 Conversation Analytics Dashboard</h1>", unsafe_allow_html=True)
    
    # Center the input form
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        with st.form("conversation_form", clear_on_submit=False):
            conversation_id = st.text_input("Enter Conversation ID")
            submit_button = st.form_submit_button("Load")
    
    if submit_button and conversation_id:
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
