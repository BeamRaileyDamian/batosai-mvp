import os
import sys
import tempfile
from langchain_chroma import Chroma
from langchain.schema.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from config import *

def create_embeddings(pdfs_stream, collection_name, pdf_filenames):
    # Create (or update) the data store.
    documents = load_documents(pdfs_stream, pdf_filenames)
    chunks = split_documents(documents)
    add_to_chroma(chunks, collection_name)
    return True

def get_embedding_function():
    return HuggingFaceEmbeddings(model_name=MODEL_NAME, model_kwargs={"device": "cpu"})

def load_documents(pdf_streams: list[bytes], pdf_filenames: list[str]):
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_files = {}

        # Save each PDF stream to a file in the temp directory
        for i, pdf_bytes in enumerate(pdf_streams):
            temp_path = os.path.join(temp_dir, f"temp_pdf_{i}.pdf")
            with open(temp_path, "wb") as f:
                f.write(pdf_bytes)
            temp_files[temp_path] = pdf_filenames[i]  # Store mapping to original filename

        # Load all PDFs from the temp directory
        loader = PyPDFDirectoryLoader(temp_dir)
        documents = loader.load()

        # Assign original filenames to metadata
        for doc in documents:
            temp_path = doc.metadata.get("source")
            if temp_path in temp_files:
                doc.metadata["original_filename"] = temp_files[temp_path]

    return documents

def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def add_to_chroma(chunks: list[Document], collection_name: str):
    # Load the existing database.
    db = Chroma(
        persist_directory=f'{CHROMA_PATH}/{collection_name}', embedding_function=get_embedding_function()
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    # print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        # print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
    # else:
        # print("✅ No new documents to add")

def calculate_chunk_ids(chunks):
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        original_filename = chunk.metadata.get("original_filename", "unknown.pdf")
        page = chunk.metadata.get("page")
        current_page_id = f"{original_filename}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        chunk.metadata["id"] = chunk_id

    return chunks