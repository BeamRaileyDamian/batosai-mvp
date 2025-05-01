import json
import random
import streamlit as st
import streamlit_js_eval
from utils import *

def load_local_lottie(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

def get_quote():
    try:
        collection_ref = st.session_state.db.collection("quotes")
        docs = collection_ref.stream()
        doc_list = list(docs)
        random_doc = random.choice(doc_list)
        return random_doc.to_dict()["quote"]
    except Exception as e:
        return f"Error retrieving document IDs: {str(e)}"

def main():
    setup("Lessons")
    fetch_module_numbers()
    fetch_lect_ids()
    sort_lectures(st.session_state.lect_ids, st.session_state.module_numbers)
    if "lect_script" not in st.session_state: st.session_state.lect_script = None
    if "curr_lect" not in st.session_state: st.session_state.curr_lect = None
    if "curr_slide" not in st.session_state: st.session_state.curr_slide = {}
    if "screen_width" not in st.session_state or not st.session_state.screen_width: st.session_state.screen_width = streamlit_js_eval.streamlit_js_eval(js_expressions='screen.width', key = 'SCR')
    if "avatar_url_json" not in st.session_state: st.session_state.avatar_url_json = load_local_lottie("assets/gif.json")

    st.session_state.pdf_response = None
    st.session_state.quote = get_quote()

    st.title("🧑‍🏫 CMSC 125 Lessons")
    button_styles()
    study_emojis = ["📚", "📖", "📝", "🎓", "📕", "📂", "📑", "🖊️", "📒", "📜", "💡", "🧠", "🗂️"]

    if st.session_state.lect_ids:
        for i, id in enumerate(st.session_state.lect_ids):
            module_number = st.session_state.module_numbers.get(id, None)
            emoji = study_emojis[i % len(study_emojis)]
            text = f"{emoji} Module {module_number}: {id}" if module_number is not None else f"{emoji} {id}"
            if st.button(text):
                if st.session_state.curr_lect != id:
                    st.session_state.curr_lect = id
                    st.session_state.curr_slide[id] = 0

                    doc_ref = st.session_state.db.collection("lect_scripts").document(id)
                    doc = doc_ref.get()
                    if doc.exists:
                        st.session_state.lect_script = doc.to_dict()
                    st.switch_page("pages/lesson.py")
                st.switch_page("pages/lesson.py")
    else:
        st.info("No lectures to display.")

if __name__ == "__main__":
    main()
