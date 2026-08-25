// /api/admin-hotel-referrals.js
//
// Admin-only endpoint: returns referral booking counts and commission
// totals for EVERY partner hotel at once, so admin-hotel-overview.html
// can show a single ranked list.
//
// POST /api/admin-hotel-referrals   body: { adminKey }

const FIREBASE_DB_URL =
  process.env.FIREBASE_DB_URL ||
  "https://ishikiri-ikoma-night-tour-default-rtdb.asia-southeast1.firebasedatabase.app";
const FIREBASE_DB_SECRET = process.env.FIREBASE_DB_SECRET;
const ADMIN_SECRET = process.env.ADMIN_SECRET;

function getJstDateString() {
  const jstOffset = 9 * 60 * 60 * 1000;
  return new Date(Date.now() + jstOffset).toISOString().slice(0, 10);
}

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
    const url = `${FIREBASE_DB_URL}/referrals.json?auth=${FIREBASE_DB_SECRET}`;
    const r = await fetch(url);
    const allData = (await r.json()) || {};

    const today = getJstDateString();
    const hotels = [];
    let grandTotalCount = 0;
    let grandTotalCommission = 0;

    for (const [hotelId, byDate] of Object.entries(allData)) {
      let totalCount = 0;
      let totalCommission = 0;
      let todayCount = 0;
      let lastDate = null;

      for (const [date, bookings] of Object.entries(byDate || {})) {
        const entries = Object.values(bookings || {});
        const count = entries.length;
        const commission = entries.reduce((sum, b) => sum + (b.commission || 0), 0);
        totalCount += count;
        totalCommission += commission;
        if (date === today) todayCount = count;
        if (!lastDate || date > lastDate) lastDate = date;
      }

      grandTotalCount += totalCount;
      grandTotalCommission += totalCommission;
      hotels.push({
        hotel: hotelId,
        todayCount,
        totalCount,
        totalCommission,
        lastBookingDate: lastDate,
      });
    }

    hotels.sort((a, b) => b.totalCount - a.totalCount);

    return res.status(200).json({
      date: today,
      hotelCount: hotels.length,
      grandTotalCount,
      grandTotalCommission,
      hotels,
    });
  } catch (err) {
    console.error("admin-hotel-referrals error:", err);
    return res.status(500).json({ error: "Server error" });
  }
};
