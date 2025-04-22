import base64
import os
import io
import sys
import uuid
import fitz
import pytesseract
from PIL import Image
import firebase_admin
from gtts import gTTS
from math import ceil
import streamlit as st
from json import loads
from speechify import Speechify
from langchain_groq import ChatGroq
from firebase_admin import firestore
from pydub import AudioSegment, effects
from supabase import create_client, Client
from google.cloud.firestore_v1 import FieldFilter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from config import *

def personality_prompt(lect_personality):  
    return f"Your personality traits: {lect_personality}. Maintain a balanced approach: while these traits should shape your style, your primary role is to be an effective lecturer."

def post_template(content):
    return f"""
        Context:
        - You are given an AI-generated script that would be used for text-to-speech
        - Clean it by removing AI-generated leading or introductory phrases such as 'Here is the generated script'
        - Remove also the symbols and special characters that text-to-speech software would speak out loud

        Input to clean:
        - {content} 
    """

def few_shot_samples():
    return f"""
        Here are some few-shot samples for you to learn from.

        Sample 1:
            Actual Slide Content: 
                What a happens when a program runs?
                A running program executes instructions.
                    1. The processor fetches an instruction from memory.
                    2. Decode: Figure out which instruction this is
                    3. Execute: i.e., add two numbers, access memory, check a condition, jump to function, and so forth.
                    4. The processor moves on to the next instruction and so on (until completion).
                This is the Von Neumann model of computing.
            Script:
                So, in this, let's take a look at what happens when a program runs. I'm sure everyone is familiar with these steps already because you have taken several CompSci courses already, but let's have a review.
                So when a program runs, it executes instructions, and it is the processor that fetches the instruction from memory.
                In the case of x86-64, which is the ISA that you studied in CompSci 131, we have a special register called the instruction pointer, which basically contains the address of the next instruction to be executed.
                Now, once that instruction is fetched, it will be decoded to figure out which instruction this is and after it has determined the operation or instruction—so usually, you are given the code, right?—then your code will be decoded, and the particular specific instruction will be extracted and executed.
                For example, if you have an ADD instruction or a MOVE instruction, these instructions are implemented at the hardware level. So, for example, if you have another instruction, at the circuit level, it will be implemented as a full adder, as you discussed in CompSci 130.
                After the execution of this instruction, the next instruction will be fetched, and the process continues. This is called the von Neumann architecture, which is the model of computing that is being implemented in the computers that we have today.

        Sample 2:
            Actual Slide Content:
                Tracing Process States: CPU Only
                o Assumes a single processor is available
                Time Process0 Process1 Notes
                1 Running Ready
                2 Running Ready
                3 Running Ready
                4 Running Ready Process0 now done
                5 - Running
                6 - Running
                7 - Running
                8 - Running Process1 now done
            Script:
                Let's take a look at an example here: tracing process states.
                The assumption here is that we have a single processor.
                This is our notation: we have four columns—Time, Process 0, Process 1, and some notes. We have two processes and a timeline.
                At time 1, Process 0 is running. Its state is "Running." Since we only have a single processor, Process 1 will be in the "Ready" state because we can only run one process at a time.
                At time 2, Process 0 is still running.
                At time 3, Process 0 is still running.
                At time 4, Process 0 is now complete, meaning it has finished its task and is terminated.
                Since Process 0 is done, we can now run the second process, Process 1.
                At times 5, 6, 7, and 8, Process 1 runs until it is also completed.
                This is how we represent the execution and transition of process states, assuming a single processor.
                Also, in this example, there are no I/O operations—only CPU operations. So, these states refer specifically to execution on the CPU.
    """

def first_slide_no_prev(curr, next, lect_personality):
    return f"""
        Context:
        - You are Sir Jac, a lecturer generating a script to introduce the first slide of a presentation.
        - Since this is the title slide, provide only a brief introduction to the lecture.
        - Conclude with a smooth and concise transition to the next slide.
        - {personality_prompt(lect_personality)}

        Title Slide Content:
        - {curr}

        Next Slide Preview:
        - {next}

        Instructions:
        - Keep the introduction engaging but shallow.
        - Ensure a natural and brief transition to the next slide.
    """

