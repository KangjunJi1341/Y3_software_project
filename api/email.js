// Send transactional emails via Resend if API key is configured.
import { Resend } from "resend";

const resendApiKey = process.env.RESEND_API_KEY;
const fromAddress = process.env.EMAIL_FROM || "noreply@example.com";

export default async function handler(req, res) {
  try {
    if (req.method !== "POST") return res.status(405).json({ error: "method_not_allowed" });
    const { to, subject, html } = req.body || {};
    if (!to || !subject || !html) return res.status(400).json({ error: "invalid_request" });

    if (!resendApiKey) {
      // Simulate success without external service
      console.log("[email:simulate] to=%s subject=%s", to, subject);
      return res.status(200).json({ ok: true, simulated: true });
    }

    const resend = new Resend(resendApiKey);
    const result = await resend.emails.send({ from: fromAddress, to, subject, html });
    if (result.error) return res.status(500).json({ error: "send_failed", detail: result.error });
    return res.status(200).json({ ok: true, id: result.data?.id });
  } catch (err) {
    console.error("/api/email error", err);
    return res.status(500).json({ error: "server_error" });
  }
}

