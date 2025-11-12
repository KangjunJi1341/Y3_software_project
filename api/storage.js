// Persist simple JSON key/value data to Firebase Firestore (Admin SDK)
// Keys are constrained to a fixed set for safety.
import admin from "firebase-admin";

const VALID_KEYS = new Set(["ft_users", "ft_chats", "ft_messages"]);

function ensureAdmin() {
  if (admin.apps.length) return admin.firestore();
  const svc = process.env.FIREBASE_SERVICE_ACCOUNT;
  if (!svc) {
    throw new Error("FIREBASE_SERVICE_ACCOUNT is not set");
  }
  let creds;
  try {
    creds = JSON.parse(svc);
  } catch {
    throw new Error("FIREBASE_SERVICE_ACCOUNT is not valid JSON");
  }
  admin.initializeApp({ credential: admin.credential.cert(creds) });
  return admin.firestore();
}

async function readKV(db, key) {
  const snap = await db.collection("kv").doc(key).get();
  if (!snap.exists) return null;
  const data = snap.data() || {};
  return Object.prototype.hasOwnProperty.call(data, "value") ? data.value : null;
}

async function writeKV(db, key, value) {
  await db.collection("kv").doc(key).set({ value }, { merge: false });
}

export default async function handler(req, res) {
  try {
    const db = ensureAdmin();

    if (req.method === "GET") {
      const { key } = req.query;
      if (!VALID_KEYS.has(key)) return res.status(400).json({ error: "invalid_key" });
      const value = await readKV(db, key);
      return res.status(200).json({ key, value: value ?? null });
    }

    if (req.method === "POST") {
      const { key, value } = req.body || {};
      if (!VALID_KEYS.has(key)) return res.status(400).json({ error: "invalid_key" });
      await writeKV(db, key, value);
      return res.status(200).json({ ok: true });
    }

    return res.status(405).json({ error: "method_not_allowed" });
  } catch (err) {
    console.error("/api/storage error", err);
    return res.status(500).json({ error: "server_error" });
  }
}

