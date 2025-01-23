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

def setup():
    load_dotenv()
    groq_api_key = os.environ.get('GROQ_API_KEY')
    if not groq_api_key: raise ValueError("API key for Groq is not set in environment variables")
    return groq_api_key

def create_model(groq_api_key):
    return ChatGroq(
        groq_api_key=groq_api_key,
        model_name='llama-3.1-8b-instant',
        temperature=0
    )

def upload_pdf(file_path, storage_path, supabase_url, supabase_api_key, bucket_name):
    supabase: Client = create_client(supabase_url, supabase_api_key)
    try:
        with open(file_path, "rb") as file:
            response = supabase.storage.from_(bucket_name).upload(storage_path, file)
        return response
    except Exception as e:
        return {"error": str(e)}

def lect_gen():
    folder_path = "data"
    files = os.listdir(folder_path)
    lect_script = []

    for i, file in enumerate(files):
        print(f"\t[{i}] {file}")
    choice = input("File: ")

    llm_key = setup()
    llm = create_model(llm_key)
    
    doc = pymupdf.open(f"{folder_path}\\{files[int(choice)]}")
    for i in range(len(doc)):
        prev_slide = "None"
        next_slide = "None"
        current_slide = doc[i].get_text()
        if i > 0: prev_slide = lect_script[i-1]
        if i < len(doc) - 1: next_slide = doc[i+1].get_text()
        
        message = template(prev_slide, current_slide, next_slide)
        response = llm.invoke(message).content
        lect_script.append(response)

    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    lecture = {
        "title": f"{files[int(choice)]}",
        "script": lect_script
    }
    db.collection("lect_scripts").document(f"{files[int(choice)]}").set(lecture)

    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_api_key = os.environ.get("SUPABASE_API_KEY")
    bucket_name = os.environ.get("BUCKET_NAME")
    bucket_folder = os.environ.get("BUCKET_FOLDER")

    local_pdf_path = f"{folder_path}\\{files[int(choice)]}"
    bucket_storage_path = f"{bucket_folder}/{files[int(choice)]}"
    result = upload_pdf(local_pdf_path, bucket_storage_path, supabase_url, supabase_api_key, bucket_name)
    print(result)

if __name__ == "__main__":
    lect_gen()