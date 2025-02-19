import os
import io
import uuid
import sys
import pymupdf
import firebase_admin
from gtts import gTTS
import streamlit as st
from langchain_groq import ChatGroq
from firebase_admin import firestore
from pydub import AudioSegment, effects
from supabase import create_client, Client

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from config import *

def pre_template(curr):
    return f"""

    """

def post_template(content):
    return f"""
        Context:
        - You are given an AI-generated script that would be used for text-to-speech
        - Clean it by removing AI-generated leading or introductory phrases such as 'Here is the generated script'
        - Remove also the symbols and special characters that text-to-speech software would speak out loud

        Input to clean:
        - {content} 
    """

def first_slide(text):
    return f"""
        Context:
        - You are a lecturer generating a script to explain the content of one presentation slide in a lecture setting.
        - This slide is the title or the first slide, so you only need to introduce it really shallowly.

        Title Slide:
        - {text}
    """

def main_template(prev, curr, next):
    return f"""
        Context:
        - You are a lecturer generating a script to explain the content of one presentation slide in a lecture setting.
        - The lecture style is instructional, aimed at students with beginner knowledge of the topic.
        - The script should be at most 120 words.
        - In generating the script, you could read some of the points in the slide like a lecturer does.

        Slide Content:
        - Current Slide: {curr}
        - Full Script from Previous Slide: {prev}
        - Next Slide: {next}

        Structure and Emphasis:
        1. Introduction: Briefly introduce the main idea of the current slide, building naturally on the previous script.
        2. Key Details: Explain key points clearly and concisely. Maintain the style established in the previous script.
        3. Transition to Next Slide: Conclude with a statement or question that connects to the next slide's content.

        Extra Instructions:
        - Use analogies, examples, or comparisons where useful to simplify complex ideas.
        - Focus on fresh content while keeping continuity with the previous slide's script.
        - Focus on clarity and accessibility, assuming the student is encountering this material for the first time.

        Generate the script for the current slide based on these instructions.
    """

def create_model(groq_api_key):
    return ChatGroq(
        groq_api_key=groq_api_key,
        model_name=LLM_MODEL,     
        temperature=0
    )

def upload_to_supabase(file, storage_path, supabase_url, supabase_api_key, bucket_name):
    supabase: Client = create_client(supabase_url, supabase_api_key)
    try:
        supabase.storage.from_(bucket_name).upload(storage_path, file)
        public_url = supabase.storage.from_(bucket_name).get_public_url(storage_path)
        if public_url.endswith("?"): public_url = public_url[:-1]
        return public_url
    except Exception as e:
        if e.to_dict()["code"] == "Duplicate":
            public_url = supabase.storage.from_(bucket_name).get_public_url(storage_path)
            if public_url.endswith("?"): public_url = public_url[:-1]
            return public_url
        return False

def script_gen(llm, prev_slide, current_slide, next_slide):
    # preprocessing
    

    # main
    message = None
    raw_response = None
    if prev_slide == "None":
        message = first_slide(current_slide)
    else: 
        message = main_template(prev_slide, current_slide, next_slide)

    try: 
        raw_response = llm.invoke(message).content
    except Exception as e:
        print(e)
        return False
    
    # postprocessing
    try: 
        post_message = post_template(raw_response)
        response = llm.invoke(post_message).content
        return response
    except Exception as e:
        print(e)
        return False

def tts_and_upload(text, bucket_folder, lect_title, supabase_url, supabase_api_key, bucket_name, lang="en"):
    # Generate TTS audio
    tts = gTTS(text=text, lang=lang)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    
    audio = AudioSegment.from_file(fp, format="mp3")
    audio = effects.speedup(audio, playback_speed=1.1)
    duration = audio.duration_seconds
    filename = f"{uuid.uuid4()}.mp3"
    file_bytes = audio.export(format="mp3").read()

    public_url = upload_to_supabase(file_bytes, f"{bucket_folder}/{lect_title}/{filename}", supabase_url, supabase_api_key, bucket_name)
    return public_url, duration

def lect_gen(file, filename, lect_title):
    lect_script = []

    # Load the LLM
    groq_api_key = st.secrets['GROQ_API_KEY']
    llm = create_model(groq_api_key)

    # Initialize Supabase
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_api_key = st.secrets["SUPABASE_API_KEY"]
    bucket_name = st.secrets["BUCKET_NAME"]
    bucket_folder_pdf = st.secrets["BUCKET_FOLDER_PDF"]
    bucket_folder_audio = st.secrets["BUCKET_FOLDER_AUDIO"]
    
    # Open the PDF file and generate the lecture scripts
    doc = pymupdf.open(stream=file)
    for i in range(len(doc)):
        prev_slide = "None"
        next_slide = "None"
        current_slide = doc[i].get_text()
        if i > 0: prev_slide = lect_script[i-1]
        if i < len(doc) - 1: next_slide = doc[i+1].get_text()

        script = script_gen(llm, prev_slide, current_slide, next_slide)
        if not script: return False

        public_url_audio, duration = tts_and_upload(script, bucket_folder_audio, lect_title, supabase_url, supabase_api_key, bucket_name)
        if not public_url_audio: return False

        lect_script.append({
            "script": script,
            "audio": public_url_audio,
            "duration": duration
        })
        break ######################

    # Upload PDF file
    bucket_storage_path = f"{bucket_folder_pdf}/{filename}"
    publicUrl = upload_to_supabase(file, bucket_storage_path, supabase_url, supabase_api_key, bucket_name)
    if not publicUrl: return False

    # Initialize Firebase Firestore
    if not firebase_admin._apps:
        cred = st.secrets["firebase"]["proj_settings"]
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    # Upload lecture script
    lecture = {
        "title": lect_title,
        "script": lect_script,
        "pdf": filename,
        "pdf_url": publicUrl,
        "slides_count": doc.page_count
    }

    try:
        db.collection("lect_scripts").document(lect_title).set(lecture)
        return True
    except Exception as e:
        print(e)
        return False    

if __name__ == "__main__":
    lect_gen()