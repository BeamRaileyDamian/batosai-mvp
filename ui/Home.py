from utils import *
import streamlit as st

import sys
import pysqlite3
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

def main():
    setup("bat.OS.AI")
    st.title("💡 Welcome to bat.OS.AI!")
    fetch_module_numbers()
    fetch_lect_ids()
    sort_lectures(st.session_state.lect_ids, st.session_state.module_numbers)

    st.markdown(
        """
        bat.OS.AI is your intelligent tutor, designed to make asynchronous learning of **CMSC 125 (Operating Systems)** engaging and effective.  
        Using cutting-edge AI technology, bat.OS.AI provides tutoring experiences through lesson materials and an AI-powered chatbot.  

        ### 🚀 **Key Features**
        - **📚 Lesson Materials:** Access comprehensive lessons covering various Operating Systems topics, designed to help you grasp concepts easily.  
        - **💬 AI Chatbot:** Ask questions anytime! The AI chatbot is available to provide explanations, clarify doubts, and offer further insights.  
        - **🧑‍🏫 The "JACH" Experience:** Immerse yourself in lectures modeled after **Sir JACH's** signature teaching style. With his familiar face, voice, iconic quotes, and thoughtfully designed quizzes, it's like learning directly from Sir JACH himself.  
        - **⬇️ Download Materials:** Need offline access of the PDF files? Head to the **Materials** tab to download course resources for studying at your convenience.  

        ### 🛠️ **How to Use bat.OS.AI**
        - 🧑‍💻 **Explore Lessons:** Click on any available lesson to dive into the study material. Each lesson is carefully structured for optimal learning.  
        - ❓ **Ask Questions:** If something is unclear, simply use the chatbot to ask questions related to the current lesson or any OS concept.  
        - 📥 **Download Resources:** Navigate to the **Materials** tab to download lecture slides, handouts, and additional references.  

        Ready to enhance your learning journey? **Select a lesson to get started!** ⚔️
        """
    )


if __name__ == "__main__":
    main()