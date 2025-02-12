import yaml
from utils import *
import firebase_admin
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from firebase_admin import credentials, firestore

setup("Admin Panel")

config = None
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.session_state.admin_title = "Admin Panel"
elif st.session_state["authentication_status"] and st.session_state["name"]:
    st.session_state.admin_title = f'Welcome, {config['credentials']['usernames'][st.session_state["username"]]['first_name']}'

st.title(st.session_state.admin_title)

# Ensure passwords are pre-hashed
try:
    stauth.Hasher.hash_passwords(config['credentials'])
except: pass

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    auto_hash=False
)

try:
    authenticator.login()
except Exception as e:
    st.error(f"Error: {e}")

try:
    authenticator.experimental_guest_login('Login with Google',
                                           provider='google',
                                           oauth2=config['oauth2'])
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
except Exception as e:
    st.error(e)

if st.session_state['authentication_status']:
        if not firebase_admin._apps:
            init_firebase()
        db = firestore.client()

        if "lect_ids" not in st.session_state:
            st.session_state.lect_ids = get_all_document_ids(db, "lect_scripts")

        st.session_state.admin_title = f'Welcome, {st.session_state["name"]}'
        if st.button("Create a Lecture"): st.switch_page("pages/create_lect.py")
        if st.button("Update a Lecture"): pass  # st.switch_page("pages/edit_lect.py")
        if st.button("Delete a Lecture"): st.switch_page("pages/delete_lect.py")
        if authenticator.logout():
            st.session_state.admin_title = "Admin Panel"
            st.rerun()

elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please Enter Credentials or Login with Google')