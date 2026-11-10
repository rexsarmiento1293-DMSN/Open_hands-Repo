# -*- coding: utf-8 -*-
"""Upload MCSN AppFactory ZIPs to Google Drive (OAuth 2.0 web-server flow).

Recommended (stable): create your OWN OAuth client (Google Cloud Console,
type = Web application, redirect URI = http://127.0.0.1:53682/), then pass it:

    export GDRIVE_CLIENT_ID=...apps.googleusercontent.com
    export GDRIVE_CLIENT_SECRET=...
    export GDRIVE_REDIRECT_URL='http://127.0.0.1:53682/?code=...'   # pasted once
    python3 upload_to_drive.py

The script exchanges the code for a refresh token, stores it in ~/.gdrive_refresh,
then uploads every ZIP in apps/downloads/ into the folder named by GDRIVE_FOLDER.

Fallback: with no env vars it uses rclone's shared public client (retiring 2026).
"""
import os, sys, json, glob, uuid
import urllib.request, urllib.parse

# Own OAuth client via env vars; falls back to rclone's public client.
CLIENT_ID = os.environ.get("GDRIVE_CLIENT_ID", "202264815644.apps.googleusercontent.com")
CLIENT_SECRET = os.environ.get("GDRIVE_CLIENT_SECRET", "X4Z3ca8xfWDb1Voo-F9a7ZxJ")
REDIRECT_URI = os.environ.get("GDRIVE_REDIRECT_URI", "http://127.0.0.1:53682/")
FOLDER_NAME = os.environ.get("GDRIVE_FOLDER", "MCSN AppFactory ZIPs")
DL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apps", "downloads")
REFRESH_FILE = os.path.expanduser("~/.gdrive_refresh")


def exchange_code(code):
    """Turn an authorization code into a refresh token and store it."""
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        "code": code, "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI}).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=60) as r:
        tok = json.load(r)
    open(REFRESH_FILE, "w").write(tok["refresh_token"])
    print("Saved refresh token to", REFRESH_FILE)
    return tok["refresh_token"]


def _refresh_token():
    tok = os.environ.get("GDRIVE_REFRESH_TOKEN", "").strip()
    if not tok:
        # allow passing the full redirected URL or just the code
        raw = os.environ.get("GDRIVE_REDIRECT_URL", "").strip()
        if raw:
            if raw.startswith("http"):
                qs = urllib.parse.urlparse(raw).query
                raw = urllib.parse.parse_qs(qs).get("code", [""])[0]
            if raw:
                return exchange_code(raw)
        if os.path.exists(REFRESH_FILE):
            tok = open(REFRESH_FILE).read().strip()
    if not tok:
        sys.exit("Missing refresh token (GDRIVE_REFRESH_TOKEN or ~/.gdrive_refresh)")
    return tok


def access_token():
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        "refresh_token": _refresh_token(), "grant_type": "refresh_token"}).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["access_token"]


def api(access, method, url, body=None):
    headers = {"Authorization": "Bearer " + access}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r) if r.status != 204 else {}


def ensure_folder(access, name):
    q = ("name='%s' and mimeType='application/vnd.google-apps.folder' "
         "and trashed=false" % name.replace("'", "\\'"))
    url = "https://www.googleapis.com/drive/v3/files?" + urllib.parse.urlencode(
        {"q": q, "fields": "files(id,name)", "spaces": "drive"})
    found = api(access, "GET", url).get("files", [])
    if found:
        return found[0]["id"]
    return api(access, "POST", "https://www.googleapis.com/drive/v3/files",
               {"name": name, "mimeType": "application/vnd.google-apps.folder"})["id"]


def upload(access, path, parent):
    name = os.path.basename(path)
    boundary = "mcsn" + uuid.uuid4().hex
    meta = json.dumps({"name": name, "parents": [parent]}).encode()
    with open(path, "rb") as f:
        media = f.read()
    body = (b"--" + boundary.encode() + b"\r\n"
            b"Content-Type: application/json; charset=UTF-8\r\n\r\n" + meta + b"\r\n"
            b"--" + boundary.encode() + b"\r\n"
            b"Content-Type: application/zip\r\n\r\n" + media + b"\r\n"
            b"--" + boundary.encode() + b"--\r\n")
    req = urllib.request.Request(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name",
        data=body, method="POST",
        headers={"Authorization": "Bearer " + access,
                 "Content-Type": "multipart/related; boundary=" + boundary})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)


def main():
    access = access_token()
    about = api(access, "GET", "https://www.googleapis.com/drive/v3/about?fields=user")
    print("Account:", about.get("user", {}).get("emailAddress"))
    folder = ensure_folder(access, FOLDER_NAME)
    zips = sorted(glob.glob(os.path.join(DL_DIR, "*.zip")))
    # put the single all-in-one bundle first
    zips.sort(key=lambda p: (0 if os.path.basename(p).startswith("ALL-") else 1, p))
    for z in zips:
        res = upload(access, z, folder)
        print("uploaded:", res.get("name"))
    print("Folder: https://drive.google.com/drive/folders/%s" % folder)


if __name__ == "__main__":
    main()
