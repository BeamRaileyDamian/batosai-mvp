import streamlit as st
import speech_recognition as sr

def transcribe_audio():
    """
    Function to transcribe audio using speech recognition
    """
    # Initialize recognizer
    recognizer = sr.Recognizer()
    
    # Use microphone as source
    with sr.Microphone() as source:
        st.write("Listening... Please speak.")
        
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        try:
            # Listen for audio input
            audio = recognizer.listen(source, timeout=5)
            
            # Recognize speech using Google Speech Recognition
            try:
                text = recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return "Sorry, could not understand audio"
            except sr.RequestError as e:
                return f"Could not request results; {e}"
        
        except sr.WaitTimeoutError:
            return "No speech detected. Timeout occurred."

def main():
    """
    Main Streamlit application
    """
    st.title("Speech Recognition App")
    
    # Add a button to start recording
    if st.button("Start Recording"):
        # Transcribe audio
        transcription = transcribe_audio()
        
        # Display transcription
        st.write("Transcription:")
        st.text_area("Recognized Text", value=transcription, height=100)

if __name__ == "__main__":
    main()