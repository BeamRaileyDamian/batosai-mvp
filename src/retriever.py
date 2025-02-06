import os
import sys
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from config import *
from lect_gen import create_model
from embedder import get_embedding_function

def create_retriever(collection_name):
    vectorstore = Chroma(persist_directory=f'{CHROMA_PATH}/{collection_name}', 
                        embedding_function=get_embedding_function())
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

def retriever_setup(collection_name):
    load_dotenv()
    return create_retriever(collection_name), os.environ.get('GROQ_API_KEY')

def create_template():
    PROMPT_TEMPLATE = """
    Answer the question based only on the following context. The following data should be treated as facts you are familiar with:

    {context}

    ---

    Answer the question based on the above context without mentioning that these were provided to you just now: {question}.
    """
    return ChatPromptTemplate.from_messages([
        ("system", PROMPT_TEMPLATE),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ])

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def rag_pipeline(query_text, retriever, groq_api_key, chat_history):
    # Retrieve relevant context
    context = retriever.invoke(query_text)
    formatted_context = format_docs(context)
    
    # Create processing chain
    chain = (
        RunnablePassthrough.assign(context=lambda _: formatted_context)
        | create_template()
        | create_model(groq_api_key)
        | StrOutputParser()
    )
    
    # Invoke chain with chat history
    response = chain.invoke({
        "question": query_text,
        "context": formatted_context,
        "chat_history": chat_history
    })
    
    # Update chat history
    updated_history = chat_history + [
        HumanMessage(content=query_text),
        AIMessage(content=response)
    ]
    
    return response, updated_history