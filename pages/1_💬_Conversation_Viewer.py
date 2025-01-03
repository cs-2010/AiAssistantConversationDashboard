"""
Main application file for the AI Assistant Conversation Dashboard.
"""

import streamlit as st
from src.database import fetch_conversation_data
from src.display import display_formatted_conversation
from src.llm import summarize_conversation_groq
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

st.set_page_config(
    page_title="Conversation Viewer",
    page_icon="💬",
    layout="wide"
)

if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = None
if 'conversation_data' not in st.session_state:
    st.session_state.conversation_data = None
if 'pm_analysis_started' not in st.session_state:
    st.session_state.pm_analysis_started = False

def start_analysis():
    st.session_state.pm_analysis_started = True

def stop_analysis():
    st.session_state.pm_analysis_started = False

def main():
    """Main application entry point."""
    st.markdown("<h1 style='text-align: center'>💬 Conversation Viewer</h1>", unsafe_allow_html=True)
    
    # Center the input form
    _, col2, _ = st.columns([3, 2, 3])
    with col2:
        with st.form("conversation_form", clear_on_submit=False):
            conversation_id = st.text_input("Enter Conversation ID", 
                                            value=st.session_state.get('conversation_id', ''))
            submit_button = st.form_submit_button("Load")
    
    # Check if conversation data is already loaded
    if st.session_state.conversation_data:
        conversation_details = st.session_state.conversation_data.get("conversation_details", {})
        analytics_data = st.session_state.conversation_data.get("analytics_data", {})
        contexts = st.session_state.conversation_data.get("contexts", [])
        messages = st.session_state.conversation_data.get("messages", [])
        
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
        
        # Handle PM Analysis button outside the tab to prevent reloads
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.session_state.pm_analysis_started:
                st.button("Stop AI Product Manager Analysis", on_click=stop_analysis, key="stop_button")
            else:
                st.button("Start AI Product Manager Analysis", on_click=start_analysis, key="start_button")
        
        with tab2:
            display_formatted_conversation(
                st.session_state.conversation_data["conversation_details"],
                st.session_state.conversation_data["contexts"],
                st.session_state.conversation_data["messages"],
                st.session_state.pm_analysis_started
            )
    
    # Load new conversation data if submit button is pressed
    if submit_button and conversation_id:
        with st.spinner('Loading conversation data...'):
            conversation_details, analytics_data, contexts, messages = fetch_conversation_data(conversation_id)
            
            if conversation_details or analytics_data:
                st.session_state.conversation_id = conversation_id
                st.session_state.conversation_data = {
                    "conversation_details": conversation_details,
                    "analytics_data": analytics_data,
                    "contexts": contexts,
                    "messages": messages
                }
                # Rerun to refresh the page with new data
                st.rerun()
            else:
                st.error("No conversation found with this ID")

if __name__ == "__main__":
    main()
