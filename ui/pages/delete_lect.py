from utils import *
import firebase_admin
import streamlit as st
from firebase_admin import firestore
from supabase import create_client

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
    if not firebase_admin._apps:
        init_firebase()
    db = firestore.client()

    setup("Delete a Lecture")
    st.title("Delete a Lecture")

    # Initialize Supabase client
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_API_KEY"]
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Define bucket name and folder to delete
    bucket_name = st.secrets["BUCKET_NAME"]
    folder_name = st.secrets["BUCKET_FOLDER_PDF"]

    if st.session_state.lect_ids:
        for id in st.session_state.lect_ids:
            if st.button(id, key=id):
                result = delete_from_firebase(db, "lect_scripts", id)
                result2 = delete_supabase_folder(client, bucket_name, f"{folder_name}/{id}/")
                
                if result and result2:
                    st.session_state.lect_ids.remove(id)
                    st.rerun()
                    # st.success("Lecture Successfully Deleted")
                else:
                    st.success("Lecture Deletion Failed")
    else:
        st.info("No lectures to display.")

if __name__ == "__main__":
    main()