import streamlit as st
from utils import *

setup("Admin Panel")
st.title("Admin Panel")

if st.button("Create a Lecture"): st.switch_page("pages/create_lect.py")
if st.button("Delete a Lecture"): st.switch_page("pages/delete_lect.py")