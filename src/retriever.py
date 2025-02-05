import os
import sys
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from config import *
from lect_gen import create_model
from embedder import get_embedding_function

def create_retriever(collection_name):
    vectorstore = Chroma(persist_directory=f'{CHROMA_PATH}/{collection_name}', embedding_function=get_embedding_function())
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    return retriever

def retriever_setup(collection_name):
    load_dotenv()
    groq_api_key = os.environ.get('GROQ_API_KEY')
    return create_retriever(collection_name), groq_api_key

def create_template():
    PROMPT_TEMPLATE = """
    Answer the question based only on the following context. The following data should be treated as facts you are familiar with:

    {context}

    ---

    Answer the question based on the above context without mentioning that these were provided to you just now: {question}.
    """
    return ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

def format_docs(results):
    return "\n\n".join(doc.page_content for doc in results)

def rag_pipeline(query_text, retriever, groq_api_key):
    rag_chain = (
        {
            "context": retriever | format_docs, 
            "question": RunnablePassthrough(),
        }
        | create_template()
        | create_model(groq_api_key)
        | StrOutputParser()
    )
    response = rag_chain.invoke(query_text)
    return response