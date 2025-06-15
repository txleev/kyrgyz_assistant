# 🎙️ Jarchy AI — Kyrgyz Speech-to-Speech Assistant

Jarchy AI is the **first open-source Kyrgyz-language speech-to-speech assistant**, built using `Aiogram`, local LLMs, STT, and TTS technologies. Designed as a prototype for the hackathon, it allows users to send **voice messages in Kyrgyz** and receive back **spoken AI responses** — directly through **Telegram**.

---

## 🚀 Demo

https://youtu.be/your-demo-link (replace this with your video link)

---

## 🧠 What Jarchy AI Does

- 🎤 **Speech Recognition (STT)**: Converts user voice messages to text (e.g., Whisper or custom model)
- 🤖 **AI Processing**: Local LLM (Ollama + Gemma3) refines and answers in Kyrgyz
- 🔊 **Text-to-Speech (TTS)**: Generates a natural Kyrgyz voice reply
- 💬 **Telegram Bot Interface**: Built with `aiogram` for seamless interaction

---

## 🧩 Tech Stack

| Component        | Tool / Framework            |
|------------------|-----------------------------|
| **STT**          | Whisper / Custom STT Module |
| **LLM**          | [Ollama](https://ollama.ai/) + Gemma 3B (local) |
| **TTS**          | `tts_mini` (internal voice engine) |
| **Bot Framework**| Aiogram (Telegram Bot)      |
| **Language**     | Python                      |
| **Platform**     | Telegram (Chatbot)          |

---

## 🛠 How to Run Locally

> ⚠️ This is a prototype. Full RAG functionality is planned but not implemented in this version.

1. **Clone the repo**
```bash
git clone https://github.com/your-username/jarchy-ai.git
cd jarchy-ai
```

Install dependencies

bash
Копировать
Редактировать
pip install -r requirements.txt
Set up Ollama

Download and run the Ollama server locally

Ensure Gemma3 is installed:

bash
Копировать
Редактировать
ollama run gemma3:12b
Set Telegram bot token

bash
Копировать
Редактировать
export BOT_TOKEN=your-telegram-token
Run the bot

bash
Копировать
Редактировать
python main.py
🎯 Vision
Jarchy AI is more than a voice bot — it’s a Kyrgyz AI assistant prototype designed to:

Make AI more accessible to Kyrgyz speakers

Work offline using local models

Support contextual memory and RAG in the future

Expand to mobile and web platforms

🧪 Planned Features
 RAG with FAISS + SQLite (conversation memory)

 Live whisper STT streaming

 Multi-user memory support

 Web UI version

 Advanced emotion-aware TTS

👥 Team
Name	Role
[Your Name]	Developer / AI Lead
[Teammate]	Bot Dev / Voice
[Teammate]	Design & Demo

📜 License
MIT — feel free to use, remix, and build on top of Jarchy AI.

❤️ Acknowledgments
Kyrgyz language community

Whisper by OpenAI

Ollama for local LLMs

Aiogram community
