// api/chat.js  —— Vercel/Node 后端，真正调用 OpenAI

import OpenAI from "openai";

const client = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
    organization: process.env.OPENAI_ORG_ID,
    project: process.env.OPENAI_PROJECT_ID,
});

// Vercel / Next.js API handler
export default async function handler(req, res) {
    if (req.method !== "POST") {
        res.status(405).json({ error: "Method not allowed" });
        return;
    }

    try {
        const { userText } = req.body;

        if (!userText || typeof userText !== "string") {
            res.status(400).json({ error: "userText is required" });
            return;
        }

        const completion = await client.chat.completions.create({
            model: "gpt-4.1",          // 你想用哪个模型改这里
            messages: [
                { role: "system", content: "You are a helpful assistant." },
                { role: "user", content: userText },
            ],
        });

        const reply =
            completion.choices?.[0]?.message?.content || "(empty reply)";

        res.status(200).json({ reply });
    } catch (err) {
        console.error("OpenAI error:", err);
        res
            .status(500)
            .json({ error: "OpenAI error", detail: err.message || String(err) });
    }
}
