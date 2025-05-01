import os
import sys
import time
from utils import *
import streamlit as st
from streamlit_lottie import st_lottie
from audio_component import audio_player
from streamlit_pdf_viewer import pdf_viewer

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../assets')))

def main():
    if not "curr_lect" in st.session_state or not st.session_state.curr_lect or not "lect_script" in st.session_state or not st.session_state.lect_script: 
        st.switch_page("pages/modules.py")
    
    setup(st.session_state.curr_lect)
    if st.session_state.curr_lect not in st.session_state.curr_slide: st.session_state.curr_slide[st.session_state.curr_lect] = 0
    if "countdown" not in st.session_state: st.session_state.countdown = 60

    if st.session_state.screen_width:
        col1, col2 = st.columns([0.85, 0.15], border=False)
        col1_placeholder = st.empty()
        col2_placeholder = st.empty()
        transcript_placeholder = st.empty()

        if st.session_state.curr_slide[st.session_state.curr_lect] < st.session_state.lect_script["slides_count"]:
            with col1:
                col1_placeholder = st.empty()
            
            with col2:
                col2_placeholder = st.empty()
                transcript_placeholder = st.empty()

            with col1:
                with col1_placeholder:
                    pdf_viewer(
                        input=st.session_state.pdf_response.content, 
                        width=int(st.session_state.screen_width*0.85),
                        pages_to_render=[st.session_state.curr_slide[st.session_state.curr_lect]+1],
                        render_text=True,
                        key=f"slide_{st.session_state.curr_slide[st.session_state.curr_lect]}"
                    )

            with col2_placeholder:
                #st_lottie(st.session_state.avatar_url_json, key=f"small_lottie_{st.session_state.curr_slide[st.session_state.curr_lect]}", width=int(st.session_state.screen_width*0.12))
                st.image("assets/wow.gif", width=int(st.session_state.screen_width*0.12))

            try:
                mp3_url = st.session_state.lect_script["script"][st.session_state.curr_slide[st.session_state.curr_lect]]["audio"]          

                if f"audio_done_{st.session_state.curr_lect}_{st.session_state.curr_slide[st.session_state.curr_lect]}" not in st.session_state:
                    st.session_state[f"audio_done_{st.session_state.curr_lect}_{st.session_state.curr_slide[st.session_state.curr_lect]}"] = False

                if not st.session_state[f"audio_done_{st.session_state.curr_lect}_{st.session_state.curr_slide[st.session_state.curr_lect]}"]:
                    result = audio_player(mp3_url, key=f"audio_{st.session_state.curr_lect}_{st.session_state.curr_slide[st.session_state.curr_lect]}")

                    if result:
                        if result.get("event") == "audio_ended":
                            st.session_state[f"audio_done_{st.session_state.curr_lect}_{st.session_state.curr_slide[st.session_state.curr_lect]}"] = True
                
                if st.session_state[f"audio_done_{st.session_state.curr_lect}_{st.session_state.curr_slide[st.session_state.curr_lect]}"]:
                    st.session_state.curr_slide[st.session_state.curr_lect] += 1
                    transcript_placeholder.empty()
                    col1_placeholder.empty()
                    col2_placeholder.empty()
                    st.rerun()

            except Exception as e:
                st.error(f'Error playing: {e}')

            with transcript_placeholder:
                transcript_text = st.session_state.lect_script["script"][st.session_state.curr_slide[st.session_state.curr_lect]]["script"]
                duration = st.session_state.lect_script["script"][st.session_state.curr_slide[st.session_state.curr_lect]]["duration"] + 5
                st.markdown(f'<div class="transcript-container"><div class="transcript-text" style="animation: autoscroll {duration}s linear forwards;">{transcript_text}</div></div>', unsafe_allow_html=True)

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
                    <div style="color: #e0e0e0; text-align: center; font-weight: bold; font-size: 25px; margin-top: 20px;">{st.session_state.quote}</div>
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
            st.session_state.curr_slide[st.session_state.curr_lect] = 0
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