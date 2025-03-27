import time
import random
import base64
import requests
from utils import *
import streamlit as st
import streamlit_js_eval
from streamlit_lottie import st_lottie
from streamlit_pdf_viewer import pdf_viewer

def apply_styles():
    st.markdown("""
        <style>
        .transcript-container {
            background-color: #f8f9fa;
            border-radius: 5px;
            color: #4b644c;
            padding: 10px;
            margin-top: 10px;
            border-left: 3px solid #4682b4;
            max-height: 550px;
            overflow-y: auto;
        }
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
                
        button {
            width: 35% !important;
            display: flex !important;
            justify-content: flex-start !important;
            text-align: left !important;
            white-space: normal !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
            background-color: #486f4f !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 10px 15px !important;
            border: 1px solid #284329 !important;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2) !important; 
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
    if "countdown" not in st.session_state: st.session_state.countdown = 3

    avatar_url = requests.get(st.secrets["GIF"]) 
    avatar_url_json = dict() 
    if avatar_url.status_code == 200: avatar_url_json = avatar_url.json() 
    else: print("Error in the URL") 

    quote = get_quote()
    apply_styles()

    if screen_width:
        col1, col2 = st.columns([0.85, 0.15], border=False)
        with col1:
            col1_placeholder = st.empty()
        
        with col2:
            col2_placeholder = st.empty()
            transcript_placeholder = st.empty()
        
        first_slide_relative = True
        for st.session_state.curr_slide in range(st.session_state.curr_slide, st.session_state.lect_script["slides_count"]):
            if first_slide_relative:
                first_slide_relative = False
                with col2_placeholder:
                    st_lottie(avatar_url_json, key=f"small_lottie_{st.session_state.curr_slide}", width=int(screen_width*0.15))

                    with transcript_placeholder:
                        transcript_text = st.session_state.lect_script["script"][st.session_state.curr_slide]["script"]
                        st.markdown(f'<div class="transcript-container">{transcript_text}</div>', unsafe_allow_html=True)

            with col1:
                with col1_placeholder:
                    pdf_viewer(
                        input=response.content, 
                        width=int(screen_width*0.85),
                        pages_to_render=[st.session_state.curr_slide+1],
                        render_text=True
                    )
            
            try:
                mp3_url = st.session_state.lect_script["script"][st.session_state.curr_slide]["audio"]
                duration = st.session_state.lect_script["script"][st.session_state.curr_slide]["duration"]
                
                with transcript_placeholder:
                    transcript_text = st.session_state.lect_script["script"][st.session_state.curr_slide]["script"]
                    st.markdown(f'<div class="transcript-container">{transcript_text}</div>', unsafe_allow_html=True)
                
                audio_html = f'''
                    <audio autoplay>
                        <source src="{mp3_url}" type="audio/mp3">
                        Your browser does not support the audio element.
                    </audio>
                '''
                
                st.markdown(audio_html, unsafe_allow_html=True)
                time.sleep(duration + 2)
                
            except Exception as e:
                st.error(f'Error playing: {e}')

        with col1_placeholder:
            st.empty()

        with col2_placeholder:
            st.empty()
            
        with transcript_placeholder:
            st.empty()

        ################# CHECK NOTES #####################
        # Use placeholders for the notes review content so we can clear them later
        with col1:
            notes_header_placeholder = st.empty()
            quote_placeholder = st.empty()
            
            # Fill the placeholders with content
            notes_header_placeholder.header("Review your notes in preparation for a quiz! 🧠")
            quote_placeholder.subheader(quote)

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
        quote_placeholder.empty()
        
        ################# QUIZ ############################
        st.session_state.countdown = 3
        
        # Create placeholders for quiz content
        with col1:
            quiz_header_placeholder = st.empty()
            quiz_content_placeholder = st.empty()
            
            # Display quiz header and questions
            quiz_header_placeholder.header("Quiz Time! 📝")
            
            quiz_content = ""
            for i in range(len(st.session_state.lect_script["quiz"])):
                quiz_content += f'<div class="quiz-question">{i+1}. {st.session_state.lect_script["quiz"][i]["question"]}</div>'
            
            quiz_content_placeholder.markdown(quiz_content, unsafe_allow_html=True)

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
        quiz_content_placeholder.empty()
        st.session_state.curr_slide = 0
        st.session_state.countdown = 3
        
        with col1:
            answers_header_placeholder = st.empty()
            answers_content_placeholder = st.empty()
            
            answers_header_placeholder.header("Quiz Answers 🎓")
            
            answers_content = ""
            for i in range(len(st.session_state.lect_script["quiz"])):
                answers_content += f'<div class="quiz-question">{i+1}. {st.session_state.lect_script["quiz"][i]["question"]}</div>'
                answers_content += f'<div class="quiz-answer">{st.session_state.lect_script["quiz"][i]["answer"]}</div>'
            
            answers_content_placeholder.markdown(answers_content, unsafe_allow_html=True)

        with col2:
            with timer_placeholder: st.empty()
            st.page_link("pages/modules.py", label="Back to Lessons")
    
if __name__ == "__main__":
    main()