#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build installable Android APKs from the MCSN offline HTML apps.

Each app folder (containing index.html + assets) is wrapped in a minimal
WebView Activity, then compiled with aapt2 + d8 + zipalign + apksigner.

Usage:
    python3 build_apk.py <app_dir> <output.apk> [--name "App Name"] [--icon icon.png]

Environment:
    ANDROID_SDK_ROOT  (default /opt/android-sdk)
    JAVA_HOME         (auto-detected if unset)
"""
import os, sys, shutil, subprocess, tempfile, zipfile, argparse

SDK = os.environ.get("ANDROID_SDK_ROOT", "/opt/android-sdk")
BT = os.path.join(SDK, "build-tools", "35.0.0")
PLATFORM = os.path.join(SDK, "platforms", "android-34", "android.jar")
AAPT2 = os.path.join(BT, "aapt2")
D8 = os.path.join(BT, "d8")
ZIPALIGN = os.path.join(BT, "zipalign")
APKSIGNER = os.path.join(BT, "apksigner")


def find_javac():
    jh = os.environ.get("JAVA_HOME")
    if jh and os.path.exists(os.path.join(jh, "bin", "javac")):
        return os.path.join(jh, "bin", "javac")
    for base in ("/usr/lib/jvm",):
        if os.path.isdir(base):
            for d in sorted(os.listdir(base)):
                p = os.path.join(base, d, "bin", "javac")
                if os.path.exists(p):
                    return p
    return shutil.which("javac")


JAVAC = find_javac()


def xml_escape(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;"))


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.stderr.write("CMD FAILED: %s\n%s\n%s\n" % (" ".join(map(str, cmd)), r.stdout[-3000:], r.stderr[-3000:]))
        raise SystemExit(1)
    return r


JAVA_SRC = r"""
package com.mcsn.appfactory;
import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebSettings;
import android.webkit.WebViewClient;
import android.webkit.WebChromeClient;
import android.content.Intent;
import android.net.Uri;

public class MainActivity extends Activity {
    private WebView web;
    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        web = new WebView(this);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);
        s.setDatabaseEnabled(true);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView v, String url) {
                if (url.startsWith("file://")) return false;
                try { startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url))); } catch (Exception e) {}
                return true;
            }
        });
        web.setWebChromeClient(new WebChromeClient());
        setContentView(web);
        web.loadUrl("file:///android_asset/www/index.html");
    }
    @Override
    public void onBackPressed() {
        if (web != null && web.canGoBack()) { web.goBack(); } else { super.onBackPressed(); }
    }
}
"""

MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="APPID"
    android:versionCode="1" android:versionName="1.0">
    <uses-permission android:name="android.permission.INTERNET"/>
    <application android:label="APPNAME"
        android:icon="@mipmap/ic_launcher"
        android:usesCleartextTraffic="true"
        android:allowBackup="true">
        <activity android:name="com.mcsn.appfactory.MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>
"""


