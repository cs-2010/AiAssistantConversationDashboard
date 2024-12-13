import streamlit as st
from pymongo import MongoClient
from pathlib import Path
from dotenv import load_dotenv
import os

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

def main():
    # Set page config to wide mode
    st.set_page_config(layout="wide")
    
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
                    st.info("Formatted view coming soon! 🚧")
            else:
                st.error("No conversation found with this ID")

if __name__ == "__main__":
    main()
