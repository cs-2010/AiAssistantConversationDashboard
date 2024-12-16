"""
Main application file for the AI Assistant Conversation Dashboard.
"""

import streamlit as st
from .database import fetch_conversation_data
from .display import display_formatted_conversation

# Must be the first Streamlit command
st.set_page_config(
    page_title="AI Assistant Conversation Dashboard",
    page_icon="🤖",
    layout="wide"
)

def main():
    """Main application entry point."""
    st.title("🤖 AI Assistant Conversation Dashboard")
    
    
    # Input field for conversation ID
    conversation_id = st.text_input(
        "Enter Conversation ID",
        help="Enter the ID of the conversation you want to analyze"
    )
    
    if conversation_id:
        try:
            # Fetch conversation data
            with st.spinner("Fetching conversation data..."):
                conversation_details, analytics_data, contexts, messages = fetch_conversation_data(conversation_id)
            
            # Debug information
            with st.expander("Debug Information"):
                st.write("Debug Info:")
                st.write(f"- Conversation details found: {conversation_details is not None}")
                st.write(f"- Number of contexts: {len(contexts)}")
                st.write(f"- Number of messages: {len(messages)}")
            
            # Display formatted conversation
            display_formatted_conversation(conversation_details, contexts, messages)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.info("Please enter a conversation ID to view the details")

if __name__ == "__main__":
    main()
