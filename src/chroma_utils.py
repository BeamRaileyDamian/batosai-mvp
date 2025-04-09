import chromadb
import streamlit as st
from config import *

def chromadbClient():
    chroma_client = chromadb.HttpClient(
        host=st.secrets["AWS_IP_ADDR"],
        port=8000
    )
    chroma_client.heartbeat()
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
    
    # # List all collections
    # # List all collections
    # collections = listCollections(client)
    # print("Collections:")
    # for collection in collections:
    #     print(f" - {collection.name}")

    # print(len(listDocuments(client, "azojt2024_main")))


if __name__ == "__main__":
    main()
