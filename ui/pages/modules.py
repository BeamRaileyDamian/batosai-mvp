import streamlit as st
import firebase_admin
from utils import *
from firebase_admin import firestore

def main():
    if not firebase_admin._apps:
        init_firebase()
    db = firestore.client()

    if "lect_ids" not in st.session_state: st.session_state.lect_ids = get_all_document_ids(db, "lect_scripts")
    if "lect_script" not in st.session_state: st.session_state.lect_script = None
    if "curr_lect" not in st.session_state: st.session_state.curr_lect = None
    if "curr_slide" not in st.session_state: st.session_state.curr_slide = 0

    setup("Lessons")
    st.title("CMSC 125 Lessons")

    if st.session_state.lect_ids:
        for id in st.session_state.lect_ids:
            if st.button(id):
                if st.session_state.curr_lect != id:
                    st.session_state.curr_lect = id
                    st.session_state.curr_slide = 0

                    doc_ref = db.collection("lect_scripts").document(id)
                    doc = doc_ref.get()
                    if doc.exists:
                        st.session_state.lect_script = doc.to_dict()

                st.switch_page("pages/lesson.py")
    else:
        st.info("No lectures to display.")

if __name__ == "__main__":
    main()