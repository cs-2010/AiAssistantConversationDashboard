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

# Message templates for consistent styling
MESSAGE_TEMPLATE = """
    <div style="
        background-color: {bg_color};
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid {border_color};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <div style="
            margin-bottom: 8px;
            color: {header_color};
            font-weight: 500;
        ">
            <strong>{icon} {role}</strong> • {timestamp}
        </div>
        <div style="
            color: {text_color};
            background-color: {content_bg};
            padding: 10px;
            border-radius: 5px;
        ">
            {content}
        </div>
    </div>
"""

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
        
        # Remove any remaining HTML tags that might break the layout
        escaped = re.sub(r'</?(div|details|summary)[^>]*>', '', escaped)
        
        return escaped
    except:
        return 'Error processing message content'

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
            for context_id in context_ids:
                context = app_db.context.find_one({"id": context_id})
                if context:
                    context_entries.append(context)
        
        return conversation_details, analytics_data, context_entries, messages
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None, None, None, None

def display_message(msg: dict) -> None:
    """Display a single message with appropriate styling."""
    role = msg.get('role', 'unknown').lower()
    content = msg.get('content', 'No content')
    timestamp = format_timestamp(msg.get('timestamp', 'N/A'))
    
    # Select color scheme based on role
    colors = USER_COLORS if role == 'user' else ASSISTANT_COLORS
    
    # Render message using template
    st.markdown(
        MESSAGE_TEMPLATE.format(
            role=role.capitalize(),
            content=escape_html_preserve_markdown(content),
            timestamp=timestamp,
            **colors
        ),
        unsafe_allow_html=True
    )

def display_context(context: dict, timestamp: int) -> None:
    """Display a context entry with appropriate styling.
    
    Args:
        context (dict): Context data to display
        timestamp (int): Timestamp when the context was used
    """
    st.markdown(f"""
        <div style="
            background-color: #f3e5f5;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 5px solid #9c27b0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="
                margin-bottom: 8px;
                color: #9c27b0;
                font-weight: 500;
            ">
                <strong>🔍 Context Used</strong> • {format_timestamp(timestamp)}
            </div>
            <details>
                <summary style="
                    color: #9c27b0;
                    font-weight: 500;
                    cursor: pointer;
                    padding: 5px;
                ">
                    View Context Data
                </summary>
                <div style="
                    color: #6a1b9a;
                    margin-top: 10px;
                    padding: 10px;
                    border-radius: 5px;
                    background-color: rgba(156, 39, 176, 0.05);
                ">
                    {escape_html_preserve_markdown(str(context.get('data', 'No data available')))}
                </div>
            </details>
        </div>
    """, unsafe_allow_html=True)

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
        st.subheader("📊 Statistics")
        if messages:
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
        first_msg = messages[0] if messages else {}
        
        # Display status indicators
        for status, (field, check) in {
            'Internal Unity': ('is_internal_unity', bool),
            'OPT Status': ('opt_status', lambda x: x.lower() == 'in')
        }.items():
            value = first_msg.get(field, False)
            st.write(f"{status}:", "✅" if (value and check(value)) else "❌")

        # Display classification data
        if class_data := first_msg.get('front_desk_classification_results', {}):
            if lang := class_data.get('user_language'):
                st.write("Language:", lang)
            if topics := class_data.get('unity_topics'):
                st.write("Topics:", ", ".join(topics))

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
        for item_type, timestamp, item in timeline:
            if item_type == 'message':
                display_message(item)
            else:
                display_context(item, timestamp)
    else:
        st.warning("No messages found in the conversation")

def main():
    """Main application entry point."""
    st.set_page_config(layout="wide")
    st.markdown("<h1 style='text-align: center'>🔍 Conversation Analytics Dashboard</h1>", unsafe_allow_html=True)
    
    # Center the input form
    _, col2, _ = st.columns([3, 2, 3])
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
