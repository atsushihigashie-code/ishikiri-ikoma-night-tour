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
<audio class="bgm-audio" autoplay loop preload="auto">
<source src="{rel}shared/audio/bgm-main.mp3" type="audio/mpeg" />
</audio>
<script src="{rel}shared/bgm-ducking.js"></script>
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

def map_link(lat, lng, label):
    url = f'https://www.google.com/maps/search/?api=1&query={lat},{lng}'
    return (f'<a class="map-link" href="{url}" target="_blank" rel="noopener">'
            f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">'
            f'<path d="M12 21s-7-6.5-7-11a7 7 0 0 1 14 0c0 4.5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>'
            f'Open {label} in Google Maps</a>')

def external_link(url, label):
    return (f'<a class="map-link" href="{url}" target="_blank" rel="noopener">'
            f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">'
            f'<path d="M14 3h7v7"/><path d="M10 14L21 3"/><path d="M21 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h5"/></svg>'
            f'{label}</a>')


def audio_slot(filename):
    audio_path = os.path.join(PUBLIC, "shared", "audio", filename)
    if os.path.exists(audio_path):
        return f'<audio class="stop-audio" controls preload="none" src="../shared/audio/{filename}"></audio>'
    return f'''<div class="audio-slot">
<div class="dot">♪</div>
<div>AUDIO PENDING<br/>expects: shared/audio/{filename}</div>
</div>'''