def build(app_dir, out_apk, app_name, app_id, icon_png=None):
    work = tempfile.mkdtemp(prefix="apkbuild_")
    try:
        # project layout
        java_dir = os.path.join(work, "java", "com", "mcsn", "appfactory")
        os.makedirs(java_dir)
        res_dir = os.path.join(work, "res")
        os.makedirs(os.path.join(res_dir, "values"))
        assets_www = os.path.join(work, "assets", "www")
        shutil.copytree(app_dir, assets_www)
        # remove PWA-only artifacts not needed inside the APK (keep icons: the
        # in-app header shows the icon image)
        for junk in ("manifest.webmanifest", "sw.js", "README.md"):
            p = os.path.join(assets_www, junk)
            if os.path.isdir(p):
                shutil.rmtree(p)
            elif os.path.exists(p):
                os.remove(p)

        with open(os.path.join(java_dir, "MainActivity.java"), "w") as f:
            f.write(JAVA_SRC)
        with open(os.path.join(work, "AndroidManifest.xml"), "w") as f:
            f.write(MANIFEST.replace("APPID", app_id).replace("APPNAME", xml_escape(app_name)))

        # launcher icons
        make_icons(res_dir, icon_png)

        # 1) compile resources + link
        compiled = os.path.join(work, "compiled.zip")
        run([AAPT2, "compile", "--dir", res_dir, "-o", compiled])
        base_apk = os.path.join(work, "base.apk")
        run([AAPT2, "link", "-o", base_apk, "-I", PLATFORM,
             "--manifest", os.path.join(work, "AndroidManifest.xml"),
             "-R", compiled, "--java", os.path.join(work, "gen"),
             "--min-sdk-version", "24", "--target-sdk-version", "34",
             "-A", os.path.join(work, "assets")])

        # 2) compile java against android.jar (R.java not needed; icon refs
        #    are resolved by aapt2 at link time)
        classes_dir = os.path.join(work, "classes")
        os.makedirs(classes_dir)
        srcs = [os.path.join(java_dir, "MainActivity.java")]
        run([JAVAC, "--release", "8", "-classpath", PLATFORM,
             "-d", classes_dir] + srcs)

        # 3) dex
        classes_jar = os.path.join(work, "classes.jar")
        run([os.path.join(os.path.dirname(JAVAC), "jar"), "cf", classes_jar, "-C", classes_dir, "."])
        dex_dir = os.path.join(work, "dex")
        os.makedirs(dex_dir)
        run([D8, "--min-api", "24", "--output", dex_dir, "--lib", PLATFORM, classes_jar])
        classes_dex = os.path.join(dex_dir, "classes.dex")

        # 4) add dex to apk
        unsigned = os.path.join(work, "unsigned.apk")
        with zipfile.ZipFile(base_apk, "r") as zin, zipfile.ZipFile(unsigned, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                zout.writestr(item, zin.read(item.filename))
            zout.write(classes_dex, "classes.dex")

        # 5) zipalign
        aligned = os.path.join(work, "aligned.apk")
        run([ZIPALIGN, "-f", "-p", "4", unsigned, aligned])

        # 6) sign with a debug keystore (auto-created)
        ks = os.path.expanduser("~/.mcsn-debug.keystore")
        ensure_keystore(ks)
        run([APKSIGNER, "sign", "--ks", ks, "--ks-pass", "pass:android",
             "--key-pass", "pass:android", "--ks-key-alias", "mcsnkey",
             "--out", out_apk, aligned])
        # verify
        run([APKSIGNER, "verify", "--print-certs", out_apk])
        return out_apk
    finally:
        shutil.rmtree(work, ignore_errors=True)


def ensure_keystore(ks):
    if os.path.exists(ks):
        return
    keytool = os.path.join(os.path.dirname(JAVAC), "keytool")
    run([keytool, "-genkeypair", "-keystore", ks, "-alias", "mcsnkey",
         "-keyalg", "RSA", "-keysize", "2048", "-validity", "10000",
         "-storepass", "android", "-keypass", "android",
         "-dname", "CN=MCSN AppFactory, OU=Apps, O=MCSN, L=Manila, C=PH"])


def make_icons(res_dir, icon_png):
    """Create mipmap icons from a source PNG (or a generated PH-flag icon)."""
    try:
        from PIL import Image
    except ImportError:
        Image = None
    sizes = {"mipmap-mdpi": 48, "mipmap-hdpi": 72, "mipmap-xhdpi": 96,
             "mipmap-xxhdpi": 144, "mipmap-xxxhdpi": 192}
    for folder, size in sizes.items():
        d = os.path.join(res_dir, folder)
        os.makedirs(d, exist_ok=True)
        target = os.path.join(d, "ic_launcher.png")
        if icon_png and os.path.exists(icon_png) and Image:
            img = Image.open(icon_png).convert("RGBA").resize((size, size))
            img.save(target)
        elif Image:
            make_flag_icon(Image, target, size)


def make_flag_icon(Image, path, size):
    from PIL import ImageDraw
    import math
    img = Image.new("RGB", (size, size), "#0038A8")
    d = ImageDraw.Draw(img)
    d.rectangle([0, size // 2, size, size], fill="#CE1126")
    d.polygon([(0, 0), (size * 0.46, size / 2), (0, size)], fill="#FFFFFF")
    cx, cy = size * 0.15, size / 2
    sr = size * 0.07
    for i in range(8):
        a = i * math.pi / 4
        d.line([(cx + math.cos(a) * sr, cy + math.sin(a) * sr),
                (cx + math.cos(a) * sr * 1.9, cy + math.sin(a) * sr * 1.9)],
               fill="#FCD116", width=max(1, int(size * 0.012)))
    d.ellipse([cx - sr, cy - sr, cx + sr, cy + sr], fill="#FCD116")
    img.save(path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("app_dir")
    ap.add_argument("out_apk")
    ap.add_argument("--name", required=True)
    ap.add_argument("--id", default="com.mcsn.appfactory")
    ap.add_argument("--icon", default=None)
    a = ap.parse_args()
    print("JAVAC:", JAVAC)
    out = build(a.app_dir, a.out_apk, a.name, a.id, a.icon)
    print("APK:", out, os.path.getsize(out), "bytes")
