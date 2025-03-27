from utils import *
import streamlit as st
import streamlit_authenticator as stauth

def main():
    setup("Admin Panel")
    fetch_lect_ids()

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
            st.session_state.admin_title = f'Welcome, {st.session_state["name"]}'
            if st.button("Create a Lecture"): st.switch_page("pages/create_lect.py")
            if st.button("Edit a Lecture's Quiz"): st.switch_page("pages/edit_quiz_choice.py")
            if st.button("Edit Quotes"): st.switch_page("pages/edit_quotes.py")
            if st.button("Delete a Lecture"): st.switch_page("pages/delete_lect.py")
            if authenticator.logout():
                st.session_state.admin_title = "Admin Panel"
                st.rerun()

    elif st.session_state['authentication_status'] is False:
        st.error('Username/password is incorrect')
    elif st.session_state['authentication_status'] is None:
        st.warning('Please Enter Credentials')

if __name__ == "__main__":
    main()