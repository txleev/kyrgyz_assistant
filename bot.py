import io
import requests
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message
from tts_mini.tts_interface import run_tts  # import your actual entry point
from stt import *
from pydub import AudioSegment
from sentence_transformers import SentenceTransformer
import faiss

# === CONFIG ===
BOT_TOKEN = "<token>"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# === SQLite Setup ===
def init_db():
    with sqlite3.connect("conversations.db") as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

def save_to_db(text):
    with sqlite3.connect("conversations.db") as conn:
        conn.execute("INSERT INTO chat_history (user_input) VALUES (?)", (text,))

def get_chat_history():
    with sqlite3.connect("conversations.db") as conn:
        rows = conn.execute("SELECT user_input FROM chat_history ORDER BY timestamp DESC").fetchall()
    return [r[0] for r in rows]

# === FAISS Retrieval ===
def chunk_text(text, max_tokens=500):
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

def build_faiss_index():
    history = get_chat_history()
    if not history:
        return None, []
    chunks = chunk_text(" ".join(history))
    embeddings = embedding_model.encode(chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index, chunks

def retrieve_top_k(query, index, texts, k=3):
    query_vec = embedding_model.encode([query])
    _, I = index.search(query_vec, k)
    return [texts[i] for i in I[0]]

# === LLM Call ===
async def chat_with_rag(prompt):
    index, chunks = build_faiss_index()
    context = ""
    if index:
        top_chunks = retrieve_top_k(prompt, index, chunks)
        context = "\n".join(top_chunks)

    payload = {
        "prompt": f"Use context below to answer in Kyrgyz without transcription. avoid using any formatting symbols such as **, --, __, etc:\n{context}\n\nQuestion: {prompt}",
        "model": 'gemma3:12b',
        'stream': False,
        "max_tokens": 1000,
        "temperature": 0.7
    }
    try:
        response = requests.post('localhost:11434/api/generate', json=payload)
        return response.json().get('response', '')
    except Exception as e:
        return f"Error contacting Ollama: {e}"

@dp.message(Command(commands=["start", "help"]))
async def cmd_start(msg: types.Message):
    await msg.reply("Send me a voice or text message, I'll reply with voice using RAG!")

@dp.message(F.voice)
async def handle_voice(msg: Message):
    file = await bot.get_file(msg.voice.file_id)
    buf = await bot.download_file(file.file_path)
    buf.seek(0)

    text = transcribe(buf.getvalue())
    print(f"raw input: {text}")
    save_to_db(text)
    llm_answer = await chat_with_rag(text)
    print(f"llm answer: {llm_answer}")

    run_tts(llm_answer)
    audio = AudioSegment.from_wav("tts_mini/utterance_001.wav")
    audio.export("reply.ogg", format="ogg", codec="libopus")
    voice = FSInputFile("reply.ogg")
    await bot.send_chat_action(msg.chat.id, action="record_voice")
    await bot.send_voice(msg.chat.id, voice)

@dp.message(F.text)
async def handle_text(msg: Message):
    save_to_db(msg.text)

    llm_answer = await chat_with_rag(msg.text)
    print(f"llm answer: {llm_answer}")

    run_tts(llm_answer)
    audio = AudioSegment.from_wav("tts_mini/utterance_001.wav")
    audio.export("reply.ogg", format="ogg", codec="libopus")
    voice = FSInputFile("reply.ogg")
    await bot.send_chat_action(msg.chat.id, action="record_voice")
    await bot.send_voice(msg.chat.id, voice)

async def log_ready():
    print("✅ Bot is up and running. Waiting for messages…")

if __name__ == "__main__":
    print("🚀 Starting bot…")
    init_db()
    dp.run_polling(bot, on_startup=[log_ready])
