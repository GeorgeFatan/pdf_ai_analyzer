import os
from groq import Groq
from dotenv import load_dotenv
from database import query_text

# Load variabilele din .env (adica cheia API)
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def chat_with_pdf(question: str):
    # cautam context in baza de date
    results = query_text(question)

    # extragem fragmentele relevante
    documents = results["documents"][0] if results["documents"] else []
    distances = results["distances"][0] if "distances" in results else []

    # filtrare context: pastram doar fragmente cu distanta < 1.0
    filtered = [
        doc for doc, dist in zip(documents, distances)
        if dist < 1.0
    ]

    # fallback: daca filtrarea elimina tot, folosim totusi primele fragmente
    if not filtered:
        filtered = documents

    context = "\n".join(filtered)

    # prompt imbunatatit
    prompt = f"""
    You are an assistant that answers questions ONLY using the context extracted from a PDF.

    CONTEXT FROM PDF:
    {context}

    QUESTION:
    {question}

    RULES:
    - If the answer is not in the context, say exactly:
      "The PDF does not contain the answer to this question."
    - Do NOT invent information.
    - Base your answer strictly on the provided context.
    """

    # trimitem promptul la Groq
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
