import streamlit as st
from utils import *

def main():
    if "lect_script_to_edit" not in st.session_state or not st.session_state.lect_script_to_edit or "lect_to_edit" not in st.session_state or not st.session_state.lect_to_edit: 
        st.switch_page("pages/edit_quiz_choice.py")

    fetch_module_numbers()
    fetch_lect_ids()
    sort_lectures(st.session_state.lect_ids, st.session_state.module_numbers)
    setup("Edit Quiz")
    st.title("Edit Quiz")

    st.subheader(f"Editing Quiz for: {st.session_state.lect_to_edit}")

    # Get quiz items from session state
    quiz_items = st.session_state.lect_script_to_edit.get("quiz", [])

    # Display and edit existing quiz items
    if quiz_items:
        for i, item in enumerate(quiz_items):
            with st.expander(f"Question {i+1}: {item['question']}"):
                edited_question = st.text_area(f"Edit Question {i+1}", item["question"], key=f"q_{i}")
                edited_answer = st.text_area(f"Edit Answer {i+1}", item["answer"], key=f"a_{i}")
                
                col1, col2, col3 = st.columns([1, 1, 10])
                with col1:
                    if st.button("Update", key=f"update_{i}"):
                        quiz_items[i] = {"question": edited_question, "answer": edited_answer}
                        st.session_state.lect_script_to_edit["quiz"] = quiz_items
                        st.rerun()
                with col2:
                    if st.button("Delete", key=f"delete_{i}"):
                        quiz_items.pop(i)
                        st.session_state.lect_script_to_edit["quiz"] = quiz_items
                        st.rerun()
                with col3: st.empty()

    else:
        st.info("No quiz items available. Add some questions to get started.")

    # Add new quiz item
    with st.expander("Add New Quiz Item"):
        new_question = st.text_area("Question")
        new_answer = st.text_area("Answer")
        if st.button("Add Question"):
            if new_question and new_answer:
                quiz_items.append({"question": new_question, "answer": new_answer})
                st.session_state.lect_script_to_edit["quiz"] = quiz_items
                st.rerun()
            else:
                st.error("Both question and answer are required.")

    # Save changes to database
    if st.button("Save All Changes"):
        doc_ref = st.session_state.db.collection("lect_scripts").document(st.session_state.lect_to_edit)
        doc_ref.set(st.session_state.lect_script_to_edit)
        st.success("Quiz saved successfully!")

    if st.button("Back to Lecture Selection"):
        st.switch_page("pages/edit_quiz_choice.py")

if __name__ == "__main__":
    main()