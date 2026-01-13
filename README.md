# Y3 Software Project

A multi-part prototype that combines a static web UI for an AI chat assistant, Vercel serverless APIs for chat/email/storage, and a separate FastAPI vector search service. The frontend includes email/password auth screens, chat history, usage limits, and voice input (browser mic + local Whisper via transformers.js).

## What is in this repo

- Web frontend: plain HTML/CSS/JS pages for auth and chat.
- Serverless API (Vercel): `/api/chat`, `/api/email`, `/api/storage`.
- FastAPI service: FAISS-backed policy search with sentence-transformers.
- Agent demo: Node CLI using OpenAI Agents + File Search tool.

## Key features

- Auth UI: login/register/forgot/reset/confirm pages.
- Chat UI: chat list, message bubbles, daily usage limits, local persistence.
- Voice input:
  - Browser mic recording.
  - Local ASR (Whisper tiny) in the browser via `@xenova/transformers` CDN.
  - Text-to-speech for assistant replies.
- Remote persistence (optional): Firestore via `api/storage.js`.
- Transactional email (optional): Resend via `api/email.js`.
- OpenAI chat completion via `api/chat.js`.
- Policy vector search (FastAPI) over `FastAPI/data/imperial_policies.jsonl`.

## Repo layout

```
.
├── app.js                 # Frontend logic (chat, local auth demo, voice, storage)
├── styles.css             # Shared styling for auth and chat UI
├── index.html             # Alternate login page
├── login.html             # Main login page (Firebase auth)
├── register.html          # Registration page (Firebase auth)
├── forgot.html            # Forgot password page (Firebase auth)
├── reset.html             # Reset password page (local demo flow)
├── confirm.html           # Email confirmation page (local demo flow)
├── dashboard.html         # Chat dashboard
├── firebase-auth.js       # Firebase Identity Toolkit helpers (REST API)
├── api/
│   ├── chat.js            # OpenAI chat completion (Vercel serverless)
│   ├── email.js           # Resend email (Vercel serverless)
│   └── storage.js         # Firestore KV store (Vercel serverless)
├── agent_demo/
│   └── agent.js           # OpenAI Agents CLI demo
└── FastAPI/
    ├── main.py            # FastAPI app with /health and /search
    ├── requirements.txt   # Python deps
    ├── validation_service/
    │   └── faiss_service.py
    └── data/
        └── imperial_policies.jsonl
```

## Frontend behavior (important notes)

- The dashboard (`dashboard.html`) loads `app.js` and renders the chat UI. It also uses Firebase auth (`firebase-auth.js`) to gate access.
- The auth HTML pages currently use Firebase REST calls (not the local demo auth in `app.js`).
- `app.js` still contains a full local auth + email confirm + reset flow; those functions are present for demo use and can be wired back in if desired.
- Chat history is stored in `localStorage` under `ft_*` keys. If `/api/storage` is configured, it also syncs to Firestore.

## Environment variables

These are read by the Vercel serverless functions in `api/`.

- `OPENAI_API_KEY` (required for `/api/chat`)
- `OPENAI_ORG_ID` (optional)
- `OPENAI_PROJECT_ID` (optional)
- `RESEND_API_KEY` (optional; enables real email send in `/api/email`)
- `EMAIL_FROM` (optional; default `noreply@example.com`)
- `FIREBASE_SERVICE_ACCOUNT` (required for `/api/storage`)
  - Full Firebase service account JSON as a single-line string.

Frontend Firebase REST API uses the API key in `firebase-auth.js`.

## Running the frontend

Static UI can be opened directly in a browser for quick checks, but `/api/*` calls require a serverless runtime.

Option A: static only (no serverless APIs)

- Open `login.html` or `index.html` directly in a browser.
- Chat UI will still render, but `/api/chat` and `/api/storage` will fail unless you run serverless functions.

Option B: with Vercel serverless APIs

- Install Vercel CLI and run in the repo root:

```bash
npx vercel dev
```

This serves the static pages and the `/api/*` functions locally.

## Serverless API endpoints

- `POST /api/chat`
  - Body: `{ "userText": "..." }`
  - Returns: `{ "reply": "..." }`
- `POST /api/email`
  - Body: `{ "to": "...", "subject": "...", "html": "..." }`
  - Returns: `{ ok: true }` (simulated if no `RESEND_API_KEY`)
- `GET /api/storage?key=ft_users|ft_chats|ft_messages`
- `POST /api/storage`
  - Body: `{ "key": "ft_users|ft_chats|ft_messages", "value": <json> }`

## FastAPI policy search service

The FastAPI app is independent from the frontend and provides vector search over policy text.

Setup:

```bash
cd FastAPI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run:

```bash
uvicorn main:app --reload
```

Endpoints:

- `GET /health` -> `{ ok: true, model: "..." }`
- `GET /search?q=your+query&k=5`

Config via env vars (optional):

- `DATA_PATH` (default `data/imperial_policies.jsonl`)
- `TEXT_KEY` (default `text`)
- `MODEL_NAME` (default `sentence-transformers/all-MiniLM-L6-v2`)
- `K` (default `5`)

## Agent demo

`agent_demo/agent.js` runs a CLI that uses OpenAI Agents with a File Search tool.

Notes:
- The file search tool references a specific vector store id.
- You will need OpenAI credentials in your environment for this to work.

Run:

```bash
node agent_demo/agent.js
```

## Data and storage

- Local chat data keys: `ft_users`, `ft_chats`, `ft_messages` in `localStorage`.
- Firestore storage (if enabled) uses collection `kv` with docs named `ft_users`, `ft_chats`, `ft_messages`, each storing `{ value: <json> }`.

## Security and demo caveats

- Local auth in `app.js` is for demo only (not secure).
- Exposing Firebase API key in `firebase-auth.js` is standard for client-side Firebase auth but should be configured per project.
- Keep OpenAI, Resend, and Firebase service account secrets out of the repo.

## Troubleshooting

- If the chat UI does not respond, confirm `/api/chat` is reachable and `OPENAI_API_KEY` is set.
- If storage sync fails, verify `FIREBASE_SERVICE_ACCOUNT` is valid JSON and Firestore is enabled.
- If voice input does not work, check browser permissions for microphone access.