def build_route(route_key, route_dir, route_title, route_tag_label, stops, prev_root="../", welcome_extra=None):
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
    welcome_extra = welcome_extra or {}
    welcome = HEAD.format(title=f"{route_title} — Welcome", rel=prev_root)
    welcome += f'<div class="eyebrow">{route_tag_label}</div>\n'
    welcome += f'<h1 class="title">{route_title}</h1>\n'
    if welcome_extra.get("hero_image"):
        img, alt = welcome_extra["hero_image"]
        welcome += f'<img class="welcome-hero" src="{prev_root}shared/photos/{img}" alt="{alt}" />\n'
    if welcome_extra.get("narration_audio"):
        welcome += (f'<audio class="stop-audio" controls preload="none" '
                    f'src="{prev_root}shared/audio/{welcome_extra["narration_audio"]}"></audio>\n')
    if welcome_extra.get("tagline"):
        welcome += f'<p class="subtitle">{welcome_extra["tagline"]}</p>\n'

    if welcome_extra.get("stats"):
        welcome += '<div class="stat-row">\n'
        for value, label in welcome_extra["stats"]:
            welcome += f'<div class="stat"><div class="stat-value">{value}</div><div class="stat-label">{label}</div></div>\n'
        welcome += '</div>\n'

    welcome += '<div class="card">\n'
    welcome += f'<p>{stops[0]["welcome_note"]}</p>\n'
    welcome += '</div>\n'

    if welcome_extra.get("narrative"):
        welcome += '<div class="card">\n'
        welcome += '<h2>Before You Begin</h2>\n'
        welcome += welcome_extra["narrative"]
        welcome += '</div>\n'

    welcome += '<div class="card">\n<h2>What\'s Ahead</h2>\n'
    blurbs = welcome_extra.get("blurbs", [])
    for i, s in enumerate(stops):
        blurb = blurbs[i] if i < len(blurbs) else ""
        welcome += (f'<div class="ahead-row"><div class="ahead-num">{i+1:02d}</div>'
                    f'<div class="ahead-txt"><strong>{s["short"]}</strong>')
        if blurb:
            welcome += f'<div class="ahead-blurb">{blurb}</div>'
        welcome += '</div></div>\n'
    welcome += '</div>\n'

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
        short="Aramoto Station — meeting point",
        elev=20,
        title="Aramoto Station",
        subtitle="荒本駅 · Kintetsu Keihanna Line / Osaka Metro Chuo Line",
        welcome_note=(
            "An easy night out with three free-or-cheap highlights: a skyline view 22 floors "
            "up, a historic mountain cable car, and a quiet shrine town — all reachable by "
            "ordinary train, no hiking required. Nine stops, each worth lingering in — meet "
            "at Aramoto Station around 5pm (autumn season) and we'll begin."
        ),
        content=(
            "<p>You're at the foot of tonight's first stop: Higashiosaka City Hall, home to "
            "one of the region's best free night views. From here the evening climbs toward "
            "Mt. Ikoma, then eases back down into the old shrine town of Ishikiri.</p>"
            + photo_img("welcome-night-tour.jpg", "Welcome to the night tour")
            + map_link(34.6786649, 135.6047452, "Aramoto Station")
            + audio_slot("main-01-arahon-station.mp3")
            + '<div class="note"><strong>Getting here</strong>: Aramoto is served by both the '
            "Kintetsu Keihanna Line and the Osaka Metro Chuo Line (through-running services) — "
            "check which fare applies to your ticket or IC card before boarding.</div>"
            + '<div class="note"><strong>Walking to City Hall</strong>: City Hall is about a '
            "7-minute walk from the station. The east entrance is closed, so enter from the "
            "north side.</div>"
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
            + map_link(34.6794486, 135.6009840, "Higashiosaka City Hall")
            + '<div class="skyline-note"><strong>Access</strong>: 5 min walk from Exit 1 of Aramoto '
            "Station (Kintetsu Keihanna Line / Osaka Metro Chuo Line). Closed Dec 29–Jan 3.</div>"
            + '<div class="note"><strong>Finding the elevator</strong>: once inside from the '
            "north entrance, turn left and look for Elevator No. 8 — it goes straight up to "
            "the 22nd floor.</div>"
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
            + '<div class="note"><strong>Save room for the summit, if you can</strong>: the '
            "restaurant inside Ikomasanjo is genuinely one of the best dinner-with-a-view spots "
            "on this whole route, so it's worth holding out for if your schedule allows. That "
            "said, if you're too hungry to wait, on the walk back from City Hall to Aramoto "
            "Station you'll pass two solid options: <em>Jonetsu Horumon</em>, a yakiniku grill "
            "house, and <em>Osaka Ohsho</em>, a cheap-and-good Chinese diner chain.</div>"
            + photo_img("near-cityhall-yakiniku.jpg", "Jonetsu Horumon yakiniku restaurant")
            + photo_img("near-cityhall-chinese.jpg", "Osaka Ohsho Chinese diner")
            + map_link(34.6786649, 135.6047452, "Aramoto Station")
        ),
        transit="Aramoto → Ikoma · Kintetsu Keihanna Line · ~10 min, no transfer",
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
            + photo_img("cable-car-train.jpg", "Ikoma Cable train at the platform")
            + map_link(34.692398, 135.6961942, "Torii-mae Station (cable car base)")
            + audio_slot("main-04-ikoma-cable.mp3")
            + '<div class="note"><strong>Finding the platform</strong>: from Ikoma Station, '
            "follow the connecting walkway signs straight to Torii-mae Station — it's well "
            "marked. If you're unsure, ask anyone nearby or a station staff member; locals are "
            "always happy to point the way.</div>"
            + '<div class="note"><strong>Buying your ticket</strong>: tickets are sold from a '
            "machine at the platform. A round-trip ticket (¥1,000) is recommended over separate "
            "one-way fares.</div>"
            + photo_img("cable-car-ticket-machine.jpg", "Ikoma Cable ticket machine screen")
            + '<div class="note"><strong>Timing matters</strong>: departures after 18:00 run only '
            "on days the mountaintop amusement park operates its night hours — that's the whole "
            "reason tonight's route is possible. Confirm the current timetable before you go. "
            "Every train requires a transfer at Hozan-ji Station (about a 4-minute wait) before "
            "continuing up to the summit. Evening departures from Torii-mae around 19:20 connect "
            "to a 19:29 departure from Hozan-ji, arriving at Ikomasanjo by 19:36 — a good target "
            "if you're arriving from City Hall around 7pm.</div>"
        ),
    ),
    dict(
        short="Ikomasanjo summit deck",
        elev=642,
        title="Ikomasanjo Amusement Park — Star Plaza",
        subtitle="生駒山上遊園地・星の広場展望デッキ",
        welcome_note="",
        content=(
            external_link("https://www.ikomasanjou.com/images/map_en.pdf", "Tap here for the full Park Map (English, PDF)")
            + map_link(34.6792181, 135.6791714, "Ikomasanjo Amusement Park")
            + "<p>The Star Plaza observation deck won a Cool Japan Award in 2019, and it earns "
            "it: on a clear night you can pick out Abeno Harukas and Osaka Castle across the "
            "basin below, tiny points of light against the dark. This is tonight's high "
            "point — literally and otherwise.</p>"
            + photo_img("ikomasanjo-view1.jpg", "Night skyline view from Ikomasanjo")
            + photo_img("ikomasanjo-view2.jpg", "Wide night skyline from the summit")
            + audio_slot("main-05-summit-deck.mp3")
            + "<p>Beyond the view, the park itself is worth wandering — food stalls, an "
            "illuminated garden of miniature lit-up houses, and rides threading through the "
            "trees against the night sky.</p>"
            + photo_img("ikomasanjo-foodstalls.jpg", "Food stalls at Ikomasanjo at night")
            + photo_img("ikomasanjo-rides-lights.jpg", "Illuminated rides and lights at Ikomasanjo")
        ),
    ),
    dict(
        short="Dinner near Ikoma Station",
        elev=100,
        title="Dinner in Ikoma",
        subtitle="生駒駅周辺で夕食",
        welcome_note="",
        content=(
            "<p>This is honestly the best night view on the whole route — and there's a simple "
            "trick to it: order something at the Ikomasanjo restaurant, and you get to sit and "
            "eat while the entire basin glitters below you. Very few places let you pair a real "
            "meal with a view like this. If you haven't eaten yet, we'd genuinely recommend "
            "doing it here rather than saving it for later — dinner with this view is worth "
            "building your evening around. Here's the ticket-machine menu again as a reminder "
            "of what's on offer, and if you're still hungry once you reach Ishikiri, there are "
            "a few more options near Shin-Ishikiri Station too.</p>"
            + audio_slot("main-06-ikoma-dinner.mp3")
            + map_link(34.6931918, 135.6978685, "Ikoma Station")
            + photo_img("ikoma-dinner-menu1.jpg", "Restaurant ticket machine — cold udon menu")
            + photo_img("ikoma-dinner-menu2.jpg", "Restaurant ticket machine — lunch plates")
            + photo_img("ikoma-dinner-menu3.jpg", "Restaurant ticket machine — more lunch plates")
            + photo_img("ikoma-dinner-menu4.jpg", "Restaurant ticket machine — kids plates")
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
            + photo_img("ishikiri-torii-illustration.jpg", "Ishikiri Shrine torii gate under a full moon")
            + audio_slot("main-07-to-ishikiri.mp3")
            + map_link(34.6852869, 135.6554838, "Ishikiri Station")
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
            + audio_slot("main-08-approach-street.mp3")
            + "<p>Here's the thing about this street: it isn't really a tourist attraction. It's "
            "where Osaka locals come, on ordinary weeknights, for an honest answer about "
            "something on their mind. Which means it's one of the very few places on this "
            "entire tour where you're not just looking at Japan — you're standing in the middle "
            "of it, next to people who came here for their own reasons.</p>"
            "<p>Divination like this has old roots in Japan, and they run closer to Shinto "
            "than you might expect. Long before it was a way to plan your week, fortune-telling "
            "was tangled up with warding off misfortune — the same impulse behind a shrine's "
            "purification rites, where a priest would clear away bad luck and offer guidance "
            "for whatever was troubling someone. This street still carries a trace of that: "
            "half practical advice, half quiet ritual.</p>"
            + photo_img("ishikiri-shrine-night1.jpg", "Ishikiri Shrine main hall at night")
            + photo_img("ishikiri-shrine-night2.jpg", "Ishikiri Shrine approach at night")
            + map_link(34.6823097, 135.6462518, "Ishikiri Approach Street")
            + '<div class="note"><strong>Try one, or don\'t</strong> — most shops are '
            "Japanese-only, so bring a translation app, or just point, smile, and see what "
            "happens; plenty of shopkeepers are happy to work it out with a curious visitor. "
            "Not in the mood? Skip straight past — there's no schedule pressure here, this "
            "whole stop is exactly as long as you want it to be. Fortune-telling here is paid "
            "directly to the shop, separate from the tour price.</div>"
            + '<div class="note"><strong>One thing to know</strong>: most of these shops keep '
            "daytime hours and close by around 16:00, well before this tour reaches them. If "
            "a reading is something you're genuinely curious about, it's worth coming back "
            "another afternoon before 4pm.</div>"
            '<div class="note"><strong>Small confession</strong>: the person who built this '
            "tour can actually read palms. Badly, but with real conviction. Ask, if you dare.</div>"
            + audio_slot("main-08b-approach-street-outro.mp3")
        ),
    ),
    dict(
        short="Ishikiri Tsurugiya Shrine (finale)",
        elev=60,
        title="Ishikiri Tsurugiya Shrine",
        subtitle="石切劔箭神社 · \"Ishikiri-san\" · Tour finale",
        welcome_note="",
        content=(
            "<p>By day this is a busy neighborhood shrine. After dark, something shifts. The "
            "crowds thin out, the lanterns take over from the sun, and the stone lions at the "
            "gate seem to watch a little more closely. Step through, and you're stepping into "
            "a story that's said to reach back some 2,600 years — to the reign of Emperor "
            "Jinmu, the legendary first emperor of Japan, in whose era this shrine's origins "
            "are traced.</p>"
            "<p>Locals call it <em>Denbo no Kamisama</em> — a name tied to healing, and above "
            "all to <em>gan-fuji</em>, warding off cancer. This is centuries-old belief, not "
            "medical claim, and it's worth saying plainly: nothing here treats illness. But "
            "belief has its own weight. People still travel here quietly, at all hours, to "
            "pray for themselves or someone they love facing a serious diagnosis — and that "
            "unspoken urgency lingers in the air in a way no ordinary sightseeing stop ever "
            "does.</p>"
            "<p>Watch the approach to the main hall and you may see it: figures walking the "
            "same short stretch of ground again and again, a hundred times over. That's "
            "<em>ohyakudo mairi</em>, \"the hundred-times pilgrimage\" — one prayer repeated "
            "until it becomes a kind of vigil. At night, with almost no one else around, it "
            "can feel less like a tourist sight and more like something you weren't quite "
            "meant to witness.</p>"
            + photo_img("ishikiri-shrine-night3.jpg", "Ishikiri Shrine covered walkway at night")
            + map_link(34.6823097, 135.6462518, "Ishikiri Tsurugiya Shrine")
            + audio_slot("main-09-ishikiri-shrine.mp3")
            + '<div class="note"><strong>Note</strong>: there is no illumination event here — '
            "lighting is ordinary street lighting after dark. We mention this so expectations "
            "stay grounded; the shrine's atmosphere, not spectacle, is the draw. Ishikiri "
            "Station, where you started your journey home, is a short walk from here.</div>"
            + "<p>How was tonight's tour? If it brought even a little peace to your heart, or "
            "a bit of quiet strength for whatever comes next in your life — then this tour has "
            "done what it set out to do. Thank you for spending the evening with us.</p>"
        ),
    ),
]

