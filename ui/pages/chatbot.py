import os
import sys
import time
from utils import *
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from retriever import rag_pipeline, retriever_setup

def main():
    setup("Chatbot")

    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_config.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    if "lect_ids" not in st.session_state: st.session_state.lect_ids = get_all_document_ids(db, "lect_scripts")

    col1, col2 = st.columns([3, 1])  # Adjust the widths of columns

    # Create the selectbox inside one of the columns to control its width
    with col1:
        st.title("Chatbot")
    with col2: 
        option = st.selectbox(
        'Chatbot Scope',
            ["General"] + st.session_state.lect_ids
        )

    if 'retriever' not in st.session_state or 'groq_api_key' not in st.session_state:
        st.session_state.retriever, st.session_state.groq_api_key = retriever_setup()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        response = rag_pipeline(prompt, st.session_state.retriever, st.session_state.groq_api_key)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            messagePlaceholder = st.empty()
            typedResponse = ""
            if response:
                for char in response: # added typing effect
                    typedResponse += char
                    messagePlaceholder.markdown(typedResponse)
                    time.sleep(0.01)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()