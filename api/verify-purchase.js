const crypto = require("crypto");

const STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY;
const FIREBASE_DB_URL =
  process.env.FIREBASE_DB_URL ||
  "https://ishikiri-ikoma-night-tour-default-rtdb.asia-southeast1.firebasedatabase.app";
const FIREBASE_DB_SECRET = process.env.FIREBASE_DB_SECRET;
const MAX_USES = 3;

module.exports = async function handler(req, res) {
  try {
    const sessionId = req.query.session_id;
    if (!sessionId || typeof sessionId !== "string") {
      res.status(400).json({ error: "missing session_id" });
      return;
    }

    if (!STRIPE_SECRET_KEY || !FIREBASE_DB_SECRET) {
      res.status(500).json({ error: "server not configured" });
      return;
    }

    // 1. Ask Stripe whether this checkout session was actually paid.
    const stripeRes = await fetch(
      `https://api.stripe.com/v1/checkout/sessions/${encodeURIComponent(sessionId)}`,
      { headers: { Authorization: `Bearer ${STRIPE_SECRET_KEY}` } }
    );
    if (!stripeRes.ok) {
      res.status(400).json({ error: "could not verify session" });
      return;
    }
    const session = await stripeRes.json();
    if (session.payment_status !== "paid") {
      res.status(402).json({ error: "payment not completed" });
      return;
    }

    // 2. Derive a deterministic code from the session id, so reloading this
    //    success page never issues a second code for the same purchase.
    const hash = crypto.createHash("sha256").update(sessionId).digest("hex").toUpperCase();
    const code = "NIGHT-" + hash.slice(0, 6);

    // 3. Create the access code in Firebase if it doesn't already exist.
    //    The database secret bypasses the normal read/write-only-uses rules,
    //    which is why this step has to happen server-side, not in the browser.
    const codeUrl = `${FIREBASE_DB_URL}/accessCodes/${code}.json?auth=${FIREBASE_DB_SECRET}`;
    const existingRes = await fetch(codeUrl);
    const existing = await existingRes.json();
    if (!existing) {
      await fetch(codeUrl, {
        method: "PUT",
        body: JSON.stringify({ maxUses: MAX_USES, uses: 0, sessionId }),
      });
    }

    res.status(200).json({ code, maxUses: MAX_USES });
  } catch (err) {
    res.status(500).json({ error: "server error" });
  }
};
