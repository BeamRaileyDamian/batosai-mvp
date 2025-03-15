from utils import *
import firebase_admin
import streamlit as st
from firebase_admin import firestore
import streamlit_authenticator as stauth

setup("Admin Panel")

config = {
    "credentials": st.secrets["credentials"].to_dict(),
    "cookie": st.secrets["cookie"],
    "preauthorized": st.secrets["preauthorized"]
}

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["preauthorized"]
)

if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.session_state.admin_title = "Admin Panel"
elif st.session_state["authentication_status"] and st.session_state["name"]:
    st.session_state.admin_title = f'Welcome, {config['credentials']['usernames'][st.session_state["username"]]["name"]}'

st.title(st.session_state.admin_title)

try:
    stauth.Hasher.hash_passwords(config['credentials'])
except: pass

try:
    authenticator.login()
except Exception as e:
    st.error(f"Error: {e}")

if st.session_state['authentication_status']:
        if not firebase_admin._apps:
            init_firebase()
        db = firestore.client()

        if "lect_ids" not in st.session_state:
            st.session_state.lect_ids = get_all_document_ids(db, "lect_scripts")

        st.session_state.admin_title = f'Welcome, {st.session_state["name"]}'
        if st.button("Create a Lecture"): st.switch_page("pages/create_lect.py")
        if st.button("Edit a Lecture's Quiz"): st.switch_page("pages/edit_quiz_choice.py")
        if st.button("Delete a Lecture"): st.switch_page("pages/delete_lect.py")
        if authenticator.logout():
            st.session_state.admin_title = "Admin Panel"
            st.rerun()

elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please Enter Credentials')