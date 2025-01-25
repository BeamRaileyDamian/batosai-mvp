import requests
from utils import *
import streamlit as st
import streamlit_js_eval
from streamlit_pdf_viewer import pdf_viewer

setup(st.session_state.curr_lect)
screen_width = streamlit_js_eval.streamlit_js_eval(js_expressions='screen.width', key = 'SCR')
url = st.session_state.lect_script["pdf_url"]
response = requests.get(url)
try:
    pdf_viewer(input=response.content, 
            width=int(screen_width*0.8),
            render_text=True)
except: pass