import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client()
collection = client.get_or_create_collection("pdf_texts")

def add_pdf_to_db(filename: str, text: str):
    embedding = model.encode(text)
    collection.add(
        documents=[text],
        embeddings=[embedding],
        metadatas=[{"filename": filename}],
        ids=[filename]
    )

def query_text(query: str):
    embedding = model.encode(query)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=3
    )
    return results
