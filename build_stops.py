#!/usr/bin/env python3
"""Generates the static stop pages for the One Coin Night Tour app from data.
Run: python3 build_stops.py
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(ROOT, "public")

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title} — One Coin Night Tour</title>
<link rel="stylesheet" href="{rel}shared/tour.css" />
</head>
<body>
<div class="wrap">
"""

FOOT = """</div>
<script src="{rel}access-guard.js"></script>
</body>
</html>
"""

def ascent_rail_svg(elevations, idx):
    """elevations: list of (label, meters). idx: current stop index."""
    w, h = 600, 64
    n = len(elevations)
    xs = [20 + i * (w - 40) / (n - 1) for i in range(n)]
    lo = min(e for _, e in elevations)
    hi = max(e for _, e in elevations)
    span = max(hi - lo, 1)
    ys = [h - 14 - (e - lo) / span * (h - 28) for _, e in elevations]

    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    dots = []
    for i, ((label, e), x, y) in enumerate(zip(elevations, xs, ys)):
        if i == idx:
            dots.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="var(--lantern)">'
                f'<animate attributeName="r" values="5.5;7.5;5.5" dur="2.2s" repeatCount="indefinite"/></circle>'
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" fill="var(--sky-deep)"/>'
            )
        elif i < idx:
            dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="var(--lantern-dim)"/>')
        else:
            dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="var(--line)"/>')
    return f'''<div class="ascent-rail" aria-hidden="true">
<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none">
<polyline points="{pts}" fill="none" stroke="var(--line)" stroke-width="1.5"/>
{''.join(dots)}
<text x="20" y="14" class="rail-label">GROUND</text>
<text x="{w-20}" y="14" class="rail-label" text-anchor="end">{int(hi)}M</text>
</svg>
</div>'''

def dots_html(n, idx):
    spans = []
    for i in range(n):
        cls = "active" if i == idx else ("done" if i < idx else "")
        spans.append(f'<span class="{cls}"></span>')
    return f'<div class="dots">{"".join(spans)}</div>'

def photo_slot(caption):
    return f'''<div class="photo-slot" data-slot="{caption}">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="1.5"/><path d="M21 16l-5-5-4 4-3-3-5 5"/></svg>
PHOTO<br/>{caption}
</div>'''

def photo_img(filename, alt):
    return f'<img class="stop-photo" src="../shared/photos/{filename}" alt="{alt}" loading="lazy" />'


def audio_slot(filename):
    return f'''<div class="audio-slot">
<div class="dot">♪</div>
<div>AUDIO PENDING<br/>expects: shared/audio/{filename}</div>
</div>
<!-- once recorded, replace the block above with:
<audio class="stop-audio" controls src="{{rel}}shared/audio/{filename}"></audio>
-->'''

def build_route(route_key, route_dir, route_title, route_tag_label, stops, prev_root="../"):
    n = len(stops)
    elevations = [(s["short"], s["elev"]) for s in stops]
    out_dir = os.path.join(PUBLIC, route_dir)
    os.makedirs(out_dir, exist_ok=True)

    for i, s in enumerate(stops):
        fname = f"stop{i+1:02d}.html"
        prev_link = (f"stop{i:02d}.html" if i > 0 else "welcome.html")
        next_link = (f"stop{i+2:02d}.html" if i < n - 1 else "../purchase/thankyou.html")
        next_label = "Finish tour →" if i == n - 1 else "Next stop →"

        body = HEAD.format(title=s["title"], rel=prev_root)
        body += f'<div class="eyebrow">{route_tag_label} · Stop {i+1} of {n}</div>\n'
        body += f'<h1 class="title">{s["title"]}</h1>\n'
        if s.get("subtitle"):
            body += f'<p class="subtitle">{s["subtitle"]}</p>\n'
        body += ascent_rail_svg(elevations, i) + "\n"
        body += dots_html(n, i) + "\n"
        body += '<div class="card">\n'
        body += s["content"]
        body += '\n</div>\n'
        if s.get("transit"):
            body += f'<div class="transit"><div class="icon">TRANSIT</div><div class="txt">{s["transit"]}</div></div>\n'
        body += '<div class="nav-row">\n'
        body += f'<a class="nav-btn prev" href="{prev_link}">← Back</a>\n'
        body += f'<a class="nav-btn next" href="{next_link}">{next_label}</a>\n'
        body += '</div>\n'
        body += FOOT.format(rel=prev_root)

        with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
            f.write(body)

    # welcome page for this route
    welcome = HEAD.format(title=f"{route_title} — Welcome", rel=prev_root)
    welcome += f'<div class="eyebrow">{route_tag_label}</div>\n'
    welcome += f'<h1 class="title">{route_title}</h1>\n'
    welcome += '<div class="card">\n'
    welcome += f'<p>{stops[0]["welcome_note"]}</p>\n'
    welcome += '<h3>What to expect</h3>\n<ul>\n'
    for s in stops:
        welcome += f'<li>{s["short"]}</li>\n'
    welcome += '</ul>\n</div>\n'
    welcome += f'<a class="btn btn-primary" style="display:block;text-align:center" href="stop01.html">Begin the tour →</a>\n'
    welcome += FOOT.format(rel=prev_root)
    with open(os.path.join(out_dir, "welcome.html"), "w", encoding="utf-8") as f:
        f.write(welcome)

    print(f"Built {n} stops + welcome.html for {route_dir}/")


