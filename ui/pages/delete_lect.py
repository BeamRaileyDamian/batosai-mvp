import os
import sys
from utils import *
import streamlit as st
from supabase import create_client
from langchain_chroma import Chroma

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.embedder import get_embedding_function
from src.config import *

def delete_from_firebase(db, collection_name, document_id):
    try:
        doc_ref = db.collection(collection_name).document(document_id)

        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
            return True
        else:
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
def delete_supabase_folder(client, bucket_name, folder_name):
    response = client.storage.from_(bucket_name).list(folder_name)

    if response:
        file_paths = [f"{folder_name}{file['name']}" for file in response]
        delete_response = client.storage.from_(bucket_name).remove(file_paths)

        if delete_response:
            return True
        else:
            return False
    else:
        return False

def main():
    setup("Delete a Lecture")
    st.title("Delete a Lecture")
    fetch_module_numbers()
    fetch_lect_ids()
    sort_lectures(st.session_state.lect_ids, st.session_state.module_numbers)
    button_styles()

    # Initialize Supabase client
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_API_KEY"]
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Define bucket name and folder to delete
    bucket_name = st.secrets["BUCKET_NAME"]
    folder_name = st.secrets["BUCKET_FOLDER_PDF"]

    if st.session_state.lect_ids:
        for id in st.session_state.lect_ids:
            module_number = st.session_state.module_numbers.get(id, None)
            text = f"Module {module_number}: {id}" if module_number is not None else id
            if st.button(text, key=id):
                result = delete_from_firebase(st.session_state.db, "lect_scripts", id)
                result2 = delete_supabase_folder(client, bucket_name, f"{folder_name}/{id}/")

                chroma_db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embedding_function())
                chroma_db.delete(where={"lesson_id": id})
                
                if result and result2:
                    st.session_state.lect_ids.remove(id)
                    st.rerun()
                else:
                    st.success("Lecture Deletion Failed")
    else:
        st.info("No lectures to display.")

if __name__ == "__main__":
    main()