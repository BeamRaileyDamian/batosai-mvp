import streamlit as st
from utils import *

def main():
    setup("Edit Quiz")
    fetch_module_numbers()
    fetch_lect_ids()
    sort_lectures(st.session_state.lect_ids, st.session_state.module_numbers)
    button_styles()
    if "lect_script_to_edit" not in st.session_state: st.session_state.lect_script_to_edit = None
    if "lect_to_edit" not in st.session_state: st.session_state.lect_to_edit = None

    st.title("Edit Quiz")

    if st.session_state.lect_ids:
        for id in st.session_state.lect_ids:
            module_number = st.session_state.module_numbers.get(id, None)
            text = f"Module {module_number}: {id}" if module_number is not None else id
            if st.button(text):
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