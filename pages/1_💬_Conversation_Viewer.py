"""
Main application file for the AI Assistant Conversation Dashboard.
"""

import streamlit as st
from src.database import fetch_conversation_data
from src.display import display_formatted_conversation

st.set_page_config(
    page_title="Conversation Viewer",
    page_icon="💬",
    layout="wide"
)

def main():
    """Main application entry point."""
    st.markdown("<h1 style='text-align: center'>💬 Conversation Viewer</h1>", unsafe_allow_html=True)
    
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