# ---------------------------------------------------------------------------
# ALTERNATE ROUTE — Ikomasanjo closed / day-hours only (7 stops)
# ---------------------------------------------------------------------------
alt_stops = [
    dict(
        short="Aramoto Station — meeting point",
        elev=20,
        title="Aramoto Station",
        subtitle="荒本駅 · Kintetsu Keihanna Line / Osaka Metro Chuo Line",
        welcome_note=(
            "The mountaintop park is closed or off its night hours today, so tonight's easy, "
            "self-guided route trades the summit deck for a shorter cable ride to Hozanji, a "
            "Buddhist temple partway up the mountain, opening with a free skyline view and "
            "closing with a slower, quieter finale at Ishikiri Tsurugiya Shrine. Meet at "
            "Aramoto Station around 5pm (autumn season)."
        ),
        content=(
            "<p>You're at the foot of tonight's first stop: Higashiosaka City Hall, home to "
            "one of the region's best free night views.</p>"
            + photo_img("welcome-night-tour-2.jpg", "Welcome to the night tour")
            + map_link(34.6786649, 135.6047452, "Aramoto Station")
            + audio_slot("alt-01-arahon-station.mp3")
            + '<div class="note"><strong>Walking to City Hall</strong>: City Hall is about a '
            "7-minute walk from the station. The east entrance is closed, so enter from the "
            "north side.</div>"
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
            + map_link(34.6794486, 135.6009840, "Higashiosaka City Hall")
            + '<div class="skyline-note"><strong>Access</strong>: 5 min walk from Exit 1 of Aramoto '
            "Station (Kintetsu Keihanna Line / Osaka Metro Chuo Line). Closed Dec 29–Jan 3.</div>"
            + '<div class="note"><strong>Finding the elevator</strong>: once inside from the '
            "north entrance, turn left and look for Elevator No. 8 — it goes straight up to "
            "the 22nd floor.</div>"
        ),
    ),
    dict(
        short="Ride to Ikoma",
        elev=70,
        title="To Ikoma Station",
        subtitle="荒本駅 → 生駒駅 · Kintetsu Keihanna Line, no transfer",
        welcome_note="",
        content=(
            "<p>One direct ride, about 10 minutes, toward Hozanji.</p>"
            + audio_slot("alt-03-to-ikoma.mp3")
            + map_link(34.6931918, 135.6978685, "Ikoma Station")
            + '<div class="note"><strong>Getting hungry already?</strong> Dinner is still ahead, '
            "but on the walk back from City Hall to Aramoto Station you'll pass two solid "
            "options if you can't wait: <em>Jonetsu Horumon</em>, a yakiniku grill house, and "
            "<em>Osaka Ohsho</em>, a cheap-and-good Chinese diner chain. Across the road from "
            "those two, there's also a <em>Torikizoku</em> (yakitori izakaya) and a "
            "<em>Gusto</em> family restaurant — solid, familiar options either way.</div>"
            + photo_img("near-cityhall-yakiniku.jpg", "Jonetsu Horumon yakiniku restaurant")
            + photo_img("near-cityhall-chinese.jpg", "Osaka Ohsho Chinese diner")
            + map_link(34.6786649, 135.6047452, "Aramoto Station")
            + '<div class="note"><strong>Eat here, or eat later?</strong> These four options '
            "are your earliest chance at dinner tonight. If you'd rather visit Hozanji first "
            "and eat near Ikoma Station afterward instead, that works too — just know it'll "
            "be a later dinner, well past the usual dinner hour.</div>"
        ),
        transit="Aramoto → Ikoma · Kintetsu Keihanna Line · ~10 min, no transfer",
    ),
    dict(
        short="Cable to Hozanji",
        elev=280,
        title="Ikoma Cable — the Hozanji Line",
        subtitle="生駒ケーブル 宝山寺線 · Torii-mae → Hozanji",
        welcome_note="",
        content=(
            "<p>Tonight's summit deck is closed, but there's still a mountain to ride: the "
            "Hozanji Line is a completely separate stretch of track from the summit line, and "
            "it runs on its own schedule — commuters and worshippers use it daily, regardless "
            "of what's happening at the amusement park above. This was Japan's very first "
            "cable railway, opened in 1918.</p>"
            + photo_slot("Hozanji line cable car")
            + audio_slot("alt-hozanji-cable.mp3")
            + map_link(34.692398, 135.6961942, "Torii-mae Station")
            + '<div class="note"><strong>Tickets</strong>: a round trip on the Hozanji Line '
            "alone is about ¥500 — half the price of the full round trip to the summit, since "
            "you're only riding one of the two lines tonight.</div>"
            + '<div class="note"><strong>Bring a light</strong>: once you step off at Hozanji, '
            "the path ahead is mountainside and only lit where it needs to be. A flashlight "
            "(a phone will do) makes the walk up much easier.</div>"
        ),
        transit="Torii-mae → Hozanji · Ikoma Cable (Hozanji Line) · a few minutes",
    ),
    dict(
        short="Hozanji Temple",
        elev=280,
        title="Hozanji — the Mountain's Older Story",
        subtitle="宝山寺 · \"Ikoma Shoten-san\"",
        welcome_note="",
        content=(
            "<p>Known locally as <em>Ikoma Shoten-san</em>, Hozanji is a major pilgrimage site "
            "dedicated to Daishō Kangiten, a deity believed to grant worldly wishes — and its "
            "history runs deeper than almost anything else on this tour. Tradition holds that "
            "the mountain ascetic En no Gyōja trained in a cave on these grounds as far back "
            "as 655, the founding year the temple itself claims. That cave, known as "
            "<em>Hannya-kutsu</em>, is said to take its name from a copy of the Prajñāpāramitā "
            "Sutra he placed inside it. Kūkai, the monk who founded Shingon Buddhism, is also "
            "said to have trained on this same mountain.</p>"
            "<p>The temple as it stands today traces to the 17th century, when the priest "
            "Tankai — a serious scholar-monk trained at Eitai-ji in Edo and on Mt. Kōya — "
            "enshrined Daishō Kangiten here. Tankai's rituals for the deity were said to be "
            "so effective that his reputation spread widely, and Hozanji became one of the "
            "most visited temples in the region.</p>"
            + photo_slot("Hozanji temple grounds at night")
            + audio_slot("alt-hozanji-temple.mp3")
            + map_link(34.684667, 135.686556, "Hozanji Temple")
            + '<div class="note"><strong>Visiting at night</strong>: the temple grounds close '
            "to general visitors around 16:30 (16:00 in winter), but the main hall and prayer "
            "hall remain open for worship at any hour. Expect a working Buddhist temple after "
            "dark — quiet, atmospheric, and lit only by what's necessary — rather than a "
            "spectacle. It's also one of the better night-view spots on the mountain, looking "
            "out over the Nara basin.</div>"
            + '<div class="note"><strong>Bring a light</strong>: the grounds are large, and '
            "stairs and side paths beyond the main hall can get genuinely dark. Keep a "
            "flashlight handy while you explore.</div>"
        ),
    ),
    dict(
        short="Dinner near Ikoma Station",
        elev=100,
        title="Dinner in Ikoma",
        subtitle="生駒駅周辺で夕食",
        welcome_note="",
        content=(
            "<p>Ikoma Station has plenty of restaurants and cafes within a short walk — from "
            "casual izakaya to department store dining floors. Take a lap, see what looks "
            "good, and settle in before continuing on to Ishikiri.</p>"
            + audio_slot("alt-04-ikoma-dinner.mp3")
            + map_link(34.6931918, 135.6978685, "Ikoma Station")
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
            + photo_img("ishikiri-torii-illustration.jpg", "Ishikiri Shrine torii gate under a full moon")
            + audio_slot("alt-05-to-ishikiri.mp3")
            + map_link(34.6852869, 135.6554838, "Ishikiri Station")
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
            "<p>Divination like this has old roots in Japan, and they run closer to Shinto "
            "than you might expect. Long before it was a way to plan your week, fortune-telling "
            "was tangled up with warding off misfortune — the same impulse behind a shrine's "
            "purification rites, where a priest would clear away bad luck and offer guidance "
            "for whatever was troubling someone. This street still carries a trace of that: "
            "half practical advice, half quiet ritual.</p>"
            + photo_img("ishikiri-shrine-night1.jpg", "Ishikiri Shrine main hall at night")
            + photo_img("ishikiri-shrine-night2.jpg", "Ishikiri Shrine approach at night")
            + audio_slot("alt-06-approach-street.mp3")
            + map_link(34.6823097, 135.6462518, "Ishikiri Approach Street")
            + '<div class="note"><strong>Try one, or don\'t</strong> — most shops are '
            "Japanese-only, so bring a translation app, or just point, smile, and see what "
            "happens. Not in the mood? Skip past — this stop is exactly as long as you want. "
            "Fortune-telling here is paid directly to the shop, separate from the tour price.</div>"
            + '<div class="note"><strong>One thing to know</strong>: most of these shops keep '
            "daytime hours and close by around 16:00, well before this tour reaches them. If "
            "a reading is something you're genuinely curious about, it's worth coming back "
            "another afternoon before 4pm.</div>"
            '<div class="note"><strong>Small confession</strong>: the person who built this '
            "tour can actually read palms. Badly, but with real conviction. Ask, if you dare.</div>"
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
            + map_link(34.6823097, 135.6462518, "Ishikiri Tsurugiya Shrine")
            + audio_slot("alt-08-shimosha.mp3")
            + '<div class="note">Ishikiri Station, where you started your journey home, is a '
            "short walk from here.</div>"
            + "<p>How was tonight's tour? If it brought even a little peace to your heart, or "
            "a bit of quiet strength for whatever comes next in your life — then this tour has "
            "done what it set out to do. Thank you for spending the evening with us.</p>"
        ),
    ),
]

