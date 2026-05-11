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
def query_text(query: str, pdf_name: str | None = None):
    if pdf_name:
        results = collection.query(
            query_texts=[query],
            where={"filename": pdf_name},
            n_results=5
        )
    else:
        results = collection.query(
            query_texts=[query],
            n_results=5
        )

    return results


# DELETE PDF FROM DATABASE
def delete_pdf_from_db(pdf_name: str):
    # gasim toate id-urile asociate cu documentul respectiv
    results = collection.get(where={"filename": pdf_name})

    if "ids" in results and results["ids"]:
        collection.delete(ids=results["ids"])
