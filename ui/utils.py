import streamlit as st

def set_sidebar():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/modules.py", label="Modules", icon="📚")
    st.sidebar.page_link("pages/admin.py", label="Admin Panel", icon="⚙️")