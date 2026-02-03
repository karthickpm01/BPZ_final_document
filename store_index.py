from dotenv import load_dotenv
import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from src.helper import text_split, download_hugging_face_embeddings

load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

def index_specific_file(file_path):
    """
    Reads a specific PDF file, chunks it, and pushes it to Pinecone.
    """
    print(f"--- STARTING INDEXING FOR: {file_path} ---")

    try:
        loader = PyPDFLoader(file_path)
        extracted_data = loader.load()
    except Exception as e:
        print(f"Failed to load PDF {file_path}: {e}")
        return False

    if not extracted_data:
        print("PDF loaded but no text found.")
        return False

    text_chunks = text_split(extracted_data)

    if not text_chunks:
        print("Text splitting failed.")
        return False

    print(f"--- Document Split into {len(text_chunks)} chunks. Sending to Pinecone... ---")

    embeddings = download_hugging_face_embeddings()
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # MUST MATCH THE NAME IN APP.PY
    index_name = "bpz-chatbot"

    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    PineconeVectorStore.from_documents(
        documents=text_chunks,
        index_name=index_name,
        embedding=embeddings,
    )

    print(f"--- SUCCESSFULLY INDEXED {file_path} ---")
    return True