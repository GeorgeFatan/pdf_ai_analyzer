import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2") 
#modelul de embedding pe care il folosim pentru a transforma textul in vectori numerici, astfel incat sa putem face cautari semantice in baza de date.


client = chromadb.Client()
collection = client.get_or_create_collection("pdf_texts")



# CHUNKING FUNCTION
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap  # suprapunere pentru context mai bun

    return chunks

# ADD PDF TO DATABASE (CHUNKED)
def add_pdf_to_db(filename: str, text: str):
    chunks = chunk_text(text)

    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk)

        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            metadatas=[{"filename": filename, "chunk_index": i}],
            ids=[f"{filename}_{i}"]
        )


# QUERY FUNCTION
def query_text(query: str):
    embedding = model.encode(query)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=5
    )

    return results
