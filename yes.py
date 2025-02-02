import io
import base64
import requests
from utils import *
from gtts import gTTS
import streamlit as st
from time import sleep
import streamlit_js_eval
from pydub import AudioSegment, effects
from streamlit_pdf_viewer import pdf_viewer

def text_to_speech(text, lang="en"):
    # Generate TTS audio
    tts = gTTS(text=text, lang=lang)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    
    # Load the audio into pydub
    audio = AudioSegment.from_file(fp, format="mp3")
    audio = effects.speedup(audio, playback_speed=1.2)
    
    # Save to a byte stream in mp3 format
    audio_fp = io.BytesIO()
    audio.export(audio_fp, format="mp3")
    audio_fp.seek(0)
    
    return audio_fp, audio.duration_seconds

if "curr_lect" in st.session_state: setup(st.session_state.curr_lect)
screen_width = streamlit_js_eval.streamlit_js_eval(js_expressions='screen.width', key = 'SCR')
if "lect_script" in st.session_state: url = st.session_state.lect_script["pdf_url"]
response = requests.get(url)

if "curr_slide" not in st.session_state: st.session_state.curr_slide = 1
pdf_placeholder = st.empty()

if screen_width:
    for slide in range(1, st.session_state.lect_script["slides_count"]):
        with pdf_placeholder:
            pdf_viewer(input=response.content, 
                    width=int(screen_width*0.8),
                    pages_to_render=[slide],
                    render_text=True)
            
        try:
            # Get the audio and its duration
            audio_fp, audio_duration = text_to_speech(st.session_state.lect_script["script"][slide-1], "en")
            
            # Encode the audio as base64
            audio_base64 = base64.b64encode(audio_fp.read()).decode('utf-8')
            audio_url = f"data:audio/mp3;base64,{audio_base64}"
            
            # Use markdown to hide audio player UI, just play audio
            st.markdown(f'<audio autoplay="true" src="{audio_url}" style="display:none;"></audio>', unsafe_allow_html=True)

            sleep(audio_duration)

        except Exception as e:
            st.error(f'Error converting text to speech: {e}')
