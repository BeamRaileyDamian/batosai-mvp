import sys
import os
import streamlit as st
from utils import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.lect_gen import lect_gen

st.title("Create a Lecture")
set_sidebar()

if "lecture_title" not in st.session_state: st.session_state.lecture_title = ""
uploaded_file = st.file_uploader("PDF Presentation", type="pdf")
if uploaded_file:
    st.session_state.lecture_title = uploaded_file.name[:-4].replace("_", " ")

lect_title = st.text_input("Lecture Title", value=st.session_state.lecture_title)
# st.session_state.lecture_title = lect_title

if st.button("Create"):
    if lect_title in st.session_state.lect_ids:
        st.warning("Lecture Title Already Exists")
    elif uploaded_file and lect_title and uploaded_file.type == "application/pdf":
        filename = uploaded_file.name
        file = uploaded_file.read()

        response = lect_gen(file, filename, lect_title)
        if response: 
            if "lect_ids" in st.session_state:
                st.session_state.lect_ids.append(lect_title)
                st.session_state.lect_ids.sort()
            st.success("Lecture Successully Created")
        else: st.error("Lecture Creation Failed")
    elif not uploaded_file:
        st.error("PDF Presentation is Required")
    elif not lect_title:
        st.error("Lecture Title is Required")