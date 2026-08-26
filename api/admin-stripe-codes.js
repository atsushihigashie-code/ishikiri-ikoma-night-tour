// /api/admin-stripe-codes.js
//
// Admin-only, READ-ONLY endpoint: lists individually-issued Stripe
// purchase codes (i.e. every accessCodes entry WITHOUT a "-shared"
// source — the opposite filter of admin-shared-codes.js), along with
// how many times each has been used (uses / maxUses).
//
// This file only reads from Firebase — it never writes, updates, or
// deletes anything, and it does not touch verify-purchase.js, gate.html,
// or admin-issue-code.js.
//
// POST /api/admin-stripe-codes   body: { adminKey, limit? }
//   - limit: optional, how many most-recent codes to return (default 50)

const FIREBASE_DB_URL =
  process.env.FIREBASE_DB_URL ||
  "https://ishikiri-ikoma-night-tour-default-rtdb.asia-southeast1.firebasedatabase.app";
const FIREBASE_DB_SECRET = process.env.FIREBASE_DB_SECRET;
const ADMIN_SECRET = process.env.ADMIN_SECRET;

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  const { adminKey, limit } = req.body || {};
  if (!adminKey || adminKey !== ADMIN_SECRET) {
    return res.status(401).json({ error: "Invalid admin key" });
  }
  if (!FIREBASE_DB_SECRET) {
    return res.status(500).json({ error: "server not configured" });
  }

  try {
    const url = `${FIREBASE_DB_URL}/accessCodes.json?auth=${FIREBASE_DB_SECRET}`;
    const r = await fetch(url);
    const allCodes = (await r.json()) || {};

    const codes = [];
    let totalUses = 0;
    for (const [code, data] of Object.entries(allCodes)) {
      const source = data && typeof data.source === "string" ? data.source : "";
      if (source.endsWith("-shared")) continue; // exclude OTA shared-pool codes; those are in admin-shared-codes.js

      const uses = typeof data.uses === "number" ? data.uses : 0;
      totalUses += uses;

      codes.push({
        code,
        sessionId: data.sessionId || null,
        uses,
        maxUses: typeof data.maxUses === "number" ? data.maxUses : 0,
      });
    }

    codes.sort((a, b) => b.uses - a.uses);
    const maxItems = typeof limit === "number" && limit > 0 ? limit : 50;

    return res.status(200).json({
      codes: codes.slice(0, maxItems),
      codeCount: codes.length,
      totalUses,
    });
  } catch (err) {
    return res.status(500).json({ error: "unexpected error", detail: String(err) });
  }
};
