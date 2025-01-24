import streamlit as st
import firebase_admin
from utils import *
from firebase_admin import credentials, firestore

def get_all_document_ids(collection_name):
    try:
        collection_ref = db.collection(collection_name)
        docs = collection_ref.stream()
        return [doc.id for doc in docs]
    except Exception as e:
        return f"Error retrieving document IDs: {str(e)}"

# Initialize Firebase
if not firebase_admin._apps:  # Ensure Firebase isn't initialized multiple times
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

if "lect_ids" not in st.session_state: st.session_state.lect_ids = []

st.title("CMSC 125 Modules")
set_sidebar()

if not st.session_state.lect_ids:
    st.session_state.lect_ids = get_all_document_ids("lect_scripts")

if st.session_state.lect_ids:
    for id in st.session_state.lect_ids:
        st.button(id)
