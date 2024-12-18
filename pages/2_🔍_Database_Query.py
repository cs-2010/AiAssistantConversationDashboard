"""
Database Query page for searching conversations.
"""

import streamlit as st
from src.database import search_conversations
from datetime import datetime
import pandas as pd

def format_timestamp(ts):
    """Safely format a timestamp, returning 'N/A' if invalid"""
    try:
        if not ts:
            return "N/A"
        return datetime.fromtimestamp(ts / 1000.0).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError, OverflowError):
        return "N/A"

# Page config
st.set_page_config(page_title="Database Query", page_icon="🔍", layout="wide")
st.title("🔍 Search Conversations")

# Add some padding and styles
st.markdown("""
    <style>
        .block-container {
            padding-left: 2rem;
            padding-right: 2rem;
        }
        .stButton > button {
            margin-top: 1.7rem;
        }
    </style>
""", unsafe_allow_html=True)

# Search interface
with st.form("search_form"):
    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
    with col1:
        search_query = st.text_input("Search conversations by title", placeholder="Enter search term (e.g., 'flappy')")
    with col2:
        min_messages = st.number_input(label="Min messages", min_value=0, value=0, step=1)
    with col3:
        max_messages = st.number_input(label="Max messages", min_value=0, value=0, step=1)
    with col4:
        start_date = st.date_input(label="Start Date")
    with col5:
        end_date = st.date_input(label="End Date")
    
    search_button = st.form_submit_button("🔍 Search", use_container_width=True)

if 'skip' not in st.session_state:
    st.session_state.skip = 0
if 'all_results' not in st.session_state:
    st.session_state.all_results = []

if search_button:
    st.session_state.skip = 0
    st.session_state.all_results = []

if search_button or st.session_state.all_results:
    # Perform search
    results = search_conversations(search_query, min_messages, max_messages, limit=1000, skip=st.session_state.skip, start_date=start_date, end_date=end_date)
    
    if results:
        st.session_state.all_results.extend(results)
        st.write(f"Found {len(st.session_state.all_results)} conversations")
        
        # Convert data for dataframe display
        table_data = []
        for conv in st.session_state.all_results:
            table_data.append({
                "ID": conv["id"],
                "Title": conv["name"],
                "Messages": conv["message_count"],
                "First Message": conv["first_message"],
                "Last Message": conv["last_message"],
                "Created": format_timestamp(conv.get("created_at")),
                "Updated": format_timestamp(conv.get("updated_at")),
                "Owners": ", ".join(conv.get("owners", [])),
            })
        
        # Create DataFrame
        df = pd.DataFrame(table_data)
        
        # Display interactive dataframe
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "ID": st.column_config.TextColumn(
                    "ID",
                    help="Conversation ID",
                    width="medium",
                ),
                "Title": st.column_config.TextColumn(
                    "Title",
                    width="large",
                ),
                "Messages": st.column_config.NumberColumn(
                    "Messages",
                    help="Number of messages in the conversation",
                    width="small",
                ),
                "First Message": st.column_config.TextColumn(
                    "First Message",
                    help="Beginning of the conversation",
                    width="large",
                ),
                "Last Message": st.column_config.TextColumn(
                    "Last Message",
                    help="Most recent message",
                    width="large",
                ),
                "Created": st.column_config.TextColumn(
                    "Created",
                    help="When the conversation started",
                ),
                "Updated": st.column_config.TextColumn(
                    "Updated",
                    help="When the conversation was last updated",
                ),
                "Owners": st.column_config.TextColumn(
                    "Owners",
                    help="Users involved in the conversation",
                    width="medium",
                ),
            },
            hide_index=True,
            column_order=[
                "ID", "Title", "Messages",
                "First Message", "Last Message",
                "Created", "Updated", "Owners"
            ],
        )
        
        if len(results) == 1000:
            if st.button("Load More", use_container_width=True):
                st.session_state.skip += 1000
                st.rerun()
    else:
        st.info("No conversations found matching your search.")
