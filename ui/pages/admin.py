from utils import *
import firebase_admin
import streamlit as st
from firebase_admin import credentials, firestore

setup("Admin Panel")
st.title("Admin Panel")

# Initialize Firebase
if not firebase_admin._apps:  # Ensure Firebase isn't initialized multiple times
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

if "lect_ids" not in st.session_state: st.session_state.lect_ids = get_all_document_ids(db, "lect_scripts")

if st.button("Create a Lecture"): st.switch_page("pages/create_lect.py")
if st.button("Delete a Lecture"): st.switch_page("pages/delete_lect.py")