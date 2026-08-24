const crypto = require("crypto");

const STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY;
const FIREBASE_DB_URL =
  process.env.FIREBASE_DB_URL ||
  "https://ishikiri-ikoma-night-tour-default-rtdb.asia-southeast1.firebasedatabase.app";
const FIREBASE_DB_SECRET = process.env.FIREBASE_DB_SECRET;
const MAX_USES = 3;

// "Today" in Japan time, as YYYY-MM-DD — used so hotel dashboards match
// what the front-desk staff mean by "today", not UTC's today.
function getJstDateString() {
  const jstOffset = 9 * 60 * 60 * 1000;
  return new Date(Date.now() + jstOffset).toISOString().slice(0, 10);
}

// Records one referred booking under referrals/{hotelId}/{date}/{sessionId}.
// Called at most once per session (guarded by the caller, same as the
// access-code creation it sits next to).
async function logReferralIfAny(session, sessionId) {
  const hotelId = session.client_reference_id;
  if (!hotelId) return;
  const date = getJstDateString();
  const refUrl = `${FIREBASE_DB_URL}/referrals/${hotelId}/${date}/${sessionId}.json?auth=${FIREBASE_DB_SECRET}`;
  await fetch(refUrl, {
    method: "PUT",
    body: JSON.stringify({ timestamp: Date.now(), commission: 200 }),
  });
}

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
      // Only reached the first time this session is verified, so the
      // referral is logged exactly once per purchase.
      await logReferralIfAny(session, sessionId);
    }

    res.status(200).json({ code, maxUses: MAX_USES });
  } catch (err) {
    res.status(500).json({ error: "server error" });
  }
};
