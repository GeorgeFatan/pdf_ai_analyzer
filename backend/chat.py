import os
from groq import Groq
from dotenv import load_dotenv
from database import query_text

# Load variabilele din .env (adica cheia API)
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def chat_with_pdf(question: str, history: list = None, pdf_name: str | None = None):
    if history is None:
        history = []

    # cautam context in baza de date
    results = query_text(question, pdf_name)

    documents = results["documents"][0] if results["documents"] else []
    distances = results["distances"][0] if "distances" in results else []

    filtered = [
        doc for doc, dist in zip(documents, distances)
        if dist < 1.0
    ]

    if not filtered:
        filtered = documents

    context = "\n".join(filtered)

    # construim istoricul pentru prompt
    history_text = ""
    for msg in history:
        history_text += f"{msg['role'].upper()}: {msg['content']}\n"

    # prompt imbunatatit cu istoric
    prompt = f"""
    You are an AI assistant that answers questions using ONLY the information found in the provided PDF context.

Your goals:
- Give clear, natural, human‑like explanations.
- Sound conversational, not robotic.
- Base every part of your answer strictly on the context.
- If the context does not contain the answer, say exactly:
  "The PDF does not contain the answer to this question."

ACTIVE PDF: {pdf_name}

CONVERSATION HISTORY:
{history_text}

PDF CONTEXT:
{context}

QUESTION:
{question}

Guidelines:
- Do NOT invent or guess information.
- Do NOT add details that are not explicitly present in the context.
- If the context is unclear or incomplete, acknowledge that.
- Keep the tone friendly, natural, and easy to read.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

