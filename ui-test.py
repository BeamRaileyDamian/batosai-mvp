import streamlit as st
import streamlit_js_eval
from streamlit_pdf_viewer import pdf_viewer

st.set_page_config(layout="wide")
# from url
import requests
url = "https://gisdypsqimhoyclwsepf.supabase.co/storage/v1/object/public/presentations/pdfs/06.Mechanism_Limited_Direct_Execution.pdf"
response = requests.get(url)
pdf_viewer(input=response.content, width=5000)

# screen_width = streamlit_js_eval.streamlit_js_eval(js_expressions='screen.width', key = 'SCR')
# pdf_viewer(input="data\\04.The_abstraction_the_process.pdf",
#            pages_to_render=[1],
#            render_text=True,
#            width=int(screen_width*0.8))