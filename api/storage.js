// Persist simple JSON key/value data to Vercel Blob
// Keys are constrained to a fixed set for safety.
import { put, list } from "@vercel/blob";

const KEY_FILE_MAP = {
  ft_users: "data/users.json",
  ft_chats: "data/chats.json",
  ft_messages: "data/messages.json"
  // Note: current user is intentionally client-only
};

async function readBlobJSON(pathname) {
  const { blobs } = await list({ prefix: pathname });
  const entry = blobs.find((b) => b.pathname === pathname);
  if (!entry) return null;
  const res = await fetch(entry.url);
  if (!res.ok) return null;
  return await res.json();
}

async function writeBlobJSON(pathname, value) {
  const body = JSON.stringify(value ?? null, null, 2);
  await put(pathname, body, {
    access: "public",
    addRandomSuffix: false,
    contentType: "application/json"
  });
}

export default async function handler(req, res) {
  try {
    if (req.method === "GET") {
      const { key } = req.query;
      const pathname = KEY_FILE_MAP[key];
      if (!pathname) return res.status(400).json({ error: "invalid_key" });
      const data = await readBlobJSON(pathname);
      return res.status(200).json({ key, value: data ?? null });
    }

    if (req.method === "POST") {
      const { key, value } = req.body || {};
      const pathname = KEY_FILE_MAP[key];
      if (!pathname) return res.status(400).json({ error: "invalid_key" });
      await writeBlobJSON(pathname, value);
      return res.status(200).json({ ok: true });
    }

    return res.status(405).json({ error: "method_not_allowed" });
  } catch (err) {
    console.error("/api/storage error", err);
    return res.status(500).json({ error: "server_error" });
  }
}

