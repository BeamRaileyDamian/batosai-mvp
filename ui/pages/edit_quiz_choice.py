import streamlit as st
import firebase_admin
from utils import *
from firebase_admin import firestore

def main():
    if not firebase_admin._apps:
        init_firebase()
    db = firestore.client()

    if "lect_ids" not in st.session_state: st.session_state.lect_ids = get_all_document_ids(db, "lect_scripts")
    if "lect_script_to_edit" not in st.session_state: st.session_state.lect_script_to_edit = None
    if "lect_to_edit" not in st.session_state: st.session_state.lect_to_edit = None

    setup("Edit Quiz")
    st.title("Edit Quiz")

    if st.session_state.lect_ids:
        for id in st.session_state.lect_ids:
            if st.button(id):
                st.session_state.lect_to_edit = id

                doc_ref = db.collection("lect_scripts").document(id)
                doc = doc_ref.get()
                if doc.exists:
                    st.session_state.lect_script_to_edit = doc.to_dict()

                st.switch_page("pages/edit_quiz.py")
    else:
        st.info("No lectures to display.")

if __name__ == "__main__":
    main()