def first_slide_with_prev(curr, next, prev_lesson, lect_personality):
    return f"""
        Context:
        - You are Sir Jac, a lecturer generating a script to introduce the first slide of a presentation.
        - Since this is the title slide, provide only a brief introduction to the lecture.
        - A summary of the previous lesson is provided. Briefly reference it (at most 3 sentences) using a natural transition (e.g., "In the previous lesson, we explored ___. Today, we will discuss ___.").
        - Conclude with a smooth and concise transition to the next slide.
        - {personality_prompt(lect_personality)}

        Previous Lesson Summary:
        - {prev_lesson}

        Title Slide Content:
        - {curr}

        Next Slide Preview:
        - {next}

        Instructions:
        - Keep the introduction engaging but concise.
        - Reference the previous lesson naturally and briefly.
        - Ensure a smooth transition to the next slide.
    """

def main_template(prev, curr, next, lect_personality):
    return f"""
        Context:
        - You are Sir Jac, a lecturer generating a script to explain the content of one presentation slide in a lecture setting.
        - The lecture style is instructional, aimed at students with beginner knowledge of the topic.
        - In generating the script, you could read some of the points in the slide like a lecturer does before explaining them.
        - {personality_prompt(lect_personality)}

        Slide Content:
        - Current Slide: {curr}
        - Full Script from Previous Slide: {prev}
        - Next Slide: {next}

        Structure and Emphasis:
        1. Introduction: Briefly introduce the main idea of the current slide. 
        2. Explanation: Explain the slide content clearly.
        3. Transition to Next Slide: Conclude with a short statement or question, at most one sentence, that connects to the next slide's content. If this is the final slide, wrap it up.

        Extra Instructions:
        - Use analogies, examples, or comparisons ONLY WHEN useful to simplify complex ideas.
        - Focus on clarity and accessibility, assuming the student is encountering this material for the first time.
        
        Few-Shot Samples:
        {few_shot_samples()}
        
        Generate the script for the current slide based on these instructions.
    """

def last_slide_template(prev, curr, entire_pdf_content, lect_personality):
    return f"""
        Context:
        - You are Sir Jac, a lecturer generating a script to explain the content of one presentation slide in a lecture setting.
        - The lecture style is instructional, aimed at students with beginner knowledge of the topic.
        - In generating the script, you could read some of the points in the slide like a lecturer does before explaining them.
        - {personality_prompt(lect_personality)}

        Slide Content:
        - Current Slide: {curr}
        - Full Script from Previous Slide: {prev}

        Structure and Emphasis:
        1. Introduction: Briefly introduce the main idea of the current slide. 
        2. Explanation: Explain the slide content clearly.
        3. Transition to Next Slide: Conclude with a short statement or question, at most one sentence, that connects to the next slide's content. If this is the final slide, wrap it up.

        Extra Instructions:
        - Use analogies, examples, or comparisons ONLY WHEN useful to simplify complex ideas.
        - Focus on clarity and accessibility, assuming the student is encountering this material for the first time.
        
        Few-Shot Samples:
        {few_shot_samples()}

        This is the last slide. Wrap up the lesson at the end of the script. The whole lesson's content is shown here:\n{entire_pdf_content}
        
        Generate the script for the current slide based on these instructions.
    """

def create_model(groq_api_key):
    return ChatGroq(
        groq_api_key=groq_api_key,
        model_name=LLM_MODEL,     
        temperature=0
    )

def upload_to_supabase(file, storage_path, supabase_url, supabase_api_key, bucket_name, content_type):
    supabase: Client = create_client(supabase_url, supabase_api_key)
    
    try:
        supabase.storage.from_(bucket_name).upload(storage_path, file, {'content-type': content_type, 'upsert': 'true'})
    except Exception as e:
        error_dict = e.to_dict() if hasattr(e, "to_dict") else {}
        
        # # If file already exists, delete it first
        # if error_dict.get("code") == "Duplicate":
        #     supabase.storage.from_(bucket_name).remove([storage_path])
        #     supabase.storage.from_(bucket_name).upload(storage_path, file, {'content-type': content_type})
    
    public_url = supabase.storage.from_(bucket_name).get_public_url(storage_path)
    return public_url.rstrip("?")

