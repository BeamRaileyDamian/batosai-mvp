import streamlit as st
from utils import *

def main():
    fetch_lect_ids()
    if "lect_script_to_edit" not in st.session_state: st.session_state.lect_script_to_edit = None
    if "lect_to_edit" not in st.session_state: st.session_state.lect_to_edit = None

    setup("Edit Quiz")
    st.title("Edit Quiz")

    if st.session_state.lect_ids:
        for id in st.session_state.lect_ids:
            if st.button(id):
                st.session_state.lect_to_edit = id

                doc_ref = st.session_state.db.collection("lect_scripts").document(id)
                doc = doc_ref.get()
                if doc.exists:
                    st.session_state.lect_script_to_edit = doc.to_dict()

                st.switch_page("pages/edit_quiz.py")
    else:
        st.info("No lectures to display.")

if __name__ == "__main__":
    main()