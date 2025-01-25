from utils import *
import firebase_admin
import streamlit as st
from firebase_admin import credentials, firestore

setup("bat.OS.AI")
st.title("Welcome to bat.OS.AI! :robot_face:")

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
if "lect_ids" not in st.session_state:
    st.session_state.lect_ids = get_all_document_ids("lect_scripts")

st.markdown(
    """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et 
    dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip 
    ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu 
    fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt 
    mollit anim id est laborum
"""
)