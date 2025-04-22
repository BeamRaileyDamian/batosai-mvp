import sys
import os
from utils import *
import streamlit as st
from supabase import create_client, Client

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.lect_gen import *
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
    fetch_lect_ids()
    fetch_module_numbers()

    if "lecture_title" not in st.session_state: st.session_state.lecture_title = ""
    if "lecture_num" not in st.session_state: st.session_state.lecture_num = None
    uploaded_file = st.file_uploader("PDF Presentation", type="pdf")
    if uploaded_file:
        st.session_state.lecture_title = uploaded_file.name[:-4].replace("_", " ")

    additional_files = st.file_uploader("Additional Files (Optional, Used as Extra Knowledge Base for Answering Students' Questions)", type="pdf", accept_multiple_files=True)
    
    col1, col2, col3 = st.columns([1, 2, 3])
    with col1:
        lect_num = st.number_input("Module Number (Optional)", step=1, min_value=1, value=st.session_state.lecture_num)
    with col2:
        lect_title = st.text_input("Lecture Title", value=st.session_state.lecture_title)
    with col3: 
        options = [
            "Charismatic", "Approachable", "Witty", "Playful",  # Communication Style & Engagement
            "Storyteller", "Dramatic", "Mysterious",  # Teaching Style & Delivery
            "Smart", "Nerdy", "Organized",  # Knowledge & Structure
            "Inspirational", "Wholesome", "Chill", "Strict"  # Attitude & Approachability
        ]
        lect_personality = st.multiselect(label=f"Lecturer Personality", default=["Chill", "Approachable", "Smart"], options=options, max_selections=3)

    # Initialize Supabase
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_api_key = os.environ.get("SUPABASE_API_KEY")
    bucket_name = os.environ.get("BUCKET_NAME")
    bucket_folder_pdf = os.environ.get("BUCKET_FOLDER_PDF")

    if st.button("Create"):
        if lect_title in st.session_state.lect_ids:
            st.warning("Lecture Title Already Exists")
        elif uploaded_file and lect_title and lect_personality and uploaded_file.type == "application/pdf":
            filename = uploaded_file.name
            file = uploaded_file.read()

            scripts, quiz = gen_script_and_quiz(file, lect_num, lect_personality)
            if scripts and quiz:
                st.session_state.generated_data = {
                    "scripts": scripts,
                    "quiz": quiz,
                    "file": file,
                    "filename": filename,
                    "lect_title": lect_title,
                    "lect_num": lect_num,
                    "lect_personality": lect_personality
                }
                st.session_state.show_continue_button = True
            else:
                st.error("Lecture Creation Failed")
        elif not uploaded_file:
            st.error("PDF Presentation is Required")
        elif not lect_title:
            st.error("Lecture Title is Required")
        elif not lect_personality:
            st.error("Select at least one lecturer personality")

    # Handle Continue button separately
    if st.session_state.get("show_continue_button", False):
        if st.button("Continue?"):
            data = st.session_state.get("generated_data")
            if data:
                publicUrl = gen_audio_upload_pdf(
                    data["scripts"], data["quiz"],
                    data["file"], data["filename"],
                    data["lect_title"], data["lect_num"]
                )
                if publicUrl:
                    st.session_state.lect_ids.append(data["lect_title"])
                    if data["lect_num"]:
                        st.session_state.module_numbers[data["lect_title"]] = data["lect_num"]
                    sort_lectures(st.session_state.lect_ids, st.session_state.module_numbers)

                    rag_pdfs = [data["file"]]
                    rag_pdfs_url = [publicUrl]
                    rag_pdfs_filenames = [data["filename"]]

                    if additional_files:
                        for f in additional_files:
                            if f.name not in rag_pdfs_filenames:
                                f.seek(0)
                                file_content = f.read()
                                bucket_storage_path = f"{bucket_folder_pdf}/{data['lect_title']}/{f.name}"
                                url = upload_to_supabase(file_content, bucket_storage_path, supabase_url, supabase_api_key, bucket_name, "application/pdf")
                                
                                rag_pdfs.append(file_content)
                                rag_pdfs_filenames.append(f.name)
                                rag_pdfs_url.append(url)

                    response_rag = create_embeddings(rag_pdfs, data["lect_title"], rag_pdfs_filenames, rag_pdfs_url)
                    if response_rag:
                        st.success("Lecture Successfully Created")
                    else:
                        st.error("Lecture Creation Failed")
                else:
                    st.error("Lecture Creation Failed")

            # Reset continue state
            st.session_state.show_continue_button = False
            st.session_state.generated_data = None

if __name__ == "__main__":
    main()