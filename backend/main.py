from fastapi import FastAPI, UploadFile, File, Query
from pypdf import PdfReader
from database import add_pdf_to_db, query_text
from chat import chat_with_pdf
from fastapi import Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()


# CORS — permite frontend-ului (5173) sa comunice (8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

class ChatRequest(BaseModel):
    question: str
    history: list | None = None
    pdf_name: str | None = None

@app.post("/chat/")
def chat(chat_request: ChatRequest):
    answer = chat_with_pdf(chat_request.question, chat_request.history, chat_request.pdf_name)
    return {"answer": answer}


# new endpoint to add list of pdfs
@app.get("/list-pdfs/")
def list_pdfs():
    files = os.listdir("uploads") # fisierele din uploads
    pdfs = [f for f in files if f.lower().endswith(".pdf")] # only pdfs extensions
    return {"pdfs": pdfs}

class DeleteRequest(BaseModel):
    pdfs: list[str]

@app.post("/delete-pdfs/")
def delete_pdfs(req: DeleteRequest):
    deleted = []

    for pdf in req.pdfs:
        file_path = os.path.join("uploads", pdf)
        
        # stergem fisierul fizic din uploads
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # stergem din baza de date ChromaDB
        from database import delete_pdf_from_db
        delete_pdf_from_db(pdf)

        deleted.append(pdf)
        
    return {"deleted": deleted}
