import os
import sys
import time
from utils import *
import streamlit as st
import firebase_admin
from firebase_admin import firestore

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from retriever import rag_pipeline, retriever_setup, create_retriever

def change_scope():
    new_collection = st.session_state.selected_lect_id
    st.session_state.retriever = create_retriever(new_collection)

def main():
    setup("Chatbot")

    if not firebase_admin._apps:
        init_firebase()
    db = firestore.client()

    if 'lect_ids' not in st.session_state: st.session_state.lect_ids = get_all_document_ids(db, "lect_scripts")
    
    if not st.session_state.lect_ids:
        st.warning("No modules available. Ask admin to create modules to proceed.")
        st.stop()

    if "selected_lect_id" not in st.session_state:
        st.session_state.selected_lect_id = st.session_state.lect_ids[0]

    if st.session_state.lect_ids and 'retriever' not in st.session_state or 'groq_api_key' not in st.session_state:
        st.session_state.retriever, st.session_state.groq_api_key = retriever_setup(st.session_state.selected_lect_id)

    col1, col2 = st.columns([3, 1])  # Adjust the widths of columns

    with col1:
        st.title("Chatbot")
    with col2: 
        st.selectbox(
            label="Chatbot Scope",
            options=st.session_state.lect_ids,
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
    if prompt := st.chat_input("What is up?"):
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
            
            sources_html = ""
            if sources:
                sources_html = "\n\n<b>Sources:</b>\n"
                # Use a div with consistent left margin for alignment
                sources_html += "<div style='margin-left:0px;'>\n"
                
                for i, source in enumerate(sources):
                    filename = source['original_filename']
                    page = source['page'] + 1
                    relevance = relevance_scores[i]
                    
                    # Create a URL for each source
                    source_url = f"{source['url']}#page={page}"
                    
                    # Create a clean line with consistent spacing using spans for alignment
                    sources_html += f"<div style='margin-bottom:5px;'>\n"
                    sources_html += f"  <span style='display:inline-block; width:30px;'>{i+1}.</span>"
                    sources_html += f"  <span style='margin-left:10px;'>{filename} | Page {page} | Relevance Score: {relevance}% | </span>\n"
                    sources_html += f"  <span><a href='{source_url}' target='_blank' style='color: #FDF6E3; font-weight: bold;'>View</a></span>"
                    sources_html += f"</div>\n"
                
                sources_html += "</div>"

            if response:
                full_response = response + sources_html
                for char in full_response:  # added typing effect
                    typedResponse += char
                    messagePlaceholder.markdown(typedResponse, unsafe_allow_html=True)
                    time.sleep(0.001)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response + sources_html})

if __name__ == "__main__":
    main()