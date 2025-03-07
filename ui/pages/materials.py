from utils import *
import streamlit as st
from supabase import create_client

setup("Materials")
st.title("CMSC 125 Materials")

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
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_API_KEY"]
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    structure = list_folders_and_files(client, st.secrets["BUCKET_NAME"], st.secrets["BUCKET_FOLDER_PDF"])

    for folder in structure:
        st.header(folder["folder"])
        for file in folder["contents"]:
            st.write(file["file"])
        st.divider()

if __name__ == "__main__":
    main()