def script_gen(llm, prev_slide, current_slide, next_slide, lect_personality):
    message = None
    raw_response = None
    message = main_template(prev_slide, current_slide, next_slide, lect_personality)

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
    
def script_gen_first_slide(llm, prev_lesson, current_slide, next_slide, lect_personality):
    message = None
    raw_response = None
    if prev_lesson:
        message = first_slide_with_prev(current_slide, next_slide, prev_lesson, lect_personality)
    else:
        message = first_slide_no_prev(current_slide, next_slide, lect_personality)

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

def script_gen_last_slide(llm, prev_slide, current_slide, entire_pdf_content, lect_personality):
    message = None
    raw_response = None
    message = last_slide_template(prev_slide, current_slide, entire_pdf_content, lect_personality)

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

def tts_with_speechify(text, bucket_folder, lect_title, supabase_url, supabase_api_key, bucket_name):
    client = Speechify(
        token=os.environ.get("SPEECHIFY_API_KEY"),
    )
    response = client.tts.audio.speech(
        input=text,
        voice_id=os.environ.get("SPEECHIFY_VOICE_ID"),
        audio_format="mp3"
    )

    audio = response.audio_data
    audio_bytes = base64.b64decode(audio)
    filename = f"{uuid.uuid4()}.mp3"

    audio_fp = io.BytesIO(audio_bytes)
    audio_segment = AudioSegment.from_file(audio_fp, format="mp3")
    duration = ceil(audio_segment.duration_seconds)

    public_url = upload_to_supabase(audio_bytes, f"{bucket_folder}/{lect_title}/{filename}", supabase_url, supabase_api_key, bucket_name, "audio/mpeg")
    return public_url, duration

def tts_and_upload_test(text, bucket_folder, lect_title, supabase_url, supabase_api_key, bucket_name, lang="en"):
    # Generate TTS audio
    tts = gTTS(text=text, lang=lang)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    
    audio = AudioSegment.from_file(fp, format="mp3")
    audio = effects.speedup(audio, playback_speed=5) #1.1
    duration = ceil(audio.duration_seconds)
    filename = f"{uuid.uuid4()}.mp3"
    file_bytes = audio.export(format="mp3").read()

    public_url = upload_to_supabase(file_bytes, f"{bucket_folder}/{lect_title}/{filename}", supabase_url, supabase_api_key, bucket_name, "audio/mpeg")
    return public_url, duration

def shorter(llm, script):
    prompt = f"""
        Shorten the following passage that is explaining a lecture slide. Do not summarize it too much; just shorten it by a bit.

        Passage: {script}
    """

    response = None
    try: 
        response = llm.invoke(prompt).content
    except Exception as e:
        print(e, response)
        return False

    # postprocessing
    try: 
        post_message = post_template(response)
        cleaned_response = llm.invoke(post_message).content
        if len(cleaned_response) > 2000:
            return shorter(llm, cleaned_response)
        else:
            return cleaned_response
    except Exception as e:
        print(e)
        return False

def quiz_gen(llm, pdf_content_str):
    prompt = f'''
    You are a college instructor creating a 5-question quiz on operating systems based on the provided lecture slides.

    {pdf_content_str}

    Generate 5 quiz questions focusing on key concepts from the content above.  
    - Questions should be a mix of identification, problem-solving (one word, number, or short phrase), and true/false.  
    - For problem-solving questions, ensure the given values or scenarios differ from those in the slides. Ensure that the new values still result in a correct answer by properly recalculating it.  
    - The difficulty level should be moderate (4 to 7 out of 10).  

    Provide the output **only** as a valid JSON array in the format:

    [
        {{"question": "Question text?", "answer": "Answer text"}},
        {{"question": "Question text?", "answer": "Answer text"}},
        ...
    ]

    Respond with a valid JSON array only, with no additional text, explanations, or formatting.
    '''

    response = None
    try: 
        response = llm.invoke(prompt).content
        return loads(response)
    except Exception as e:
        print(e, response)
        return False