MAIN_WELCOME_EXTRA = dict(
    narration_audio="main-00-welcome.mp3",
    tagline="One coin. Two thousand six hundred years of story. A city that never sleeps, seen from above and from the ground.",
    stats=[("¥500", "One Coin"), ("642m", "Summit Height"), ("~660 BC", "Shrine Founded")],
    narrative=(
        "<h3>A Night That Climbs, Then Comes Back Down</h3>"
        "<p>Most night tours pick one thing — a view, or a shrine, or a ride — and stop there. "
        "This one does all three, in a single evening, because Higashiosaka happens to have "
        "all three within reach of each other: a free skyline deck 22 floors up, a historic "
        "cable railway that's been climbing this mountain since before most of Osaka's skyline "
        "existed, and a shrine town said to trace its roots back some 2,600 years, to the reign "
        "of Japan's legendary first emperor.</p>"
        "<h3>Why the Order Matters</h3>"
        "<p>Tonight starts high and bright, at City Hall, while the sky still holds some color. "
        "Then it climbs higher still — by cable car, up Mt. Ikoma — while the color drains out "
        "of the sky and the city below turns into a field of light. And it ends low and quiet, "
        "in a shrine town where the crowds have gone home and the lanterns do the work the sun "
        "did earlier. Ascent, then descent — into something older and stranger than a skyline.</p>"
        "<p><strong>One tip before you go</strong>: this tour's real highlight is dinner with a "
        "view at the summit. If your schedule allows, hold off on eating until you reach the "
        "restaurant inside Ikomasanjo — it's genuinely one of the best dinner-with-a-view spots "
        "on the whole route.</p>"
    ),
    blurbs=[
        "Meet here — Kintetsu Keihanna Line / Osaka Metro Chuo Line.",
        "A free, award-recognized night view, 22 floors up — tonight's opening act.",
        "One direct ride toward the base of the mountain.",
        "A historic cable railway, climbing through Hozan-ji to the summit.",
        "The high point of the night, literally — an illuminated park with a Cool Japan Award view.",
        "A break to eat, back down at Ikoma Station.",
        "One stop toward the old shrine town.",
        "A street of fortune tellers that's been read by locals for generations.",
        "A shrine said to trace back some 2,600 years — where the night quietly ends.",
    ],
)

