# MCSN AppFactory

**36 standalone offline HTML apps** — installable PWAs (Add to Home Screen), walang internet na kailangan.

By **Rex Sarmiento** (MCSN).

## Batches

| Batch | Apps | Range |
|-------|------|-------|
| Deepseek | 17 | 01–17 |
| Gemini | 14 | 18–31 |
| Grok | 5 | 32–36 |

## Ano ang nasa repo

- `apps/` — ang 36 apps (bawat isa: `index.html`, `manifest.webmanifest`, `sw.js`, `icons/`)
- `apps/index.html` — **hub** (listahan ng lahat ng apps)
- `apps/downloads.html` — downloads page (Buksan/Install + ZIP bawat app)
- `apps/downloads/` — per-app ZIPs + `ALL-36-Apps.zip` (lahat sa isang ZIP)
- `apps/MCSN-AppFactory-36-Apps.zip` — master bundle
- `apps/imahe-overview.html` — image overview
- `build.py` — generator (vanilla JS, walang framework; mobile-first; localStorage)
- `qrcode.min.js` — offline QR lib (inlined sa QR apps)

## Paano gamitin

**I-download lahat (isang ZIP):** `apps/downloads/ALL-36-Apps.zip`

**Bawat app:** buksan ang `apps/downloads.html` at i-tap ang **ZIP** o **Buksan / Install**.

**I-preview:** i-serve ang `apps/` folder, halimbawa:
```
cd apps && python3 -m http.server 12000
```
tapos buksan ang `http://localhost:12000/` sa Chrome → **Add to Home Screen** para maging app.

## I-rebuild

```
pip install Pillow
python3 build.py
```

Bawat app = 4 screens: **Home / Input / Resulta / Tapos Na**. Offline, mobile-first, state sa localStorage. Ang PWA icons ay logo ng **bandila ng Pilipinas**.
