// /api/admin-shared-codes.js
//
// Admin-only endpoint: lists every OTA shared access code (source ending
// in "-shared", e.g. "getyourguide-shared", "viator-shared") along with
// its usage. This covers whichever OTA platforms have had a code issued
// via admin-issue-code.js — no per-platform hardcoding needed.
//
// POST /api/admin-shared-codes   body: { adminKey }
//
// Note: this only reports maxUses / uses (a simple counter), matching how
// gate.html and admin-issue-code.js actually track redemptions in this
// project. It does not track distinct devices — that would require a
// device-fingerprint log this project doesn't currently record.

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

  const { adminKey } = req.body || {};
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
    for (const [code, data] of Object.entries(allCodes)) {
      const source = data && typeof data.source === "string" ? data.source : "";
      if (!source.endsWith("-shared")) continue; // only OTA shared-pool codes, not individual purchase codes

      codes.push({
        code,
        source,
        maxUses: typeof data.maxUses === "number" ? data.maxUses : 0,
        uses: typeof data.uses === "number" ? data.uses : 0,
      });
    }

    // Alphabetical by source so same-platform codes group together.
    codes.sort((a, b) => a.source.localeCompare(b.source));

    return res.status(200).json({ codes, codeCount: codes.length });
  } catch (err) {
    return res.status(500).json({ error: "unexpected error", detail: String(err) });
  }
};
