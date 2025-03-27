import streamlit as st
from utils import *

def main():
    fetch_lect_ids()
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

                    doc_ref = st.session_state.db.collection("lect_scripts").document(id)
                    doc = doc_ref.get()
                    if doc.exists:
                        st.session_state.lect_script = doc.to_dict()

                st.switch_page("pages/lesson.py")
    else:
        st.info("No lectures to display.")

if __name__ == "__main__":
    main()