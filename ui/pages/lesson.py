import os
import time
import random
import base64
import requests
from utils import *
import streamlit as st
import streamlit_js_eval
from streamlit_lottie import st_lottie
from audio_component import audio_player
from streamlit_pdf_viewer import pdf_viewer

def apply_styles():
    st.markdown("""
        <style>
        .transcript-container {
            background-color: #f8f9fa;
            border-radius: 5px;
            color: #4b644c;
            padding: 5px;
            margin-top: 5px;
            font-size: 14px;
            border-left: 3px solid #4682b4;
            max-height: 400px;
            overflow-y: auto;
        }
        .quiz-question {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #e0e0e0; /* Lighter text for green board */
        }
        .quiz-answer {
            font-size: 18px;
            color: white;
            margin-bottom: 20px;
            padding: 10px;
            background-color: #567257;
            border-left: 4px solid #59B75B;
            border-radius: 5px;
        }
        .timer {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            padding: 10px;
            text-align: center;
            
            background-color: #59B75B !important;
            color: white !important;
            border-radius: 8px !important;
            border: 1px solid #284329 !important;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2) !important; 
        }
        
        .green-board {
            background-color: #4b644c;
            background-size: 30px 30px;
            border-radius: 10px;
            padding: 20px;
            color: #e0e0e0;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.3);
            min-height: 400px;
        }
        
        .green-board h2 {
            color: #ffffff;
            margin-bottom: 20px;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

def get_quote():
    try:
        collection_ref = st.session_state.db.collection("quotes")
        docs = collection_ref.stream()
        doc_list = list(docs)
        random_doc = random.choice(doc_list)
        return random_doc.to_dict()["quote"]
    except Exception as e:
        return f"Error retrieving document IDs: {str(e)}"

def load_gif(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    return encoded

def main():
    if not "curr_lect" in st.session_state or not st.session_state.curr_lect or not "lect_script" in st.session_state or not st.session_state.lect_script: 
        st.switch_page("pages/modules.py")
    else: 
        setup(st.session_state.curr_lect)

    screen_width = streamlit_js_eval.streamlit_js_eval(js_expressions='screen.width', key = 'SCR')
    url = st.session_state.lect_script["pdf_url"]
    response = requests.get(url)

    if "curr_slide" not in st.session_state: st.session_state.curr_slide = 0
    if "countdown" not in st.session_state: st.session_state.countdown = 60
    st.session_state.first_slide_relative = True

    avatar_url = requests.get(st.secrets["GIF"].strip('"')) 
    avatar_url_json = dict() 
    if avatar_url.status_code == 200: avatar_url_json = avatar_url.json() 
    else: print("Error in the URL") 

    quote = get_quote()
    apply_styles()

    if screen_width:
        col1, col2 = st.columns([0.85, 0.15], border=False)
        col1_placeholder = st.empty()
        col2_placeholder = st.empty()
        transcript_placeholder = st.empty()

        if st.session_state.curr_slide < st.session_state.lect_script["slides_count"]:
            with col1:
                col1_placeholder = st.empty()
            
            with col2:
                col2_placeholder = st.empty()
                transcript_placeholder = st.empty()

            with col1:
                with col1_placeholder:
                    pdf_viewer(
                        input=response.content, 
                        width=int(screen_width*0.85),
                        pages_to_render=[st.session_state.curr_slide+1],
                        render_text=True,
                        key=f"slide_{st.session_state.curr_slide}"
                    )
            
            with transcript_placeholder:
                transcript_text = st.session_state.lect_script["script"][st.session_state.curr_slide]["script"]
                st.markdown(f'<div class="transcript-container">{transcript_text}</div>', unsafe_allow_html=True)

            if st.session_state.first_slide_relative:
                st.session_state.first_slide_relative = False
                with col2_placeholder:
                    st_lottie(avatar_url_json, key=f"small_lottie_{st.session_state.curr_slide}", width=int(screen_width*0.12))

                    with transcript_placeholder:
                        transcript_text = st.session_state.lect_script["script"][st.session_state.curr_slide]["script"]
                        st.markdown(f'<div class="transcript-container">{transcript_text}</div>', unsafe_allow_html=True)

            try:
                mp3_url = st.session_state.lect_script["script"][st.session_state.curr_slide]["audio"]          

                if f"audio_done_{st.session_state.curr_slide}" not in st.session_state:
                    st.session_state[f"audio_done_{st.session_state.curr_slide}"] = False

                if not st.session_state[f"audio_done_{st.session_state.curr_slide}"]:
                    result = audio_player(mp3_url, key=f"audio_{st.session_state.curr_slide}")

                    if result:
                        if result.get("event") == "audio_ended":
                            st.session_state[f"audio_done_{st.session_state.curr_slide}"] = True
                
                if st.session_state[f"audio_done_{st.session_state.curr_slide}"]:
                    st.session_state.curr_slide += 1
                    transcript_placeholder.empty()
                    col1_placeholder.empty()
                    col2_placeholder.empty()
                    st.rerun()

            except Exception as e:
                st.error(f'Error playing: {e}')

        else: 
            transcript_placeholder.empty()
            col1_placeholder.empty()
            col2_placeholder.empty()
            
            ################# CHECK NOTES #####################
            # Use placeholders for the notes review content so we can clear them later
            with col1:
                notes_header_placeholder = st.empty()
                
                # Fill the placeholders with content
                notes_content = f'''
                <div class="green-board">
                    <h2>Review your notes in preparation for a quiz! 🧠</h2>
                    <div style="color: #e0e0e0; text-align: center; font-weight: bold; font-size: 25px; margin-top: 20px;">{quote}</div>
                </div>
                '''
                notes_header_placeholder.markdown(notes_content, unsafe_allow_html=True)

            with col2:
                timer_placeholder = st.empty()
                while st.session_state.countdown > 0:
                    minutes, seconds = divmod(st.session_state.countdown, 60)
                    with timer_placeholder:
                        st.markdown(f'<div class="timer">Time Left: {minutes:02d}:{seconds:02d} ⏳</div>', unsafe_allow_html=True)
                    time.sleep(1)
                    with timer_placeholder:
                        st.empty()
                    st.session_state.countdown -= 1
                with timer_placeholder: st.markdown(f'<div class="timer">Time\'s up! ⏰</div>', unsafe_allow_html=True)
                time.sleep(1)

            # Clear all the placeholders after time is up
            with col1_placeholder: st.empty()
            with col2_placeholder: st.empty()
            transcript_placeholder.empty()
            timer_placeholder.empty()
            notes_header_placeholder.empty()
            
            ################# QUIZ ############################
            st.session_state.countdown = 120
            
            # Create placeholders for quiz content
            with col1:
                quiz_header_placeholder = st.empty()
                
                # Combine header and questions in a single green board div
                quiz_content = f'''
                <div class="green-board">
                    <h2>Quiz Time! 📝</h2>
                    {"".join(f'<div class="quiz-question">{i+1}. {st.session_state.lect_script["quiz"][i]["question"]}</div>' for i in range(len(st.session_state.lect_script["quiz"])))}
                </div>
                '''
                quiz_header_placeholder.markdown(quiz_content, unsafe_allow_html=True)

            with col2:
                timer_placeholder = st.empty()
                while st.session_state.countdown > 0:
                    minutes, seconds = divmod(st.session_state.countdown, 60)
                    with timer_placeholder:
                        st.markdown(f'<div class="timer">Time Left: {minutes:02d}:{seconds:02d} ⏳</div>', unsafe_allow_html=True)
                    time.sleep(1)
                    with timer_placeholder:
                        st.empty()
                    st.session_state.countdown -= 1
                
                # Show time's up message temporarily
                with timer_placeholder:
                    st.markdown(f'<div class="timer">Time\'s up! ⏰</div>', unsafe_allow_html=True)
                    time.sleep(1)
            
            ################# QUIZ ANSWERS ############################
            # Clear quiz content
            quiz_header_placeholder.empty()
            st.session_state.curr_slide = 0
            st.session_state.countdown = 60
            
            with col1:
                answers_header_placeholder = st.empty()
                
                # Combine header, questions, and answers in a single green board div
                answers_content = f'''
                <div class="green-board">
                    <h2>Quiz Answers 🎓</h2>
                    {"".join(f'<div class="quiz-question">{i+1}. {st.session_state.lect_script["quiz"][i]["question"]}</div><div class="quiz-answer">{st.session_state.lect_script["quiz"][i]["answer"]}</div>' for i in range(len(st.session_state.lect_script["quiz"])))}
                </div>
                '''
                answers_header_placeholder.markdown(answers_content, unsafe_allow_html=True)

            with col2:
                with timer_placeholder: st.empty()
                st.page_link("pages/modules.py", label="Back to Lessons")
    
if __name__ == "__main__":
    main()