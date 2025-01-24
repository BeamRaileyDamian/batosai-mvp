import streamlit as st
from gtts import gTTS
import io
import base64

def text_to_speech(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    audio_base64 = base64.b64encode(fp.read()).decode('utf-8')
    return audio_base64

def main():
    st.title('Text-to-Speech Converter')
    
    text = st.text_area('Enter text to convert to speech')
    
    lang = st.selectbox('Select Language', 
        ['en', 'fr', 'es', 'de', 'it', 'ja', 'ko', 'zh-CN', 'ru']
    )
    
    if st.button('Convert to Speech'):
        if text:
            try:
                audio_base64 = text_to_speech(text, lang)
                
                audio_html = f'''
                    <audio autoplay>
                        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                        Your browser does not support the audio element.
                    </audio>
                '''
                
                st.markdown(audio_html, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f'Error converting text to speech: {e}')
        else:
            st.warning('Please enter some text')

if __name__ == '__main__':
    main()