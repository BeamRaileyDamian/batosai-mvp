import os
import sys
import requests
from langchain_chroma import Chroma
import streamlit as st
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
    return create_retriever(collection_name), st.secrets['GROQ_API_KEY']

def rerank(documents, query):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['JINA_API_KEY']}"
    }
    
    # Create documents with both content and metadata
    docs_with_metadata = [
        {
            "text": doc.page_content,
            "metadata": doc.metadata
        } for doc in documents
    ]
    
    data = {
        "model": RERANKING_MODEL,
        "query": query,
        "top_n": 5,
        "documents": [doc["text"] for doc in docs_with_metadata]
    }
    
    response = requests.post(JINA_URL, headers=headers, json=data)
    results = response.json()["results"]
    
    # Map the reranked results back to the original documents with metadata
    reranked_docs = []
    for result in results:
        idx = result["index"]  # Get the original index
        reranked_docs.append({
            "document": {
                "text": docs_with_metadata[idx]["text"],
                "metadata": docs_with_metadata[idx]["metadata"]
            },
            "relevance_score": result["relevance_score"]
        })
    
    return reranked_docs

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
    formatted_texts = []
    for doc in docs:
        text = doc["document"]["text"]
        formatted_texts.append(text)
    return "\n\n".join(formatted_texts), [doc["document"]["metadata"] for doc in docs]

def rag_pipeline(query_text, retriever, groq_api_key, chat_history):
    llm = create_model(groq_api_key)
    if not is_relevant(query_text, llm):
        response = unable_to_answer(query_text, llm)
        updated_history = chat_history + [
            HumanMessage(content=query_text),
            AIMessage(content=response)
        ]
        return response, updated_history
    
    # Retrieve relevant context
    context = retriever.invoke(query_text)
    # rerank and filter
    filtered_docs = rerank(context, query_text)
    relevance_scores = [round(i["relevance_score"] * 100, 2) for i in filtered_docs]
    formatted_context, sources = format_docs(filtered_docs)

    chain = (
        RunnablePassthrough.assign(context=lambda _: formatted_context)
        | create_template()
        | llm
        | StrOutputParser()
        | (lambda response: post_clean(response, llm))
    ).with_config({"tracing": True})
    
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
    
    return response, updated_history, sources, relevance_scores