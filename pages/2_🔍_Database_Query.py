import streamlit as st

st.set_page_config(
    page_title="Database Query",
    page_icon="🔍",
    layout="wide"
)

def main():
    st.markdown("<h1 style='text-align: center'>🔍 Database Query</h1>", unsafe_allow_html=True)
    
    # Center the content
    st.markdown("<div style='text-align: center'>", unsafe_allow_html=True)
    st.write("This is the database query page.")
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
