import streamlit as st
from pymongo import MongoClient
from pathlib import Path
from dotenv import load_dotenv
import os
import html
import re

# MongoDB connection setup
def get_mongodb_uri():
    """Get MongoDB URI from environment"""
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise ValueError("MONGO_URI environment variable is not set. Please check your .env file.")
    return str(uri).strip()

# MongoDB client with connection options
try:
    MONGO_URI = get_mongodb_uri()
    client = MongoClient(
        MONGO_URI,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000,
        serverSelectionTimeoutMS=30000,
        waitQueueTimeoutMS=30000,
        retryWrites=True,
        tls=True,
    )
except Exception as e:
    st.error(f"Error creating MongoDB client: {str(e)}")
    raise

def get_database(database_name: str):
    """Returns a MongoDB database object."""
    return client[database_name]

def fetch_conversation_data(conversation_id):
    try:
        # Access databases
        app_db = get_database("muse-application")
        feedback_db = get_database("muse-assistant-feedback")
        
        # Get data from analytics collection
        analytics_data = feedback_db.analytics.find_one({
            "conversation_id": conversation_id
        })
        
        if not analytics_data:
            return None, None, None
            
        # Get all context data for this conversation
        context_entries = []
        if "message_history" in analytics_data:
            context_ids = set()  # To avoid duplicates
            for message in analytics_data["message_history"]:
                if message.get("context_id"):
                    context_ids.add(message["context_id"])
            
            # Fetch all unique context entries
            for context_id in context_ids:
                context_data = app_db.context.find_one({"id": context_id})
                if context_data:
                    context_entries.append(context_data)
        
        # Get messages from the message history
        messages = analytics_data.get("message_history", [])
        
        return analytics_data, context_entries, messages
        
    except Exception as e:
        st.error(f"Error in fetch_conversation_data: {str(e)}")
        return None, None, None

def escape_html_preserve_markdown(content):
    """Escape HTML but preserve markdown formatting"""
    import re
    import html
    
    # Save markdown code blocks
    code_blocks = []
    def save_code_block(match):
        code_blocks.append(match.group(0))
        return f"CODE_BLOCK_{len(code_blocks)-1}_"
    
    content = re.sub(r'```[\s\S]*?```', save_code_block, content)
    
    # Save inline code
    inline_codes = []
    def save_inline_code(match):
        inline_codes.append(match.group(0))
        return f"INLINE_CODE_{len(inline_codes)-1}_"
    
    content = re.sub(r'`[^`]+`', save_inline_code, content)
    
    # Escape HTML
    content = html.escape(content)
    
    # Restore code blocks
    for i, block in enumerate(code_blocks):
        content = content.replace(f"CODE_BLOCK_{i}_", block)
    
    # Restore inline code
    for i, code in enumerate(inline_codes):
        content = content.replace(f"INLINE_CODE_{i}_", code)
    
    return content

def display_formatted_conversation(conversation, contexts, messages):
    """Display conversation data in a formatted, user-friendly way"""
    # Conversation Overview
    st.subheader("💬 Conversation Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**ID:** {conversation.get('conversation_id', 'N/A')}")
        st.info(f"**Status:** {conversation.get('status', 'N/A')}")
    with col2:
        st.info(f"**Created:** {conversation.get('created_at', 'N/A')}")
        st.info(f"**Updated:** {conversation.get('updated_at', 'N/A')}")

    # Message History
    if messages:
        st.subheader("💭 Conversation")
        
        for msg in messages:
            role = msg.get('role', 'unknown').lower()
            content = msg.get('content', 'No content')
            timestamp = msg.get('timestamp', 'N/A')
            
            # Format timestamp if it's a Unix timestamp
            try:
                if isinstance(timestamp, (int, float)):
                    from datetime import datetime
                    timestamp = datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass

            # Create message container based on role
            if role == 'user':
                # For user messages, escape HTML in content
                escaped_content = html.escape(content)
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
            conversation, contexts, messages = fetch_conversation_data(conversation_id)
            
            if conversation:
                # Create tabs for raw and formatted data
                tab1, tab2 = st.tabs(["Raw Data", "Formatted View"])
                
                with tab1:
                    # Add some padding for the results
                    st.markdown("<div style='padding: 0 2rem'>", unsafe_allow_html=True)
                    
                    # Create three columns with proper spacing
                    col1, col2, col3 = st.columns([1, 1, 1], gap="large")
                    
                    # Column 1: Conversation Details
                    with col1:
                        st.header("Conversation Details")
                        st.json(conversation)
                    
                    # Column 2: Context Entries
                    with col2:
                        st.header("Context Entries")
                        if contexts:
                            for i, context in enumerate(contexts, 1):
                                st.subheader(f"Context Entry {i}")
                                st.json(context)
                        else:
                            st.info("No context entries found")
                    
                    # Column 3: Message History
                    with col3:
                        st.header("Message History")
                        if messages:
                            for message in messages:
                                st.json(message)
                        else:
                            st.info("No messages found")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with tab2:
                    display_formatted_conversation(conversation, contexts, messages)
            else:
                st.error("No conversation found with this ID")

if __name__ == "__main__":
    main()