import streamlit as st

def setup(tabname):
    st.set_page_config(layout="wide", page_icon="🤖", page_title=tabname)
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/modules.py", label="Modules", icon="📚")
    st.sidebar.page_link("pages/admin.py", label="Admin Panel", icon="⚙️")