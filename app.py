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

def escape_html_preserve_markdown(text: str) -> str:
    """Escape HTML while preserving markdown formatting.
    
    Args:
        text (str): Text to escape
        
    Returns:
        str: Escaped text with preserved markdown
    """
    try:
        # Replace HTML tags with their escaped versions, except for markdown-related tags
        escaped = text.replace('&', '&amp;')\
                     .replace('<', '&lt;')\
                     .replace('>', '&gt;')\
                     .replace('"', '&quot;')\
                     .replace("'", '&#39;')
        
        # Remove any remaining HTML-like tags that might break the layout
        escaped = re.sub(r'</div>', '', escaped)
        escaped = re.sub(r'<div[^>]*>', '', escaped)
        
        return escaped
    except:
        return 'Error processing message content'

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

def display_conversation_overview(conversation_details: dict, messages: list):
    """Display conversation overview in columns."""
    if not conversation_details:
        st.warning("No conversation details found in muse-application")
        return

    # Create three columns for better organization
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("💭 Overview")
        # Use get() with default values to handle missing fields
        st.write("ID:", conversation_details.get('id', conversation_details.get('conversation_id', 'Unknown')))
        
        # Get schema version from the document structure
        if 'history' in conversation_details:
            st.write("Schema:", "v2")  # New schema with 'history' field
        elif 'message_history' in conversation_details:
            st.write("Schema:", "v1")  # Old schema with 'message_history' field
        else:
            st.write("Schema:", "Unknown")
        
        # Format timestamps if they exist
        created = conversation_details.get('created')
        if created:
            st.write("Created:", format_timestamp(created))
        
        updated = conversation_details.get('updated')
        if updated:
            st.write("Updated:", format_timestamp(updated))

    with col2:
        st.subheader("📊 Statistics")
        if messages:
            # Count messages by role from the messages list
            role_counts = {}
            for msg in messages:
                role = msg.get('role', 'unknown').lower()
                role_counts[role] = role_counts.get(role, 0) + 1
            
            st.metric("Total Messages", len(messages))
            st.metric("User Messages", role_counts.get('user', 0))
            st.metric("Assistant Messages", role_counts.get('assistant', 0))
        else:
            st.write("No messages found")

    with col3:
        st.subheader("🏷️ Metadata")
        # Use emoji for internal unity status
        first_msg = messages[0] if messages else {}
        is_internal = first_msg.get('is_internal_unity', False)
        internal_emoji = "✅" if is_internal else "❌"
        st.write("Internal Unity:", internal_emoji)
        
        # Use emoji for opt status
        opt_status = first_msg.get('opt_status', '')
        opt_emoji = "✅" if opt_status.lower() == 'in' else "❌"
        st.write("OPT Status:", opt_emoji)
        
        # Display language and topics if available
        if first_msg.get('front_desk_classification_results'):
            classification = first_msg['front_desk_classification_results']
            if 'user_language' in classification:
                st.write("Language:", classification['user_language'])
            if 'unity_topics' in classification:
                st.write("Topics:", ", ".join(classification['unity_topics']))

def display_formatted_conversation(conversation: dict, contexts: list, messages: list) -> None:
    """Display conversation data in a formatted, user-friendly way.
    
    Args:
        conversation (dict): Conversation metadata and details
        contexts (list): List of context entries (deprecated)
        messages (list): List of conversation messages
    """
    # Display conversation overview with all details
    display_conversation_overview(conversation, messages)
    
    # Display message history
    if messages:
        st.subheader("💬 Message History")
        for msg in messages:
            display_message(msg)
    else:
        st.warning("No messages found in the conversation")

def display_message(msg: dict) -> None:
    """Display a single message with appropriate styling.
    
    Args:
        msg (dict): Message data to display
    """
    role = msg.get('role', 'unknown').lower()
    content = msg.get('content', 'No content')
    timestamp = format_timestamp(msg.get('timestamp', 'N/A'))
    
    # Determine message style based on role
    if role == 'user':
        st.markdown(f"""
            <div style="
                background-color: #e3f2fd;
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 5px solid #1976d2;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <div style="
                    margin-bottom: 8px;
                    color: #1976d2;
                    font-weight: 500;
                ">
                    <strong>👤 User</strong> • {timestamp}
                </div>
                <div style="
                    color: #1565c0;
                    background-color: rgba(25, 118, 210, 0.05);
                    padding: 10px;
                    border-radius: 5px;
                ">
                    {escape_html_preserve_markdown(content)}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="
                background-color: #e8f5e9;
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 5px solid #2e7d32;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <div style="
                    margin-bottom: 8px;
                    color: #2e7d32;
                    font-weight: 500;
                ">
                    <strong>🤖 Assistant</strong> • {timestamp}
                </div>
                <div style="
                    color: #1b5e20;
                    background-color: rgba(46, 125, 50, 0.05);
                    padding: 10px;
                    border-radius: 5px;
                ">
                    {escape_html_preserve_markdown(content)}
                </div>
            </div>
        """, unsafe_allow_html=True)

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
