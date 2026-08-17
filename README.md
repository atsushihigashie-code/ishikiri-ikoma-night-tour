# One Coin Night Tour — Sacred Sites & Skyline Views

Self-guided ¥500 night tour app. Plain static HTML/CSS/JS — no build step, no
framework. Deploys as-is.

Kept fully separate from the Osaka Castle Tour app: own repo, own Firebase
project, own Stripe Payment Link, own Vercel project — so nothing here can
affect that tour's sales or access codes.

## Structure

```
public/
  index.html            landing page (tour overview, buy / enter-code links)
  gate.html              access code entry
  route-select.html      route picker (protected — shown after unlocking)
  access-guard.js        include on every protected page; redirects to gate.html
                          if no valid session, mirrors the Osaka Castle Tour pattern
  shared/
    tour.css             the whole visual design
    images/spots/         drop photos here (see naming below)
    audio/                 drop narration mp3s here (see naming below)
  route-main/            8 stops — used when Ikomasanjo is running night hours
    welcome.html, stop01.html … stop08.html
  route-alt/              6 stops — used when the mountaintop park is closed
    welcome.html, stop01.html … stop06.html
  purchase/
    index.html            Stripe payment placeholder — needs a real Payment Link
    thankyou.html          shown after the last stop of either route

build_stops.py            regenerates every stop page from the data arrays
                           inside it — edit stop text/order here, not the HTML
                           files directly, then re-run: python3 build_stops.py
```

## What's done

- Full route content for both Main (8 stops) and Alt (6 stops) routes, based
  on the night tour planning notes (石切神社・生駒ケーブル・生駒山上・東大阪市役所)
- Route selection flow, access-code gate, and page-level guard on every
  protected page
- A distinctive visual design — deep indigo night sky, lantern-amber accents,
  and a signature "ascent rail" on every stop page that tracks real elevation
  gained across the tour (ground → 642m summit → 22F deck)
- Photo and audio slots on every stop, clearly marked, ready for drop-in

## What's still open (needs your accounts — I can't create these directly)

1. **Photos** — drop images into `public/shared/images/spots/`, then swap each
   `<div class="photo-slot">…</div>` block in the relevant stop HTML for an
   `<img>` tag (same pattern as the Osaka Castle Tour app). Suggested naming:
   `main-01-ishikiri-station.jpg`, `main-02-shrine-01.jpg`, etc.
2. **Audio narration** — scripts still need writing (only the existing
   Ishikiri Shrine guide script covers part of this) and recording via
   Speechma → ffmpeg to 44.1kHz, same as the castle tour's audio pipeline.
   Drop files into `public/shared/audio/` using the filenames already
   referenced in each stop's audio-slot comment.
3. **Firebase project** — create a new project (separate from
   `osaka-castle-tour`) for access-code storage. Fill in the config and
   verification logic marked `TODO(firebase)` in `gate.html`.
4. **Stripe Payment Link** — create a new link in the East River 31 Stripe
   account (separate from the castle tour's link). Wire it into
   `public/purchase/index.html` where marked `TODO(stripe)`, with its success
   URL issuing an access code (mirrors `verify-purchase.js` in the castle
   tour repo once this project has its own Firebase project to write to).
5. **GitHub repo + Vercel project** — push this folder to a new repo and
   import it into a new Vercel project. `vercel.json` is already set to
   serve `public/` with no build step.

## Editing stop content

Don't hand-edit the generated `stopNN.html` files — edit the `main_stops` /
`alt_stops` data in `build_stops.py` and re-run it. This keeps both routes'
markup, nav links, dot progress, and ascent-rail elevations consistent.

## Testing locally before Firebase is wired up

`gate.html` accepts a temporary preview code — `PREVIEW2026` — so the full
flow (unlock → route select → stops → finale) can be tested end to end
before Stripe/Firebase are connected. Remove it before launch.
