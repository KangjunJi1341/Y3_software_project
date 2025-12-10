Modification History

- Added vercel.json for clean URLs and pretty routes (/login, /register, /forgot, /reset, /confirm).
- Added email verification flow (confirm.html + token handling in app.js).
- Added forgot/reset password flow (forgot.html, reset.html + tokens in app.js).
- Updated register flow to require email confirmation before login and to display a demo confirmation link.
- Updated login flow to block unverified accounts and display a demo “resend” confirmation link.
- Kept chat demo: typing + voice input, local history, and daily usage limits (guest 20/day, regular 100/day).

2025-11-02 — Blob persistence + real email support
- Added serverless APIs under `front_test/api`:
  - `api/storage.js`: persists `users`, `chats`, and `messages` JSON to Vercel Blob. Overwrites files deterministically.
  - `api/email.js`: sends email via Resend (uses `RESEND_API_KEY`); falls back to simulated mode if not configured.
- Added `front_test/package.json` with dependencies (`@vercel/blob`, `resend`). No build step required.
- Updated `app.js`:
  - Added `remoteLoad`/`remoteSave` and wired setters to save to Blob; hydration on page load pulls remote data if available.
  - Registration: attempts to send real confirmation email via `/api/email` (falls back to on-screen link).
  - Login (unverified): resends confirmation email via `/api/email`.
  - Forgot password: sends reset email via `/api/email` after issuing token.

Environment (Vercel)
- Email: set `RESEND_API_KEY` (and optional `EMAIL_FROM`, default `noreply@example.com`). If not set, emails are simulated and links are shown in the UI.

Firestore Backend (replaces Blob)
- Serverless API `api/storage.js` now uses Firebase Admin to read/write Firestore.
- Required env var on Vercel Project:
  - `FIREBASE_SERVICE_ACCOUNT`: the full JSON of a Firebase service account (paste as a single line JSON string).
- Data layout in Firestore:
  - Collection `kv`, docs: `ft_users`, `ft_chats`, `ft_messages`; each doc shape: `{ value: <JSON> }`.
- Frontend remains unchanged; it calls `/api/storage` which proxies to Firestore.

Data Format
- Blob paths:
  - `data/users.json` — array of `{ email, passwordHash, isVerified, verifyToken, resetToken }`.
  - `data/chats.json` — array of chats `{ id, title, createdAt, userEmail }`.
  - `data/messages.json` — map `chatId -> DB of messages`.


Notes
- Email delivery is simulated. Confirmation and reset links are presented on-screen for demo purposes.
- All data is stored in localStorage. Clear it to reset this demo.
