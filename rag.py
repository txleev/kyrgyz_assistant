import requests
import json
from typing import List, Dict
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import PyPDF2
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Tuple
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
import sqlite3
import numpy as np
import sqlite3

async def init_db():
    conn = sqlite3.connect("conversations.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

async def save_user_input(user_input: str):
    conn = sqlite3.connect("conversations.db")
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (user_input) VALUES (?)", (user_input,))
    conn.commit()
    conn.close()


embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def chunk_text(text: str, max_tokens: int = 500) -> List[str]:
    sentences = text.split('.')
    chunks, chunk = [], ""
    for sentence in sentences:
        if len((chunk + sentence).split()) < max_tokens:
            chunk += sentence + '.'
        else:
            chunks.append(chunk.strip())
            chunk = sentence + '.'
    if chunk:
        chunks.append(chunk.strip())
    return chunks

def build_faiss_index(text_chunks: List[str]) -> Tuple[faiss.IndexFlatL2, List[str]]:
    embeddings = embedding_model.encode(text_chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index, text_chunks

def retrieve_top_k(query: str, index, texts: List[str], k: int = 3) -> List[str]:
    query_vec = embedding_model.encode([query])
    _, I = index.search(query_vec, k)
    return [texts[i] for i in I[0]]

def generate_answer(question: str, context: str, use_ollama: bool = False) -> str:
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": "You are a helpful assistant for Sonun university. add citation. Answer in Kyrgyz Language."},
        {"role": "user", "content": f"Answer the question based on the following context:\n\n{context}\n\nQuestion: {question}"}
    ]

    if use_ollama:
        response = requests.post(
            # url= insert URL,
            json={
                "model": "gemma3",  # Change model name as needed
                "messages": messages,
                "stream": True,
                "temperature": 0.8,
                "top_p": 0.1,
                "max_tokens": 2048
            },
            stream=True
        )

        # Accumulate content from streamed chunks
        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    content = data.get("message", {}).get("content", "")
                    full_response += content
                except json.JSONDecodeError:
                    continue  # Skip malformed lines

        return full_response.strip()


    else:
        endpoint = "https://models.github.ai/inference"
        model = "deepseek/DeepSeek-V3-0324"
        token = os.environ["V3_TOKEN"]

        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(token),
        )

        response = client.complete(
            messages=messages,
            temperature=0.8,
            top_p=0.1,
            max_tokens=2048,
            model=model
        )
        return response.choices[0].message['content'].strip()



# Preload FAISS index
def load_index_from_pdfs(pdf_files: List[str]):
    all_chunks = []
    for pdf in pdf_files:
        text = extract_text_from_pdf(pdf)
        chunks = chunk_text(text)
        all_chunks.extend(chunks)
    return build_faiss_index(all_chunks)