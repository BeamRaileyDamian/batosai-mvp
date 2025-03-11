import time
import random
import requests
from utils import *
import firebase_admin
import streamlit as st
import streamlit_js_eval
from firebase_admin import firestore
from streamlit_lottie import st_lottie
from streamlit_pdf_viewer import pdf_viewer

def get_quote():
    if not firebase_admin._apps:
        cred = st.secrets["firebase"]["proj_settings"]
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    try:
        collection_ref = db.collection("quotes")
        docs = collection_ref.stream()
        doc_list = list(docs)
        random_doc = random.choice(doc_list)
        return random_doc.to_dict()["quote"]
    except Exception as e:
        return f"Error retrieving document IDs: {str(e)}"

def main():
    if "curr_lect" in st.session_state: setup(st.session_state.curr_lect)
    screen_width = streamlit_js_eval.streamlit_js_eval(js_expressions='screen.width', key = 'SCR')
    url = st.session_state.lect_script["pdf_url"]
    response = requests.get(url)

    if "curr_slide" not in st.session_state: st.session_state.curr_slide = 1
    if "countdown" not in st.session_state: st.session_state.countdown = 3

    avatar_url = requests.get("https://lottie.host/c0f03d0a-0b99-4286-b493-fde639e5c47c/IYycUBZs2E.json") 
    avatar_url_json = dict() 
    if avatar_url.status_code == 200: avatar_url_json = avatar_url.json() 
    else: print("Error in the URL") 

    if screen_width:
        col1, col2 = st.columns([0.15, 0.85], border=False)
        with col1:
            col1_placeholder = st.empty()
        
        with col2:
            col2_placeholder = st.empty()
        
        for slide in range(st.session_state.lect_script["slides_count"]):
            with col1_placeholder:
                st_lottie(avatar_url_json, height=150, key=f"small_lottie_{slide}", width=int(screen_width*0.15))
            
            with col2:
                with col2_placeholder:
                    pdf_viewer(
                        input=response.content, 
                        width=int(screen_width*0.85),
                        pages_to_render=[slide+1],
                        render_text=True
                    )
            
            try:
                mp3_url = st.session_state.lect_script["script"][slide]["audio"]
                duration = st.session_state.lect_script["script"][slide]["duration"]
                
                audio_html = f'''
                    <audio autoplay>
                        <source src="{mp3_url}" type="audio/mp3">
                        Your browser does not support the audio element.
                    </audio>
                '''
                
                st.markdown(audio_html, unsafe_allow_html=True)
                time.sleep(duration + 2)
                
                with col1_placeholder:
                    st.empty()
                
            except Exception as e:
                st.error(f'Error playing: {e}')

        with col2_placeholder:
            st.empty()

        st.markdown("""
        <style>
        .quiz-question {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .quiz-answer {
            font-size: 18px;
            color: #4b644c;
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f0f8ff;
            border-left: 4px solid #4682b4;
            border-radius: 5px;
        }
        .timer {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 10px;  
            border: 3px solid #FF5733; 
            padding: 10px;
            border-radius: 10px;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)

        ################# CHECK NOTES #####################
        # Use placeholders for the notes review content so we can clear them later
        with col2:
            notes_header_placeholder = st.empty()
            quote_placeholder = st.empty()
            
            # Fill the placeholders with content
            notes_header_placeholder.header("Review your notes in preparation for a quiz! 🧠")
            quote = get_quote()
            quote_placeholder.subheader(quote)

        with col1:
            timer_placeholder = st.empty()
            while st.session_state.countdown > 0:
                minutes, seconds = divmod(st.session_state.countdown, 60)
                with timer_placeholder:
                    st.markdown(f'<div class="timer">Time Left: {minutes:02d}:{seconds:02d} ⏳</div>', unsafe_allow_html=True)
                time.sleep(1)
                with timer_placeholder:
                    st.empty()
                st.session_state.countdown -= 1
            timer_placeholder.write("Time's up! ⏰")
            time.sleep(1)

        # Clear all the placeholders after time is up
        with col1_placeholder: st.empty()
        with col2_placeholder: st.empty()
        timer_placeholder.empty()
        notes_header_placeholder.empty()
        quote_placeholder.empty()
        
        ################# QUIZ ############################
        st.session_state.countdown = 3
        
        # Create placeholders for quiz content
        with col2:
            quiz_header_placeholder = st.empty()
            quiz_content_placeholder = st.empty()
            
            # Display quiz header and questions
            quiz_header_placeholder.header("Quiz Time! 📝")
            
            quiz_content = ""
            for i in range(len(st.session_state.lect_script["quiz"])):
                quiz_content += f'<div class="quiz-question">{i+1}. {st.session_state.lect_script["quiz"][i]["question"]}</div>'
            
            quiz_content_placeholder.markdown(quiz_content, unsafe_allow_html=True)

        with col1:
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
        
        ################# QUIZ ANSWERS ############################
        # Clear quiz content
        quiz_header_placeholder.empty()
        quiz_content_placeholder.empty()
        
        with col2:
            answers_header_placeholder = st.empty()
            answers_content_placeholder = st.empty()
            
            answers_header_placeholder.header("Quiz Answers 🎓")
            
            answers_content = ""
            for i in range(len(st.session_state.lect_script["quiz"])):
                answers_content += f'<div class="quiz-question">{i+1}. {st.session_state.lect_script["quiz"][i]["question"]}</div>'
                answers_content += f'<div class="quiz-answer">{st.session_state.lect_script["quiz"][i]["answer"]}</div>'
            
            answers_content_placeholder.markdown(answers_content, unsafe_allow_html=True)
    
if __name__ == "__main__":
    main()