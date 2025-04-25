import os
import chromadb
from config import *
import streamlit as st
from dotenv import load_dotenv
from chromadb.config import Settings

def chromadbClient():
    load_dotenv(dotenv_path=".env", override=True)
    chroma_client = chromadb.HttpClient(
        settings=Settings(
            chroma_api_impl="rest",
            chroma_server_host=st.secrets["AWS_IP_ADDR"],
            chroma_server_http_port="8000"
        ),
        host=st.secrets["AWS_IP_ADDR"],
        port=8000
    )
    print(chroma_client.heartbeat())
    return chroma_client

def listCollections(client):
    collections = client.list_collections()
    return collections

def listDocuments(client, collection_name):
    collection = client.get_collection(collection_name)
    documents = collection.get()['documents']
    return documents

def deleteCollection(client, collectionName):
    try:
        client.delete_collection(collectionName)
        print(f"Collection '{collectionName}' deleted successfully")
        return True
    except Exception as e:
        print(f"Error deleting collection '{collectionName}': {e}")
        return False

def main():
    client = chromadbClient()
    collections = listCollections(client)
    print(collections)
    if collections:
        print(len(listDocuments(client, "cmsc125")))

if __name__ == "__main__":
    main()
