# 🧠 Gemini CRUD + Voice Chatbot Demo (Full-Stack AI App)

A full-stack CRUD application powered by **Google's ADK**, **Vertex AI Gemini**, and **FastAPI**, with a slick **React + Tailwind** frontend and voice-enabled chatbot.

---

## 🚀 Features

### 🤖 Backend
- FastAPI + SQLite-based CRUD API
- Gemini LLM + ADK tools (`@tool`) for:
  - `create`, `read`, `update`, `delete` customer operations
- LLM-driven agent routes natural language to the right CRUD tool
- `.env`-based Gemini API setup
- Secure tool use with Pydantic schema validation

### 🌐 Frontend
- Built with React + TailwindCSS
- Functional UI with:
  - Manual Customer form (Create/Update)
  - Live customer table with Edit/Delete buttons
  - Gemini-powered chatbot (connected to `/chatbot`)
  - Voice input via Web Speech API 🗣️

---

## 🛠️ Setup Guide

### 📦 Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env  # Create a .env file from the template