# ---------------------------------------------------------------------------
# MAIN ROUTE — 生駒山上遊園地ナイター営業日 (9 stops)
# ---------------------------------------------------------------------------
main_stops = [
    dict(
        short="Arahon Station — meeting point",
        elev=20,
        title="Arahon Station",
        subtitle="荒本駅 · Kintetsu Keihanna Line / Osaka Metro Chuo Line",
        welcome_note=(
            "Tonight's route climbs, quite literally: from a city-hall skyline view, up a "
            "mountain by cable car, then back down to a shrine town where the night ends "
            "slowly. Nine stops, each worth lingering in — meet at Arahon Station around "
            "18:00 (autumn season) and we'll begin."
        ),
        content=(
            "<p>You're at the foot of tonight's first stop: Higashiosaka City Hall, home to "
            "one of the region's best free night views. From here the evening climbs toward "
            "Mt. Ikoma, then eases back down into the old shrine town of Ishikiri.</p>"
            + photo_slot("Arahon Station exterior")
            + audio_slot("main-01-arahon-station.mp3")
            + '<div class="note"><strong>Getting here</strong>: Arahon is served by both the '
            "Kintetsu Keihanna Line and the Osaka Metro Chuo Line (through-running services) — "
            "check which fare applies to your ticket or IC card before boarding.</div>"
        ),
    ),
    dict(
        short="Higashiosaka City Hall observatory",
        elev=90,
        title="Higashiosaka City Hall Observatory",
        subtitle="東大阪市役所22階展望ロビー · Tonight's opening view",
        welcome_note="",
        content=(
            "<p>Free to enter, open until 23:00, and certified as one of Japan's Night View "
            "Heritage sites — this 22nd-floor lobby is where tonight's ascent begins. From "
            "here: Abeno Harukas, Mt. Ikoma ahead of you, the Higashiosaka junction below, "
            "and on a clear night, Awaji Island on the horizon.</p>"
            + photo_img("cityhall-entrance.jpg", "22F observatory entrance")
            + photo_img("cityhall-exterior.jpg", "Higashiosaka City Hall exterior at night")
            + photo_img("cityhall-view1.jpg", "Night skyline view from the 22F observatory")
            + photo_img("cityhall-view2.jpg", "Night skyline view toward Mt. Ikoma")
            + audio_slot("main-02-city-hall.mp3")
            + '<div class="skyline-note"><strong>Access</strong>: 5 min walk from Exit 1 of Arahon '
            "Station (Kintetsu Keihanna Line / Osaka Metro Chuo Line). Closed Dec 29–Jan 3.</div>"
        ),
    ),
    dict(
        short="Ride to Ikoma",
        elev=70,
        title="To Ikoma Station",
        subtitle="荒本駅 → 生駒駅 · Kintetsu Keihanna Line, no transfer",
        welcome_note="",
        content=(
            "<p>One direct ride, about 10 minutes, toward the base of the cable car.</p>"
            + audio_slot("main-03-to-ikoma.mp3")
        ),
        transit="Arahon → Ikoma · Kintetsu Keihanna Line · ~10 min, no transfer",
    ),
    dict(
        short="Ikoma Cable — ride the mountain",
        elev=350,
        title="Ikoma Cable",
        subtitle="生駒ケーブル · Torii-mae → Hozan-ji → Ikomasanjo",
        welcome_note="",
        content=(
            "<p>From Torii-mae Station beside Ikoma Station, the cable car climbs through "
            "Hozan-ji on its way to the summit station. This is one of the oldest cable "
            "railways in Japan, and after dark the city lights unfold below as you rise.</p>"
            + photo_slot("Cable car cabin")
            + photo_slot("View during ascent")
            + audio_slot("main-04-ikoma-cable.mp3")
            + '<div class="note"><strong>Timing matters</strong>: departures after 18:00 run only '
            "on days the mountaintop amusement park operates its night hours — that's the whole "
            "reason tonight's route is possible. Confirm the current timetable before you go.</div>"
        ),
    ),
    dict(
        short="Ikomasanjo summit deck",
        elev=642,
        title="Ikomasanjo Amusement Park — Star Plaza",
        subtitle="生駒山上遊園地・星の広場展望デッキ",
        welcome_note="",
        content=(
            "<p>The Star Plaza observation deck won a Cool Japan Award in 2019, and it earns "
            "it: on a clear night you can pick out Abeno Harukas and Osaka Castle across the "
            "basin below, tiny points of light against the dark. This is tonight's high "
            "point — literally and otherwise.</p>"
            + photo_slot("Star Plaza deck at night")
            + photo_slot("Skyline from summit")
            + audio_slot("main-05-summit-deck.mp3")
        ),
    ),
    dict(
        short="Dinner near Ikoma Station",
        elev=100,
        title="Dinner in Ikoma",
        subtitle="生駒駅周辺で夕食",
        welcome_note="",
        content=(
            "<p>Back down at Ikoma Station, settle in for dinner before the tour's final "
            "stretch — the quiet descent into Ishikiri.</p>"
            "<h3>A few options</h3>"
            "<ul>"
            "<li><strong>Doudan</strong> — izakaya, 1 min from the station, open 17:00–23:00, no closing day</li>"
            "<li><strong>Nanko</strong> — izakaya near the station</li>"
            "<li><strong>Tsukihi</strong> — 6F of Kintetsu Department Store Ikoma</li>"
            "</ul>"
            + photo_slot("Ikoma Station area at night")
            + audio_slot("main-06-ikoma-dinner.mp3")
        ),
    ),
    dict(
        short="Ride to Ishikiri",
        elev=40,
        title="To Ishikiri Station",
        subtitle="生駒駅 → 石切駅 · Kintetsu Nara Line, no transfer",
        welcome_note="",
        content=(
            "<p>Board any Express, Semi-Express, Sub-Express, or Local train toward Osaka — "
            "the Rapid Express does not stop at Ishikiri. One stop, no transfer.</p>"
            + audio_slot("main-07-to-ishikiri.mp3")
        ),
        transit="Ikoma → Ishikiri · Kintetsu Nara Line · 1 stop, no transfer",
    ),
    dict(
        short="Ishikiri Approach Street — fortune tellers & locals",
        elev=50,
        title="The Approach Street",
        subtitle="石切参道商店街 · A street built for slowing down",
        welcome_note="",
        content=(
            "<p>This narrow, sloped street is lined with more fortune-telling shops per block "
            "than almost anywhere else in Japan — palm reading, face reading, name divination, "
            "and a dozen other traditions, packed into shopfronts that have barely changed in "
            "decades. Most visitors just walk through. We'd rather you didn't.</p>"
            "<p>Here's the thing about this street: it isn't really a tourist attraction. It's "
            "where Osaka locals come, on ordinary weeknights, for an honest answer about "
            "something on their mind. Which means it's one of the very few places on this "
            "entire tour where you're not just looking at Japan — you're standing in the middle "
            "of it, next to people who came here for their own reasons.</p>"
            + photo_slot("Approach street shopfronts")
            + photo_slot("Fortune-telling shop signage")
            + audio_slot("main-08-approach-street.mp3")
            + '<div class="note"><strong>Try one, or don\'t</strong> — most shops are '
            "Japanese-only, so bring a translation app, or just point, smile, and see what "
            "happens; plenty of shopkeepers are happy to work it out with a curious visitor. "
            "Not in the mood? Skip straight past — there's no schedule pressure here, this "
            "whole stop is exactly as long as you want it to be. Fortune-telling here is paid "
            "directly to the shop, separate from the tour price.</div>"
            '<div class="note"><strong>Small confession</strong>: the person who built this '
            "tour can actually read palms. Badly, but with real conviction. Ask, if you dare.</div>"
        ),
    ),
    dict(
        short="Ishikiri Tsurugiya Shrine (finale)",
        elev=60,
        title="Ishikiri Tsurugiya Shrine",
        subtitle="石切劔箭神社 · \"Ishikiri-san\" · Tour finale",
        welcome_note="",
        content=(
            "<p>Tradition holds this shrine was founded in the second year of Emperor Jinmu's "
            "reign. Locals know it as <em>Denbo no Kamisama</em> — a place associated with "
            "healing, especially freedom from illness. The grounds are open 24 hours, and "
            "this is where tonight's route quietly comes to rest.</p>"
            "<p>Its best-known reputation is for <em>gan-fuji</em> — warding off cancer — "
            "alongside illness more broadly. This is a matter of centuries-old belief and "
            "tradition, not medical claim: many visitors come specifically to pray for "
            "themselves or a family member facing serious illness, and that quiet sense of "
            "purpose is part of what makes the atmosphere here different from an ordinary "
            "sightseeing stop.</p>"
            "<p>Look for visitors circling the approach to the main hall in slow, repeated "
            "laps — that's <em>ohyakudo mairi</em>, \"the hundred-times pilgrimage,\" one of "
            "the shrine's oldest and most visible customs, and something you'll see almost "
            "nowhere else on this scale.</p>"
            + photo_slot("Shrine main hall")
            + photo_slot("Ohyakudo mairi path")
            + audio_slot("main-09-ishikiri-shrine.mp3")
            + '<div class="note"><strong>Note</strong>: there is no illumination event here — '
            "lighting is ordinary street lighting after dark. We mention this so expectations "
            "stay grounded; the shrine's atmosphere, not spectacle, is the draw. Ishikiri "
            "Station, where you started your journey home, is a short walk from here.</div>"
        ),
    ),
]

