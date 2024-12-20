import streamlit as st

st.set_page_config(
    page_title="AI Assistant Conversation Dashboard",
    page_icon="💬",
    layout="wide"
)

# Center the main title
st.markdown("<h1 style='text-align: center'>AI Assistant Conversation Dashboard 💬</h1>", unsafe_allow_html=True)

# Use columns to center content
_, center_col, _ = st.columns([1, 2, 1])

with center_col:
    st.markdown("## Welcome to the AI Assistant Conversation Dashboard!")
    
    st.markdown("""
        This application is designed to help you access and analyze conversation data
        from the AI Assistant tool at Unity Technologies.
    """)
    
    st.markdown("### What you can do:")
    
    st.markdown("""
        ✨ View conversation histories  
        🔍 Query the conversation database  
        📊 Analyze AI Assistant interactions
    """)
    
    st.markdown("---")
    
    st.markdown("### 👈 Select a page from the sidebar to get started!")
