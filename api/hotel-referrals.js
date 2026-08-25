// /api/hotel-referrals.js
//
// Returns booking counts + commission for ONE partner hotel, for the
// hotel-facing dashboard page (partner-dashboard.html).
//
// GET /api/hotel-referrals?hotel=001&key=<per-hotel dashboard key>
//
// The `key` must match an HMAC of the hotel id, keyed by
// HOTEL_DASHBOARD_SECRET. This stops one partner hotel from simply
// editing the `hotel=` value in the URL to see another hotel's numbers —
// each hotel's dashboard link only works for its own id.
//
// Required env vars (FIREBASE_DB_URL / FIREBASE_DB_SECRET already set,
// same ones verify-purchase.js uses):
//   FIREBASE_DB_URL
//   FIREBASE_DB_SECRET
//   HOTEL_DASHBOARD_SECRET   (new)

const crypto = require("crypto");

const FIREBASE_DB_URL =
  process.env.FIREBASE_DB_URL ||
  "https://ishikiri-ikoma-night-tour-default-rtdb.asia-southeast1.firebasedatabase.app";
const FIREBASE_DB_SECRET = process.env.FIREBASE_DB_SECRET;
const HOTEL_DASHBOARD_SECRET = process.env.HOTEL_DASHBOARD_SECRET;

function getJstDateString() {
  const jstOffset = 9 * 60 * 60 * 1000;
  return new Date(Date.now() + jstOffset).toISOString().slice(0, 10);
}

function expectedKeyFor(hotelId) {
  return crypto
    .createHmac("sha256", HOTEL_DASHBOARD_SECRET)
    .update(hotelId)
    .digest("hex")
    .slice(0, 10);
}

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "GET") return res.status(405).json({ error: "Method not allowed" });

  const { hotel, key } = req.query;
  if (!hotel) {
    return res.status(400).json({ error: "Missing hotel id (?hotel=001)" });
  }
  if (!FIREBASE_DB_SECRET || !HOTEL_DASHBOARD_SECRET) {
    return res.status(500).json({ error: "server not configured" });
  }

  const expected = expectedKeyFor(hotel);
  if (!key || key !== expected) {
    return res.status(401).json({ error: "Missing or incorrect dashboard key for this hotel" });
  }

  try {
    const url = `${FIREBASE_DB_URL}/referrals/${encodeURIComponent(hotel)}.json?auth=${FIREBASE_DB_SECRET}`;
    const r = await fetch(url);
    const data = (await r.json()) || {};

    const today = getJstDateString();
    const byDate = {};
    const commissionByDate = {};
    let totalCount = 0;
    let totalCommission = 0;

    for (const [date, bookings] of Object.entries(data)) {
      const entries = Object.values(bookings || {});
      const count = entries.length;
      const commission = entries.reduce((sum, b) => sum + (b.commission || 0), 0);
      byDate[date] = count;
      commissionByDate[date] = commission;
      totalCount += count;
      totalCommission += commission;
    }

    const todayCount = byDate[today] || 0;
    const todayCommission = commissionByDate[today] || 0;
    const recentDates = Object.keys(byDate).sort().reverse().slice(0, 14);

    return res.status(200).json({
      hotel,
      date: today,
      todayCount,
      todayCommission,
      totalCount,
      totalCommission,
      recent: recentDates.map((d) => ({ date: d, count: byDate[d], commission: commissionByDate[d] })),
    });
  } catch (err) {
    console.error("hotel-referrals error:", err);
    return res.status(500).json({ error: "Server error" });
  }
};
