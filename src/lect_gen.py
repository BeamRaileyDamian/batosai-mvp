import os
import sys
import pymupdf
import firebase_admin
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from supabase import create_client, Client
from firebase_admin import credentials, firestore

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

def upload_pdf(file, storage_path, supabase_url, supabase_api_key, bucket_name):
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


def lect_gen(file, filename, lect_title):
    load_dotenv()
    lect_script = []

    # Load the LLM
    groq_api_key = os.environ.get('GROQ_API_KEY')
    llm = create_model(groq_api_key)
    
    # Open the PDF file and generate the lecture scripts
    doc = pymupdf.open(stream=file)
    for i in range(len(doc)):
        prev_slide = "None"
        next_slide = "None"
        current_slide = doc[i].get_text()
        if i > 0: prev_slide = lect_script[i-1]
        if i < len(doc) - 1: next_slide = doc[i+1].get_text()

        response = script_gen(llm, prev_slide, current_slide, next_slide)
        if response: 
            lect_script.append(response)
            break ######################
        else: return False

    # Initialize Supabase
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_api_key = os.environ.get("SUPABASE_API_KEY")
    bucket_name = os.environ.get("BUCKET_NAME")
    bucket_folder = os.environ.get("BUCKET_FOLDER")

    # Upload PDF file
    bucket_storage_path = f"{bucket_folder}/{filename}"
    publicUrl = upload_pdf(file, bucket_storage_path, supabase_url, supabase_api_key, bucket_name)
    if not publicUrl: return False

    # Initialize Firebase Firestore
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_config.json")
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