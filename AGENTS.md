
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
- Release v3.0-apks has ALL-51/36/15-APKs.zip.

## Google Drive upload (needs user OAuth once)
- `upload_to_drive.py` collects 58 ZIPs (HTML + APK bundles) -> Drive folder "MCSN AppFactory ZIPs".
- Run: GDRIVE_REDIRECT_URL='<pasted redirect url>' python3 upload_to_drive.py
- Uses rclone public client by default; own client via GDRIVE_CLIENT_ID/SECRET.
