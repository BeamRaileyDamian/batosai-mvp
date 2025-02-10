import os
import sys
import requests
from dotenv import load_dotenv
from langchain_chroma import Chroma
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
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})

def retriever_setup(collection_name):
    load_dotenv()
    return create_retriever(collection_name), os.environ.get('GROQ_API_KEY')

def rerank(documents, query):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ.get('JINA_API_KEY')}"
    }

    data = {
        "model": RERANKING_MODEL,
        "query": query,
        "top_n": 5,
        "documents": documents
    }

    response = requests.post(JINA_URL, headers=headers, json=data)
    return response.json()["results"]

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

def is_relevant(query, llm):
    prompt = f"""
    You are an intelligent tutor for a course on Operating Systems.
    Your task is to determine whether the given question is relevant to the subject and if it is academic in nature and not asking for the answer to an exam or quiz question.

    Question: "{query}"

    Answer only with "yes" if it is relevant and "no" if it is not.
    """

    response = llm.invoke(prompt)
    return "yes" in response.content.lower()

def unable_to_answer(query, llm):
    prompt = f"""
    You are an intelligent tutor for a course on Operating Systems.
    Say that you are unable to answer the following question due to your scope and ethics, if it applies.

    Question: "{query}"
    """

    response = llm.invoke(prompt)
    return response.content

def post_clean(query, llm):
    prompt = f"""
    You are an AI assistant refining a response to remove any mention of external knowledge sources.  
    Revise the response to sound natural, as if the AI knew the answer without retrieving documents.  
    Remove or rewrite phrases such as:
    - "Based on the provided context"
    - "According to the retrieved documents"
    - "From my available sources"
    - "I found in the documents"
    - "From external sources"
    - "The data indicates"

    **Original Response:**  
    {query}

    **Cleaned Response:**  
    """

    response = llm.invoke(prompt)
    return response.content

def format_docs(docs):
    return "\n\n".join(doc["document"]["text"] for doc in docs)

def rag_pipeline(query_text, retriever, groq_api_key, chat_history):
    # Retrieve relevant context
    context = retriever.invoke(query_text)
    # rerank and filter
    filtered_docs = rerank([doc.page_content for doc in context], query_text)
    formatted_context = format_docs(filtered_docs)

    llm = create_model(groq_api_key)

    if not is_relevant(query_text, llm):
        response = unable_to_answer(query_text, llm)
        updated_history = chat_history + [
            HumanMessage(content=query_text),
            AIMessage(content=response)
        ]
        return response, updated_history

    chain = (
        RunnablePassthrough.assign(context=lambda _: formatted_context)
        | create_template()
        | llm
        | StrOutputParser()
        | (lambda response: post_clean(response, llm))
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