ALT_WELCOME_EXTRA = dict(
    hero_image=("alt-welcome-night-view.jpg", "Night view from Mt. Ikoma over Osaka"),
    narration_audio="alt-00-welcome.mp3",
    tagline="One coin. Two faiths in one night — a Buddhist mountain temple and a Shinto shrine town, both after dark.",
    stats=[("¥500", "One Coin"), ("655 AD", "Hozanji Founded"), ("100x", "Ohyakudo Mairi")],
    narrative=(
        "<h3>A Night That Crosses Two Traditions</h3>"
        "<p>This route ends up being something the main route isn't: a single evening that "
        "moves between Japan's two major religious traditions. Hozanji, partway up the "
        "mountain, is a working Buddhist temple with roots to 655 AD. Ishikiri Tsurugiya "
        "Shrine, where the night ends, is Shinto, with its own much older founding legend. "
        "Very few nights let you stand in both kinds of sacred space, lit by nothing but "
        "lanterns and streetlight, within a few hours of each other.</p>"
        "<h3>A Slower Kind of Night</h3>"
        "<p>Instead of rides and lights, tonight's middle stretch is a night view over Nara "
        "from a mountainside temple, followed by more time in Ishikiri's shrine town — through "
        "its street of fortune tellers that's been read by locals for generations, and finally "
        "to the quiet ritual of <em>ohyakudo mairi</em>, a hundred-times pilgrimage walked by "
        "visitors who came for reasons of their own.</p>"
        "<p><strong>Bring a flashlight</strong>: parts of tonight's route — the temple grounds, "
        "the shrine paths — are only as bright as the lanterns and streetlight allow. A phone "
        "flashlight works, but a real one is worth packing.</p>"
    ),
    blurbs=[
        "Meet here — Kintetsu Keihanna Line / Osaka Metro Chuo Line.",
        "A free, award-recognized night view, 22 floors up — tonight's opening act.",
        "One direct ride toward Ikoma.",
        "A separate cable line, running on its own — Japan's very first cable railway.",
        "A working Buddhist temple with roots to 655 AD, and a quiet night view over Nara.",
        "A break to eat near Ikoma Station.",
        "One stop toward the old shrine town.",
        "A street of fortune tellers that's been read by locals for generations.",
        "The main hall, where the night quietly ends.",
    ],
)

build_route("main", "route-main", "Sacred Sites & Skyline Views", "MAIN ROUTE", main_stops, welcome_extra=MAIN_WELCOME_EXTRA)
build_route("alt", "route-alt", "Sacred Sites & Skyline Views (Alt.)", "ALT ROUTE", alt_stops, welcome_extra=ALT_WELCOME_EXTRA)
print("Done.")