# ---------------------------------------------------------------------------
# ALTERNATE ROUTE — Ikomasanjo closed / day-hours only (7 stops)
# ---------------------------------------------------------------------------
alt_stops = [
    dict(
        short="Arahon Station — meeting point",
        elev=20,
        title="Arahon Station",
        subtitle="荒本駅 · Kintetsu Keihanna Line / Osaka Metro Chuo Line",
        welcome_note=(
            "The mountaintop park is closed or off its night hours today, so tonight's route "
            "trades the summit deck for more time at the shrine and its street, opening with "
            "the skyline view and closing with a slower, quieter finale in Ishikiri. Meet at "
            "Arahon Station around 18:00 (autumn season)."
        ),
        content=(
            "<p>You're at the foot of tonight's first stop: Higashiosaka City Hall, home to "
            "one of the region's best free night views.</p>"
            + photo_slot("Arahon Station exterior")
            + audio_slot("alt-01-arahon-station.mp3")
        ),
    ),
    dict(
        short="Higashiosaka City Hall observatory",
        elev=90,
        title="Higashiosaka City Hall Observatory",
        subtitle="東大阪市役所22階展望ロビー · Tonight's opening view",
        welcome_note="",
        content=(
            "<p>Free to enter, open until 23:00, and certified as one of Japan's Night View "
            "Heritage sites. From the 22nd floor: Abeno Harukas, Mt. Ikoma, the Higashiosaka "
            "junction below, and on a clear night, Awaji Island on the horizon.</p>"
            + photo_img("cityhall-entrance.jpg", "22F observatory entrance")
            + photo_img("cityhall-exterior.jpg", "Higashiosaka City Hall exterior at night")
            + photo_img("cityhall-view1.jpg", "Night skyline view from the 22F observatory")
            + photo_img("cityhall-view2.jpg", "Night skyline view toward Mt. Ikoma")
            + audio_slot("alt-02-city-hall.mp3")
            + '<div class="skyline-note"><strong>Access</strong>: 5 min walk from Exit 1 of Arahon '
            "Station (Kintetsu Keihanna Line / Osaka Metro Chuo Line). Closed Dec 29–Jan 3.</div>"
        ),
    ),
    dict(
        short="Ride to Ikoma",
        elev=70,
        title="To Ikoma Station",
        subtitle="荒本駅 → 生駒駅 · Kintetsu Keihanna Line, no transfer",
        welcome_note="",
        content=(
            "<p>One direct ride, about 10 minutes, toward dinner.</p>"
            + audio_slot("alt-03-to-ikoma.mp3")
        ),
        transit="Arahon → Ikoma · Kintetsu Keihanna Line · ~10 min, no transfer",
    ),
    dict(
        short="Dinner near Ikoma Station",
        elev=100,
        title="Dinner in Ikoma",
        subtitle="生駒駅周辺で夕食",
        welcome_note="",
        content=(
            "<h3>A few options</h3>"
            "<ul>"
            "<li><strong>Doudan</strong> — izakaya, 1 min from the station, open 17:00–23:00, no closing day</li>"
            "<li><strong>Nanko</strong> — izakaya near the station</li>"
            "<li><strong>Tsukihi</strong> — 6F of Kintetsu Department Store Ikoma</li>"
            "</ul>"
            + photo_slot("Ikoma Station area at night")
            + audio_slot("alt-04-ikoma-dinner.mp3")
        ),
    ),
    dict(
        short="Ride to Ishikiri",
        elev=40,
        title="To Ishikiri Station",
        subtitle="生駒駅 → 石切駅 · Kintetsu Nara Line, no transfer",
        welcome_note="",
        content=(
            "<p>Board any Express, Semi-Express, Sub-Express, or Local train toward Osaka — "
            "the Rapid Express does not stop at Ishikiri. One stop, no transfer.</p>"
            + audio_slot("alt-05-to-ishikiri.mp3")
        ),
        transit="Ikoma → Ishikiri · Kintetsu Nara Line · 1 stop, no transfer",
    ),
    dict(
        short="Ishikiri Approach Street — fortune tellers & locals",
        elev=50,
        title="The Approach Street",
        subtitle="石切参道商店街 · A street built for slowing down",
        welcome_note="",
        content=(
            "<p>This narrow, sloped street is lined with more fortune-telling shops per block "
            "than almost anywhere else in Japan. Most visitors just walk through — but this "
            "isn't really a tourist attraction, it's where Osaka locals come on ordinary "
            "weeknights for an honest answer about something on their mind. Standing here, "
            "you're not just looking at Japan, you're in the middle of it.</p>"
            + photo_slot("Approach street shopfronts")
            + photo_slot("Fortune-telling shop signage")
            + audio_slot("alt-06-approach-street.mp3")
            + '<div class="note"><strong>Try one, or don\'t</strong> — most shops are '
            "Japanese-only, so bring a translation app, or just point, smile, and see what "
            "happens. Not in the mood? Skip past — this stop is exactly as long as you want. "
            "Fortune-telling here is paid directly to the shop, separate from the tour price.</div>"
            '<div class="note"><strong>Small confession</strong>: the person who built this '
            "tour can actually read palms. Badly, but with real conviction. Ask, if you dare.</div>"
        ),
    ),
    dict(
        short="Kamisha (Upper Shrine)",
        elev=65,
        title="Kamisha — the Upper Shrine",
        subtitle="石切劔箭神社 上之社",
        welcome_note="",
        content=(
            "<p>A quieter, elevated companion to the main shrine, about 7 minutes on foot from "
            "the station. Visiting Kamisha before the main hall is the recommended order.</p>"
            + photo_slot("Kamisha grounds")
            + audio_slot("alt-07-kamisha.mp3")
        ),
    ),
    dict(
        short="Shimosha (Main Hall, finale)",
        elev=55,
        title="Shimosha — the Main Hall",
        subtitle="石切劔箭神社 下之社 · Tour finale",
        welcome_note="",
        content=(
            "<p>The main hall and its inner sanctuary — where tonight's route quietly comes "
            "to rest. Look for visitors circling the approach in slow, repeated laps — that's "
            "<em>ohyakudo mairi</em>, \"the hundred-times pilgrimage,\" one of the shrine's "
            "oldest and most visible customs.</p>"
            + photo_slot("Shimosha main hall")
            + audio_slot("alt-08-shimosha.mp3")
            + '<div class="note">Ishikiri Station, where you started your journey home, is a '
            "short walk from here.</div>"
        ),
    ),
]

build_route("main", "route-main", "Sacred Sites & Skyline Views", "MAIN ROUTE", main_stops)
build_route("alt", "route-alt", "Sacred Sites & Skyline Views (Alt.)", "ALT ROUTE", alt_stops)
print("Done.")
