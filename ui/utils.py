import streamlit as st
import firebase_admin
from firebase_admin import credentials

def setup(tabname):
    st.set_page_config(layout="wide", page_icon="🤖", page_title=tabname)
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/modules.py", label="Modules", icon="📚")
    st.sidebar.page_link("pages/chatbot.py", label="Chatbot", icon="🗨️")
    st.sidebar.page_link("pages/admin.py", label="Admin Panel", icon="⚙️")

def get_all_document_ids(db, collection_name):
    try:
        collection_ref = db.collection(collection_name)
        docs = collection_ref.stream()
        return [doc.id for doc in docs]
    except Exception as e:
        return f"Error retrieving document IDs: {str(e)}"
    
@st.cache_resource
def init_firebase():
    cred = credentials.Certificate(dict(st.secrets["firebase"]["proj_settings"]))
    print(cred)
    return firebase_admin.initialize_app(cred)