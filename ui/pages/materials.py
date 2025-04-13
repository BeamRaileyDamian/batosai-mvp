import io
import os
import zipfile
import requests
from utils import *
import streamlit as st
from supabase import create_client

def download_all_files():
    try:
        # Show a spinner while preparing the download
        with st.spinner("Preparing files for download..."):
            # Create a temporary zip file
            zip_buffer = io.BytesIO()
            
            # Get the Supabase client and file structure
            SUPABASE_URL = os.environ.get("SUPABASE_URL")
            SUPABASE_KEY = os.environ.get("SUPABASE_API_KEY")
            client = create_client(SUPABASE_URL, SUPABASE_KEY)
            structure = list_folders_and_files(client, os.environ.get("BUCKET_NAME"), os.environ.get("BUCKET_FOLDER_PDF"))
            
            # Create a new zip file
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Loop through the structure and add files to the zip
                for item in structure:
                    if "folder" in item:
                        folder_name = item["folder"]
                        for file_item in item["contents"]:
                            file_name = file_item["file"]
                            file_url = file_item["public_url"]
                            
                            # Download the file content
                            file_content = requests.get(file_url).content
                            
                            # Add the file to the zip with folder structure
                            zip_path = f"{folder_name}/{file_name}"
                            zip_file.writestr(zip_path, file_content)
                    elif "file" in item:
                        # Handle files in the root directory
                        file_name = item["file"]
                        file_url = item["public_url"]
                        file_content = requests.get(file_url).content
                        zip_file.writestr(file_name, file_content)
            
            zip_buffer.seek(0)
            return zip_buffer
    except Exception as e:
        st.error(f"An error occurred while preparing the download: {str(e)}")
        return None

def list_folders_and_files(client, bucket_name, folder_path=""):
    root_response = client.storage.from_(bucket_name).list(folder_path)
    structure = []

    if root_response:
        for item in root_response:
            if item["name"] == ".emptyFolderPlaceholder":
                continue  # Skip placeholder files

            item_path = f"{folder_path}/{item['name']}".strip("/")  # Ensure correct path formatting
            
            if item["metadata"] is None:  # It's a folder
                sub_response = client.storage.from_(bucket_name).list(item_path)
                folder_contents = []

                if sub_response:
                    for sub_item in sub_response:
                        if sub_item["metadata"]:  # It's a file
                            file_path = f"{item_path}/{sub_item['name']}"
                            public_url = client.storage.from_(bucket_name).get_public_url(file_path).rstrip("?")
                            folder_contents.append({"file": sub_item["name"], "public_url": public_url})

                structure.append({"folder": item["name"], "contents": folder_contents})
            else:  # It's a file in the root folder
                public_url = client.storage.from_(bucket_name).get_public_url(item_path).rstrip("?")
                structure.append({"file": item["name"], "public_url": public_url})

    return structure

def main():
    setup("Materials")
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_API_KEY")
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    structure = list_folders_and_files(client, os.environ.get("BUCKET_NAME"), os.environ.get("BUCKET_FOLDER_PDF"))

    # Create session state variables to track download states
    if 'zip_ready' not in st.session_state:
        st.session_state.zip_ready = False
        st.session_state.zip_data = None
    
    # Track whether a download has been initiated
    if 'download_initiated' not in st.session_state:
        st.session_state.download_initiated = False
    
    # Function to handle zip creation
    def create_zip():
        zip_buffer = download_all_files()
        if zip_buffer:
            st.session_state.zip_data = zip_buffer
            st.session_state.zip_ready = True
            st.rerun()
    
    # Function to mark download as initiated
    def mark_download_initiated():
        st.session_state.download_initiated = True

    col1, col2 = st.columns([4,1])
    with col1:
        st.title("📚 CMSC 125 Materials")
    with col2:
        # Use a single container for all button states
        button_container = st.container()
        
        # Show the appropriate button based on the download state
        with button_container:
            if st.session_state.download_initiated:
                st.success("Download completed!")
            elif not st.session_state.zip_ready:
                if st.button("📦 Create Zip File"):
                    create_zip()
            else:
                st.download_button(
                    label="Download Zip File",
                    data=st.session_state.zip_data,
                    file_name="CMSC_125_Materials.zip",
                    mime="application/zip",
                    key="download-zip",
                    icon=":material/download:",
                    on_click=mark_download_initiated
                )

    for folder in structure:
        st.header(f"📁 {folder['folder']}")
        for file in folder["contents"]:
            # st.write(file["file"])
            st.download_button(
                label=file['file'],
                data=requests.get(file["public_url"]).content,
                file_name=file["file"],
                mime="application/pdf",
                icon="⬇️",
                key=folder["folder"]+"_"+file["file"]
            )
        st.divider()

if __name__ == "__main__":
    main()