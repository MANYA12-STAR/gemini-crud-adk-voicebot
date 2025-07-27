# Gemini CRUD + ADK Tools + Voice Chatbot (Full-Stack)

A full-stack demo using:

- **FastAPI** + **SQLite**
- **Google Python ADK**: `@tool` for CRUD ops, **one Agent** for routing NL → CRUD tool
- **Vertex AI Gemini** as the LLM
- **React + Tailwind** frontend with:
  - Manual form
  - Chatbot UI (uses `/chatbot`)
  - Live table with Update/Delete
  - **Speech-to-text** support via Web Speech API

---

## 1) Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\\Scripts\\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env:
#   GEMINI_PROJECT_ID=...
#   GEMINI_REGION=us-central1
#   GEMINI_MODEL=gemini-1.5-pro

uvicorn app.main:app --reload --port 8000
