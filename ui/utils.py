import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

def setup(tabname):
    st.set_page_config(layout="wide", page_icon="🤖", page_title=tabname, menu_items={"About": "### Beam Damian - CMSC 190 ", "Report a Bug": "mailto:bmdamian@up.edu.ph", "Get help": "mailto:bmdamian@up.edu.ph"})
    st.logo("assets/sidebar_logo.png", icon_image="assets/main_logo.png", size="large")
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/modules.py", label="Lessons", icon="🧑‍🏫")
    st.sidebar.page_link("pages/materials.py", label="Materials", icon="📚")
    st.sidebar.page_link("pages/chatbot.py", label="Chatbot", icon="🗨️")
    st.sidebar.page_link("pages/admin.py", label="Admin Panel", icon="⚙️")

def get_all_document_ids(db, collection_name):
    try:
        collection_ref = db.collection(collection_name)
        docs = collection_ref.stream()
        return [doc.id for doc in docs]
    except Exception as e:
        return f"Error retrieving document IDs: {str(e)}"

def fetch_lect_ids():
    if "db" not in st.session_state:
        if not firebase_admin._apps:
            init_firebase()
        db = firestore.client()
        st.session_state.db = db

    if "lect_ids" not in st.session_state: st.session_state.lect_ids = get_all_document_ids(st.session_state.db, "lect_scripts")

def sort_lectures(lect_id, module_numbers):
    lect_id.sort(key=lambda x: (
        x not in module_numbers,  # Prioritize items in module_numbers first
        module_numbers.get(x, float('inf')) if module_numbers.get(x) is not None else float('inf'),  # Handle None case
        x  # Lexicographic order for remaining
    ))

def fetch_module_numbers():
    if "db" not in st.session_state:
        if not firebase_admin._apps:
            init_firebase()
        db = firestore.client()
        st.session_state.db = db

    if "module_numbers" not in st.session_state:
        dict = {}
        try:
            collection_ref = st.session_state.db.collection("lect_scripts")
            docs = collection_ref.stream()
            for doc in docs:
                dict[doc.id] = doc.to_dict()["module_number"]
            st.session_state.module_numbers = dict
        except Exception as e:
            return f"Error retrieving document IDs: {str(e)}"

def button_styles():
    st.markdown("""
    <style>
    div.stButton > button {
        width: 420px !important;
        display: flex !important;
        justify-content: flex-start !important;
        text-align: left !important;
        white-space: normal !important; /* Allows text wrapping */
        word-wrap: break-word !important; /* Ensures long words wrap */
        overflow-wrap: break-word !important; /* Alternative wrapping method */
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def init_firebase():
    cred = credentials.Certificate(dict(st.secrets["firebase"]["proj_settings"]))
    return firebase_admin.initialize_app(cred)