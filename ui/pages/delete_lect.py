import os
import shutil
from utils import *
import firebase_admin
import streamlit as st
from firebase_admin import firestore

def delete(collection_name, document_id):
    try:
        doc_ref = db.collection(collection_name).document(document_id)

        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
            return True
        else:
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if not firebase_admin._apps:
    init_firebase()
db = firestore.client()

setup("Delete a Lecture")
st.title("Delete a Lecture")

if st.session_state.lect_ids:
    for id in st.session_state.lect_ids:
        if st.button(id, key=id):
            to_delete = id
            result = delete("lect_scripts", id)
            
            if result:
                st.session_state.lect_ids.remove(id)
                st.rerun()
                # st.success("Lecture Successfully Deleted")
            else:
                st.success("Lecture Deletion Failed")
else:
    st.info("No lectures to display.")