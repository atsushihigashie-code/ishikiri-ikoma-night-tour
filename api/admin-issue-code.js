// /api/admin-issue-code.js
//
// Admin-only endpoint: issues (or re-fetches) a shared access code, meant
// for embedding statically in an OTA ticket/voucher (GetYourGuide, Viator,
// etc). Unlike Stripe-purchased codes (maxUses: 3 in verify-purchase.js),
// shared OTA codes get a much higher maxUses so many customers can each
// redeem the same printed code.
//
// POST /api/admin-issue-code   body: { adminKey, source, maxUses? }
//   - source: short label, e.g. "getyourguide-shared" or "viator-shared".
//     Used as part of the generated code and stored for auditing.
//   - maxUses: optional, defaults to 200.
//
// Calling this twice with the same "source" returns the SAME existing code
// rather than minting a second one, so it's safe to re-run if you forget
// the code later.

const FIREBASE_DB_URL =
  process.env.FIREBASE_DB_URL ||
  "https://ishikiri-ikoma-night-tour-default-rtdb.asia-southeast1.firebasedatabase.app";
const FIREBASE_DB_SECRET = process.env.FIREBASE_DB_SECRET;
const ADMIN_SECRET = process.env.ADMIN_SECRET;
const DEFAULT_MAX_USES = 200;

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  const { adminKey, source, maxUses } = req.body || {};
  if (!adminKey || adminKey !== ADMIN_SECRET) {
    return res.status(401).json({ error: "Invalid admin key" });
  }
  if (!source || typeof source !== "string") {
    return res.status(400).json({ error: "source is required, e.g. 'getyourguide-shared'" });
  }
  if (!FIREBASE_DB_SECRET) {
    return res.status(500).json({ error: "server not configured" });
  }

  try {
    // Look for an existing shared code with this exact source first, so
    // re-running this endpoint is idempotent.
    const listUrl = `${FIREBASE_DB_URL}/accessCodes.json?auth=${FIREBASE_DB_SECRET}`;
    const listRes = await fetch(listUrl);
    const allCodes = (await listRes.json()) || {};

    const existingEntry = Object.entries(allCodes).find(
      ([, data]) => data && data.source === source
    );
    if (existingEntry) {
      const [existingCode, data] = existingEntry;
      return res.status(200).json({
        code: existingCode,
        maxUses: data.maxUses,
        uses: data.uses,
        source,
        reused: true,
      });
    }

    // Mint a new one: SHARED-<SOURCE-SLUG>-<4 random base36 chars>.
    const slug = source.replace(/[^a-zA-Z0-9]+/g, "").toUpperCase().slice(0, 12);
    const rand = Math.random().toString(36).slice(2, 6).toUpperCase();
    const code = `NIGHT-${slug}-${rand}`;

    const codeUrl = `${FIREBASE_DB_URL}/accessCodes/${code}.json?auth=${FIREBASE_DB_SECRET}`;
    const finalMaxUses = typeof maxUses === "number" && maxUses > 0 ? maxUses : DEFAULT_MAX_USES;
    await fetch(codeUrl, {
      method: "PUT",
      body: JSON.stringify({ maxUses: finalMaxUses, uses: 0, source }),
    });

    return res.status(200).json({ code, maxUses: finalMaxUses, uses: 0, source, reused: false });
  } catch (err) {
    return res.status(500).json({ error: "unexpected error", detail: String(err) });
  }
};
