import os
import pymupdf
import firebase_admin
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from supabase import create_client, Client
from firebase_admin import credentials, firestore

def template(prev, curr, next):
    return f"""
        Context:
        - You are a lecturer generating a script to explain the content of one presentation slide in a lecture setting.
        - The lecture style is instructional, aimed at students with beginner knowledge of the topic.
        - The script should be at most 120 words.

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
        model_name='llama-3.1-8b-instant',
        temperature=0
    )

def upload_pdf(file, storage_path, supabase_url, supabase_api_key, bucket_name):
    supabase: Client = create_client(supabase_url, supabase_api_key)
    try:
        supabase.storage.from_(bucket_name).upload(storage_path, file)
        return True
    except:
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
        
        message = template(prev_slide, current_slide, next_slide)
        try: 
            response = llm.invoke(message).content
        except:
            return False
        lect_script.append(response)

    # Initialize Firebase Firestore
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_config.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    # Upload lecture script
    lecture = {
        "title": lect_title,
        "script": lect_script,
        "pdf": filename
    }

    try:
        db.collection("lect_scripts").document(lect_title).set(lecture)
    except:
        return False

    # Initialize Supabase
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_api_key = os.environ.get("SUPABASE_API_KEY")
    bucket_name = os.environ.get("BUCKET_NAME")
    bucket_folder = os.environ.get("BUCKET_FOLDER")

    # Upload PDF file
    bucket_storage_path = f"{bucket_folder}/{filename}"
    result = upload_pdf(file, bucket_storage_path, supabase_url, supabase_api_key, bucket_name)
    return result

if __name__ == "__main__":
    lect_gen()