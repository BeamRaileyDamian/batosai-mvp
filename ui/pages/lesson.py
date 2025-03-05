import requests
from utils import *
import streamlit as st
from time import sleep
import streamlit_js_eval
from streamlit_lottie import st_lottie
from streamlit_pdf_viewer import pdf_viewer

if "curr_lect" in st.session_state: setup(st.session_state.curr_lect)
screen_width = streamlit_js_eval.streamlit_js_eval(js_expressions='screen.width', key = 'SCR')
url = st.session_state.lect_script["pdf_url"]
response = requests.get(url)

if "curr_slide" not in st.session_state: st.session_state.curr_slide = 1
#pdf_placeholder = st.empty()

avatar_url = requests.get("https://lottie.host/c0f03d0a-0b99-4286-b493-fde639e5c47c/IYycUBZs2E.json") 
avatar_url_json = dict() 
if avatar_url.status_code == 200: avatar_url_json = avatar_url.json() 
else: print("Error in the URL") 

if screen_width:
    col1, col2 = st.columns([0.15, 0.85], border=False)
    with col1:
        lottie_placeholder = st.empty()
    
    with col2:
        pdf_placeholder = st.empty()
    
    for slide in range(1, st.session_state.lect_script["slides_count"]):
        with lottie_placeholder:
            st_lottie(avatar_url_json, height=150, key=f"small_lottie_{slide}", width=int(screen_width*0.15))
        
        with col2:
            with pdf_placeholder:
                pdf_viewer(
                    input=response.content, 
                    width=int(screen_width*0.85),
                    pages_to_render=[slide],
                    render_text=True
                )
        
        try:
            mp3_url = st.session_state.lect_script["script"][slide-1]["audio"]
            duration = st.session_state.lect_script["script"][slide-1]["duration"]
            
            audio_html = f'''
                <audio autoplay>
                    <source src="{mp3_url}" type="audio/mp3">
                    Your browser does not support the audio element.
                </audio>
            '''
            
            st.markdown(audio_html, unsafe_allow_html=True)
            sleep(duration + 2)
            
            with lottie_placeholder:
                st.empty()
            
        except Exception as e:
            st.error(f'Error playing: {e}')