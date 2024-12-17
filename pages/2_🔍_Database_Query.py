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
col1, col2 = st.columns([4, 1])
with col1:
    search_query = st.text_input("Search conversations by title", placeholder="Enter search term (e.g., 'flappy')")
with col2:
    search_button = st.button("🔍 Search", use_container_width=True)

if search_button and search_query:
    # Perform search
    results = search_conversations(search_query)
    
    if results:
        st.write(f"Found {len(results)} conversations")
        
        # Convert data for dataframe display
        table_data = []
        for conv in results:
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
    else:
        st.info("No conversations found matching your search.")
elif search_button:
    st.warning("Please enter a search term.")
