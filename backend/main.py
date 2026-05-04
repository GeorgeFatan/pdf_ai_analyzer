from fastapi import FastAPI, UploadFile, File, Query
from pypdf import PdfReader
from database import add_pdf_to_db, query_text
from chat import chat_with_pdf
from fastapi import Body
import os

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def root():
    return {"message": "Backend running..."}

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # save PDF-ul
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extragem textul
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    # Save textul în ChromaDB
    add_pdf_to_db(file.filename, text)

    return {
        "filename": file.filename,
        "text_preview": text[:600]
    }

@app.get("/search/")
def search(query: str = Query(...)):
    results = query_text(query)
    return results

@app.post("/chat/")
def chat(question: str = Body(..., embed=True)):
    answer = chat_with_pdf(question)
    return {"answer": answer}