import os
import sys
import time
from utils import *
import streamlit as st

# import pysqlite3
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from retriever import rag_pipeline, retriever_setup, create_retriever

def gen_sources(sources, relevance_scores):
    if not sources:
        return ""

    sources_html = """
    <div style='
        background-color: #404c44;
        border-left: 5px solid #59B75B;
        border-radius: 8px;
        padding: 12px;
        margin-top: 5px;
        font-size: 14px;
        color: #FDF6E3;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);
    '>
    <b style='font-size:23px; font-weight: bold; color: #70c272;'>📚 Sources:</b><br>
    """

    for i, source in enumerate(sources):
        filename = source['original_filename']
        page = source['page'] + 1
        relevance = relevance_scores[i]
        source_url = f"{source['url']}#page={page}"

        sources_html += (
            f"<span style='display: block; margin-top: 2px;'>"
            f"<span style='color:white3; font-size: 16px;'>{i+1}. {filename}</span> "
            f"<span style='color:#8ea395; font-size: 16px;'>(Page {page}) </span> "
            f"<span style='color:white; font-size: 16px;'>[Relevance: </span> "
            f"<span style='color:#70c272; font-size: 16px;'>{relevance}%</span> "
            f"<span style='color:white; font-size: 16px;'>]</span> "
            f"<span style='float: right;'>"
            f"<a href='{source_url}' target='_blank' "
            f"style='background-color: #59B75B; color: white; font-size: 16px; font-weight: bold; padding: 3px 10px;"
            f"border-radius: 6px; text-decoration: none;'>View</a></span>"
            f"</span><br>"
        )

    sources_html += "</div>"
    return sources_html


def change_scope():
    new_collection = st.session_state.selected_lect_id
    st.session_state.retriever = create_retriever(new_collection)

def main():
    setup("Chatbot")
    fetch_lect_ids()
    
    if not st.session_state.lect_ids:
        st.warning("No modules available. Ask admin to create modules to proceed.")
        st.stop()

    if "selected_lect_id" not in st.session_state:
        st.session_state.selected_lect_id = "General"

    if st.session_state.lect_ids and 'retriever' not in st.session_state or 'groq_api_key' not in st.session_state:
        st.session_state.retriever, st.session_state.groq_api_key = retriever_setup(st.session_state.selected_lect_id)

    col1, col2 = st.columns([3, 1])  # Adjust the widths of columns

    with col1:
        st.title("🗨️ Chatbot")
    with col2: 
        st.selectbox(
            label="Chatbot Scope",
            options=["General"] + st.session_state.lect_ids,
            key="selected_lect_id",
            on_change=change_scope
        )

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

    # Accept user input
    if prompt := st.chat_input("Ask about OS"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        response, st.session_state.chat_history, sources, relevance_scores = rag_pipeline(prompt, st.session_state.retriever, st.session_state.groq_api_key, st.session_state.chat_history)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            messagePlaceholder = st.empty()
            typedResponse = ""

            if response:
                sources_html = gen_sources(sources, relevance_scores)
                response_end = len(response)
                full_response = response + sources_html
                for i, char in enumerate(full_response):
                    typedResponse += char
                    messagePlaceholder.markdown(typedResponse, unsafe_allow_html=True)
                    if i < response_end:
                        time.sleep(0.001)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response + sources_html})

if __name__ == "__main__":
    main()