def get_text_or_ocr(page):
    text = page.get_text("text")
        
    if len(text.split()) < 30:
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
        
        # Convert pixmap to PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        text = pytesseract.image_to_string(img)
        img.close()
    
    return text

def gen_script_and_quiz(file, lect_num, lect_personality):
    scripts = []
    entire_pdf_content = []
    test_content = []

    # Load the LLM
    groq_api_key = os.environ.get('GROQ_API_KEY')
    llm = create_model(groq_api_key)

    # Initialize Firebase Firestore
    if not firebase_admin._apps:
        cred = st.secrets["firebase"]["proj_settings"]
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    prev_module = None
    prev_module_content = None
    if lect_num:
        prev_module = db.collection("lect_scripts").where(filter=FieldFilter("module_number", "==", lect_num-1)).limit(1).get()
    if prev_module:
        first_doc = prev_module[0]  # Get the first document from the result
        prev_module_content = '\n'.join([i["script"] for i in first_doc.to_dict()["script"]])

    # Open the PDF file and generate the lecture scripts
    doc = fitz.open(stream=file)
    for i in range(len(doc)):
        prev_slide = None
        next_slide = None
        current_slide = get_text_or_ocr(doc[i])
        entire_pdf_content.append(f"{current_slide}\n----------------")
        if i > 0: prev_slide = scripts[i-1]
        if i < len(doc) - 1: next_slide = doc[i+1].get_text()

        script = None
        if i == 0:
            script = script_gen_first_slide(llm, prev_module_content, current_slide, next_slide, lect_personality)
        elif i == len(doc) - 1:
            script = script_gen_last_slide(llm, prev_module_content, current_slide, entire_pdf_content, lect_personality)
        else:
            script = script_gen(llm, prev_slide, current_slide, next_slide, lect_personality)

        if not script: return False
        if len(script) > 2000:
            script = shorter(llm, script)
        test_content.append(f"Slide {i+1}:\n{script}\n----------------")
        scripts.append(script)
    
    with open("script_generated.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(test_content))

    # generate 5-item quiz
    quiz = quiz_gen(llm, '\n'.join(entire_pdf_content))
    return scripts, quiz

def gen_audio_upload_pdf(scripts, quiz, file, filename, lect_title, lect_num):
    # Initialize Supabase
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_api_key = os.environ.get("SUPABASE_API_KEY")
    bucket_name = os.environ.get("BUCKET_NAME")
    bucket_folder_pdf = os.environ.get("BUCKET_FOLDER_PDF")
    bucket_folder_audio = os.environ.get("BUCKET_FOLDER_AUDIO")
    lect_script = []

    # Initialize Firebase Firestore
    if not firebase_admin._apps:
        cred = st.secrets["firebase"]["proj_settings"]
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    for script in scripts:
        public_url_audio, duration = tts_and_upload_test(script, bucket_folder_audio, lect_title, supabase_url, supabase_api_key, bucket_name)
        #public_url_audio, duration = tts_with_speechify(script, bucket_folder_audio, lect_title, supabase_url, supabase_api_key, bucket_name)
        if not public_url_audio: return False

        lect_script.append({
            "script": script,
            "audio": public_url_audio,
            "duration": duration
        })

    # Upload PDF file
    bucket_storage_path = f"{bucket_folder_pdf}/{lect_title}/{filename}"
    publicUrl = upload_to_supabase(file, bucket_storage_path, supabase_url, supabase_api_key, bucket_name, "application/pdf")
    if not publicUrl: return False

    doc = fitz.open(stream=file)
    # Upload lecture script
    lecture = {
        "title": lect_title,
        "module_number": lect_num,
        "script": lect_script,
        "pdf": filename,
        "pdf_url": publicUrl,
        "slides_count": doc.page_count,
        "quiz": quiz
    }

    try:
        db.collection("lect_scripts").document(lect_title).set(lecture)
        return publicUrl
    except Exception as e:
        print(e)
        return False