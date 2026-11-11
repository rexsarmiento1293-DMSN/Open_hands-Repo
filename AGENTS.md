
## GitHub (published)
- Repo: https://github.com/rexsarmiento1293-DMSN/Open_hands-Repo (public, main)
- Release v1.0: https://github.com/rexsarmiento1293-DMSN/Open_hands-Repo/releases/tag/v1.0
  - ALL-36-Apps.zip, MCSN-AppFactory-36-Apps.zip, mcsn-appfactory-src.tar.gz, mcsn-appfactory.bundle
- Push: needs a classic PAT with `repo` scope (the OpenHands GitHub App token is read-only).

## APK pipeline
- `build_apk.py <app_dir> <out.apk> --name "Name" --id com.mcsn.appfactory.<slug> [--icon png]`
  WebView wrapper -> aapt2 + javac(--release 8) + d8 + zipalign + apksigner (debug keystore ~/.mcsn-debug.keystore).
  Requires: ANDROID_SDK_ROOT=/opt/android-sdk, build-tools 35.0.0 (34 NPEs in d8), platform android-34, JDK 21, Pillow.
- `build_all_apks.py` builds all 51 apps -> apk/ (36) + apk-v2/ (15).
- Release v3.1-glass has ALL-51/36/15-APKs.zip + the two HTML app bundles.

## Icons + dashboard theme (v3.1)
- `icons.py` `themed_icon(path, size, emoji, name)`: each app's launcher/PWA icon is a
  unique vibrant gradient tile featuring that app's OWN emoji (movie -> film reel,
  ulam -> pan, calculator, ...). Emoji art comes from Twemoji (jsdelivr SVG), rasterised
  with `cairosvg`, cached in `.iconcache/`. Replaces the identical PH-flag icon.
- Dashboard look = **glassmorphism**: `glass_dark.css` (batch 1) and `glass_light.css`
  (batch 2) hold all styling. Frosted cards (`--glass`/`--brd` + `backdrop-filter`),
  animated `.bg span` gradient blobs, floating pill `.tabs` nav, glass header logo
  (`<img src="icons/icon-192.png">`).
- The CSS files are read at build time (`BASE_CSS`/`LIGHT_CSS = open(...).read()`), so
  edit the CSS then re-run the builders.
- `build_apk.py` keeps `icons/` inside APK assets (the in-app header shows the icon);
  it strips only manifest/sw/README.
- Rebuild: `python3 build.py && python3 build_negosyo.py` then `python3 build_all_apks.py`.

## Google Drive upload (needs user OAuth once)
- `upload_to_drive.py` collects 58 ZIPs (HTML + APK bundles) -> Drive folder "MCSN AppFactory ZIPs".
- Run: GDRIVE_REDIRECT_URL='<pasted redirect url>' python3 upload_to_drive.py
- Uses rclone public client by default; own client via GDRIVE_CLIENT_ID/SECRET.
