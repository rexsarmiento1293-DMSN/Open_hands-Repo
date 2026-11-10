#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build installable Android APKs for every MCSN offline app (batch 1 + 2).

Reads each app folder's manifest.webmanifest for its display name, then wraps
the folder in a WebView APK via build_apk.build().
"""
import os, sys, json, glob, re, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from build_apk import build

BATCHES = [
    (os.path.join(ROOT, "apps"), os.path.join(ROOT, "apk"), "mcsn"),
    (os.path.join(ROOT, "apps-v2"), os.path.join(ROOT, "apk-v2"), "mcsn"),
]


def slug_id(folder):
    s = re.sub(r'^[0-9]+-', '', folder)
    return re.sub(r'[^a-z0-9]', '', s)


def app_name(folder_path, folder):
    mf = os.path.join(folder_path, "manifest.webmanifest")
    if os.path.exists(mf):
        try:
            return json.load(open(mf, encoding='utf-8'))["name"]
        except Exception:
            pass
    return re.sub(r'^[0-9]+-', '', folder).replace('-', ' ').title()


def main():
    total = 0
    for src, out, _ in BATCHES:
        if not os.path.isdir(src):
            continue
        os.makedirs(out, exist_ok=True)
        folders = sorted(d for d in os.listdir(src)
                         if os.path.isdir(os.path.join(src, d)) and d[0].isdigit())
        for folder in folders:
            fp = os.path.join(src, folder)
            name = app_name(fp, folder)
            icon = os.path.join(fp, "icons", "icon-192.png")
            apk_name = folder + ".apk"
            out_apk = os.path.join(out, apk_name)
            build(fp, out_apk, name, "com.mcsn.appfactory." + slug_id(folder),
                  icon if os.path.exists(icon) else None)
            print("OK %-45s -> %s (%.1f KB)" % (name, apk_name, os.path.getsize(out_apk) / 1024.0))
            total += 1
    print("Built %d APKs" % total)


if __name__ == "__main__":
    main()
