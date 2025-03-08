import sys
import os
from utils import *
import streamlit as st
from supabase import create_client, Client

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.lect_gen import lect_gen
from src.embedder import create_embeddings

def upload_to_supabase(file, storage_path, supabase_url, supabase_api_key, bucket_name, content_type):
    supabase: Client = create_client(supabase_url, supabase_api_key)
    
    try:
        supabase.storage.from_(bucket_name).upload(storage_path, file, {'content-type': content_type, 'upsert': 'true'})
    except Exception as e:
        error_dict = e.to_dict() if hasattr(e, "to_dict") else {}
        
        # # If file already exists, delete it first
        # if error_dict.get("code") == "Duplicate":
        #     supabase.storage.from_(bucket_name).remove([storage_path])
        #     supabase.storage.from_(bucket_name).upload(storage_path, file, {'content-type': content_type})
    
    public_url = supabase.storage.from_(bucket_name).get_public_url(storage_path)
    return public_url.rstrip("?")

def main():
    setup("Create a Lecture")
    st.title("Create a Lecture")

    if "lecture_title" not in st.session_state: st.session_state.lecture_title = ""
    uploaded_file = st.file_uploader("PDF Presentation", type="pdf")
    if uploaded_file:
        st.session_state.lecture_title = uploaded_file.name[:-4].replace("_", " ")

    additional_files = st.file_uploader("Additional Files (Optional, Used as Extra Knowledge Base for Answering Students' Questions)", type="pdf", accept_multiple_files=True)
    lect_title = st.text_input("Lecture Title", value=st.session_state.lecture_title)

    # Initialize Supabase
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_api_key = st.secrets["SUPABASE_API_KEY"]
    bucket_name = st.secrets["BUCKET_NAME"]
    bucket_folder_pdf = st.secrets["BUCKET_FOLDER_PDF"]

    if st.button("Create"):
        if lect_title in st.session_state.lect_ids:
            st.warning("Lecture Title Already Exists")
        elif uploaded_file and lect_title and uploaded_file.type == "application/pdf":
            filename = uploaded_file.name
            file = uploaded_file.read()

            publicUrl = lect_gen(file, filename, lect_title)
            if publicUrl: 
                if "lect_ids" in st.session_state:
                    st.session_state.lect_ids.append(lect_title)
                    st.session_state.lect_ids.sort()
            else: 
                st.error("Lecture Creation Failed")
                return

            rag_pdfs = [file]
            rag_pdfs_url = [publicUrl]
            rag_pdfs_filenames = [filename]
            if additional_files:
                for f in additional_files:
                    if f.name not in rag_pdfs_filenames:
                        f.seek(0)
                        file_content = f.read()
                        bucket_storage_path = f"{bucket_folder_pdf}/{lect_title}/{f.name}"
                        url = upload_to_supabase(file_content, bucket_storage_path, supabase_url, supabase_api_key, bucket_name, "application/pdf")
                        
                        rag_pdfs.append(file_content)
                        rag_pdfs_filenames.append(f.name)
                        rag_pdfs_url.append(url)

            response_rag = create_embeddings(rag_pdfs, lect_title, rag_pdfs_filenames, rag_pdfs_url)

            if publicUrl and response_rag:
                st.success("Lecture Successully Created")

        elif not uploaded_file:
            st.error("PDF Presentation is Required")
        elif not lect_title:
            st.error("Lecture Title is Required")

if __name__ == "__main__":
    main()