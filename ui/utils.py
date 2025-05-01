import streamlit as st
import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore

def setup(tabname):
    st.set_page_config(layout="wide", page_icon="🤖", page_title=tabname, menu_items={"About": "### Beam Damian - CMSC 190 ", "Report a Bug": "mailto:bmdamian@up.edu.ph", "Get help": "mailto:bmdamian@up.edu.ph"})
    global_styles()
    st.logo("assets/sidebar_logo.png", icon_image="assets/main_logo.png", size="large")
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/modules.py", label="Lessons", icon="🧑‍🏫")
    st.sidebar.page_link("pages/materials.py", label="Materials", icon="📚")
    st.sidebar.page_link("pages/chatbot.py", label="Chatbot", icon="🗨️")
    st.sidebar.page_link("pages/admin.py", label="Admin Panel", icon="⚙️")

def global_styles():
    st.markdown("""
    <style>
    <link href="https://fonts.googleapis.com/css2?family=Inter&display=swap" rel="stylesheet">
    p {
        font-family: 'Inter', serif !important;
        font-size: 13px !important;
        letter-spacing: 0.5px !important;
    }

    h2 {
        font-size: 20px !important;
        font-weight: bold;
    }
                
    div.stButton > button {
        background-color: #486f4f !important;
        color: white !important;
        padding: 10px 15px !important;
        border: 1px solid #284329 !important;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2) !important; 
    }

    div.stButton > button:hover {
        background-color: #59B75B !important;
    }
        
    .transcript-container {
        background-color: #f8f9fa;
        border-radius: 5px;
        color: #4b644c;
        padding: 2px;
        margin-top: 5px;
        font-size: 14px;
        border-left: 3px solid #4682b4;
        max-height: 425px;
        overflow-y: auto;
        position: relative;
    }

    .transcript-text {
        padding-bottom: 20px;
        animation-play-state: running;
    }
            
    .transcript-container:hover .transcript-text {
        animation-play-state: paused !important;
    }
            
    @keyframes autoscroll {
        0% { transform: translateY(0); }
        100% { transform: translateY(calc(-100% + 380px)); }
    }        
            
    .quiz-question {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #e0e0e0; /* Lighter text for green board */
    }
    .quiz-answer {
        font-size: 18px;
        color: white;
        margin-bottom: 20px;
        padding: 10px;
        background-color: #567257;
        border-left: 4px solid #59B75B;
        border-radius: 5px;
    }
    .timer {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
        padding: 10px;
        text-align: center;
        
        background-color: #59B75B !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #284329 !important;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2) !important; 
    }
    
    .green-board {
        background-color: #4b644c;
        background-size: 30px 30px;
        border-radius: 10px;
        padding: 20px;
        color: #e0e0e0;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.3);
        min-height: 400px;
    }
    
    .green-board h2 {
        color: #ffffff;
        margin-bottom: 20px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

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
        width: 35% !important;
        display: flex !important;
        justify-content: flex-start !important;
        text-align: left !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        background-color: #486f4f !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 15px !important;
        border: 1px solid #284329 !important;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2) !important; 
    }

    div.stButton > button:hover {
        background-color: #59B75B !important;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def init_firebase():
    cred = credentials.Certificate(dict(st.secrets["firebase"]["proj_settings"]))
    return firebase_admin.initialize_app(cred)