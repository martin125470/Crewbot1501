# Equipment Manual Copilot

A multi-user chatbot that lets you upload PDF equipment manuals, assign each a **unit number**, and ask questions via a chat interface. The assistant uses Retrieval-Augmented Generation (RAG) to answer questions from the correct manual and can **cross-reference** multiple manuals when parts or keywords span units.

## Features

| Feature | Details |
|---|---|
| 📄 PDF Upload | Upload any number of PDF manuals; each gets a unique unit number |
| 🔍 Unit-targeted Q&A | Mention "unit 102" in chat — the bot searches that manual first |
| 🔗 Cross-manual reference | Keywords like *hoses, filters, parts* trigger a search across all manuals |
| 👥 Multi-user | Admin + unlimited user accounts with JWT authentication |
| 🗑️ Add / Delete | Admins can add or remove manuals and manage user accounts |
| 💻 Web UI | Built-in single-page app — no separate frontend install needed |

## Quick Start

### 1. Prerequisites

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY and SECRET_KEY
```

**.env settings:**

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key (required) |
| `SECRET_KEY` | A long random string used to sign JWT tokens |
| `CHAT_MODEL` | OpenAI model (default: `gpt-4o-mini`) |
| `EMBEDDING_MODEL` | Embedding model (default: `text-embedding-3-small`) |
| `PDF_STORAGE_DIR` | Where uploaded PDFs are stored (default: `./data/pdfs`) |
| `CHROMA_DB_DIR` | ChromaDB vector store location (default: `./data/chroma`) |

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

Open **http://localhost:8000** in your browser.

### 5. First login

| Username | Password | Role |
|---|---|---|
| `admin` | `admin` | Admin |

> **Change the default password** immediately after first login by deleting and re-creating the admin user, or edit `data/users.json` directly.

---

## Usage Guide

### Uploading a Manual

1. Go to the **Manuals** page.
2. Click **Upload Manual**.
3. Enter a unit number (e.g. `102`) and optionally a description.
4. Drag & drop or select a PDF file.
5. Click **Upload & Index** — the PDF is extracted and embedded automatically.

### Chatting

- Open the **Chat** page.
- Ask any question. Examples:
  - *"What are the hydraulic specs for unit 102?"*
  - *"What hoses do I need for unit 102?"* — triggers cross-manual part lookup
  - *"Compare oil specs across all units"*
- The assistant cites the unit number and page for every answer.

### Managing Users (Admin only)

1. Go to the **Users** page.
2. Click **Add User**, enter a username, password, and role.
3. To remove a user, click **Remove** next to their name.

---

## Architecture

```
app/
├── main.py                  # FastAPI app + static file serving
├── auth.py                  # JWT auth, user store (data/users.json)
├── models/
│   └── schemas.py           # Pydantic models
├── routers/
│   ├── auth_router.py       # POST /api/auth/token, user CRUD
│   ├── manuals_router.py    # GET/POST/DELETE /api/manuals
│   └── chat_router.py       # POST /api/chat
└── services/
    ├── pdf_service.py        # PDF text extraction + chunking
    ├── vector_service.py     # ChromaDB indexing & querying
    └── chat_service.py       # RAG pipeline + OpenAI chat
static/
└── index.html               # Single-page web UI
data/
├── pdfs/                    # Uploaded PDFs stored here
└── chroma/                  # Vector index (auto-created)
```

### RAG Pipeline

1. **Ingest**: PDF → `pdfplumber` extracts text page-by-page → split into 800-char overlapping chunks → embedded with OpenAI `text-embedding-3-small` → stored in ChromaDB (one collection per unit).
2. **Retrieve**: User message → detect unit numbers → query that unit's collection + cross-reference all collections if parts keywords are detected.
3. **Generate**: Top chunks injected into system prompt → OpenAI GPT generates answer with citations.

## API Reference

All endpoints require `Authorization: Bearer <token>` except `POST /api/auth/token`.

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/token` | None | Login, get JWT |
| `GET` | `/api/auth/me` | User | Current user info |
| `GET` | `/api/auth/users` | Admin | List users |
| `POST` | `/api/auth/users` | Admin | Create user |
| `DELETE` | `/api/auth/users/{username}` | Admin | Delete user |
| `GET` | `/api/manuals` | User | List manuals |
| `POST` | `/api/manuals` | User | Upload PDF manual |
| `GET` | `/api/manuals/{unit}` | User | Get manual metadata |
| `GET` | `/api/manuals/{unit}/download` | User | Download PDF |
| `DELETE` | `/api/manuals/{unit}` | Admin | Delete manual |
| `POST` | `/api/chat` | User | Send chat message |
