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
    context = "\n".join(documents)

    # construim promptul modelului
    prompt = f"""
    You are an assistant that helps answer questions based on the following context from the PDF document:

    PDF Context:
    {context}

    Question: {question}

    If the answer is not in the context of the PDF, say: "The PDF does not contain the answer to this question."
    """

    # trimitem promptul la Groq
    response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": prompt}]
    )


    return response.choices[0].message.content.strip()
