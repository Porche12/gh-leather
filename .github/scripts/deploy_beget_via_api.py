#!/usr/bin/env python3
"""Deploy ONLY GH-Leather to Beget using the API secret held by GitHub Actions.

API auth:  POST HTTPS to api.beget.com with Beget account + BEGET_API_PASSWORD.
Beget API confirms the exact target site and FTP user's restricted home first.
FTP:       Dedicated account b2000an4_ghsync, auto-generated ephemeral password.
Transport: Explicit FTP over TLS with validated server certificate.
Scope:     Upload only HTML/CSS/JS/images, never delete other website assets.
The API password and FTP password are never written to log or repository.
"""
from __future__ import annotations

import ftplib
import hashlib
import io
import json
import os
from pathlib import Path
import secrets
import ssl
import string
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
ACCOUNT = "b2000an4"
FTP_SUFFIX = "ghsync"
FTP_USER = f"{ACCOUNT}_{FTP_SUFFIX}"
FTP_SERVER = f"{ACCOUNT}.beget.tech"
SITE_PATH = "ghleather.ru/public_html"
FTP_HOME = "/" + SITE_PATH
DOMAIN = "ghleather.ru"
API_ROOT = "https://api.beget.com/api"
API_PASSWORD = os.environ.get("BEGET_API_PASSWORD", "")
BUILD_SHA = os.environ.get("GITHUB_SHA", "local-test")
HTTP_TIMEOUT = 28


def api(section, method, data=None):
    if not API_PASSWORD:
        raise RuntimeError("GitHub secret BEGET_API_PASSWORD is empty or missing.")
    payload = {
        "login": ACCOUNT,
        "passwd": API_PASSWORD,
        "output_format": "json",
    }
    # Read-only getList calls take NO input_data. Beget rejects JSON format
    # without input_data with 'Cannot parse the JSON input params'.
    if data is not None:
        payload["input_format"] = "json"
        payload["input_data"] = json.dumps(data, ensure_ascii=False)
    url = f"{API_ROOT}/{section}/{method}"
    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(payload).encode("utf-8"),
        headers={"User-Agent": "GH-Leather-site-deploy/1.0",
                 "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
            data = response.read(262144)
            response_type = response.headers.get("Content-Type", "unknown")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Beget API {section}/{method}: HTTP {exc.code}") from None
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Beget API connection failed ({type(exc.reason).__name__})") from None
    try:
        if data[:2] == bytes((31, 139)):
            import gzip
            data = gzip.decompress(data)
        answer = json.loads(data.decode("utf-8-sig"))
    except (ValueError, TypeError, UnicodeError):
        clean_type = response_type.split(";")[0][:40]
        stripped = data.lstrip()
        body_kind = (
            "empty" if not stripped else
            "HTML" if stripped[:30].lower().startswith((b"<html", b"<!doctype", b"<head")) else
            "JSON-like" if stripped[:1] in (b"{", b"[") else
            "plain text" if all(32 <= c < 127 or c in (9,10,13) for c in stripped[:100]) else
            "binary/unknown"
        )
        # An API gateway may reply with a short diagnostic instead of JSON.
        # Explicitly redact the API credential, account login and long tokens.
        import re
        message = data.decode("utf-8", errors="replace").strip()
        message = message.replace(API_PASSWORD, "[REDACTED_SECRET]")
        message = message.replace(ACCOUNT, "[REDACTED_LOGIN]")
        message = re.sub(r"[A-Za-z0-9_+\\/=-]{14,}", "[REDACTED_TOKEN]", message)
        safe_message = message[:120].replace("\\n", " ")
        raise RuntimeError(
            f"Beget API returned non-JSON for {section}/{method}. "
            f"HTTP content type={clean_type}, body={body_kind}, bytes={len(data)}, "
            f"server_message={safe_message!r}."
        ) from None

    if answer.get("status") != "success":
        raise RuntimeError(
            f"Beget API request rejected: {section}/{method}, "
            f"error={answer.get('error_code', 'UNKNOWN')}"
        )
    wrapped = answer.get("answer")
    if not isinstance(wrapped, dict) or wrapped.get("status") != "success":
        codes = []
        if isinstance(wrapped, dict):
            codes = [str(e.get("error_code", "UNKNOWN")) for e in
                     wrapped.get("errors", []) if isinstance(e, dict)]
        raise RuntimeError(
            f"Beget API method rejected: {section}/{method}; codes={','.join(codes) or 'UNKNOWN'}"
        )
    return wrapped.get("result")


def verify_site():
    sites = api("site", "getList")
    if not isinstance(sites, list):
        raise RuntimeError("API did not return a website list; no changes made.")
    target = [
        item for item in sites if isinstance(item, dict)
        and str(item.get("path", "")).strip("/") == SITE_PATH
    ]
    if len(target) != 1:
        seen = [str(item.get("path")) for item in sites if isinstance(item, dict)]
        raise RuntimeError(
            f"Target {SITE_PATH} not uniquely found in Beget account. "
            f"Available paths: {', '.join(seen[:8])}"
        )
    other_domain_matches = [
        str(item.get("path", "")) for item in sites if isinstance(item, dict)
        and item is not target[0] and any(
            d.get("fqdn", "").lower().rstrip(".") == DOMAIN
            for d in item.get("domains", []) if isinstance(d, dict)
        )
    ]
    if other_domain_matches:
        raise RuntimeError("ghleather.ru is linked to another site; refusing deployment.")
    domains = [d.get("fqdn") for d in target[0].get("domains", [])
               if isinstance(d, dict)]
    print(f"Verified Beget target: {SITE_PATH}; linked domains: {domains}")
    return target[0]


def make_ftp_password():
    alphabet = string.ascii_letters + string.digits
    return "A9a" + "".join(secrets.choice(alphabet) for _ in range(29))


def prepare_ftp():
    entries = api("ftp", "getList")
    if not isinstance(entries, list):
        raise RuntimeError("FTP account list unavailable; no changes made.")
    matching = [
        entry for entry in entries if isinstance(entry, dict)
        and entry.get("login") == FTP_USER
    ]
    if len(matching) > 1:
        raise RuntimeError("Duplicate restricted FTP login; refusing to continue.")
    if matching:
        home = str(matching[0].get("homedir", "")).rstrip("/")
        if home != FTP_HOME:
            raise RuntimeError(
                "Existing FTP login points to a different directory. "
                "Password was not changed; refusing to deploy."
            )
        action = "changePassword"
        arguments = {"suffix": FTP_SUFFIX, "password": make_ftp_password()}
    else:
        action = "add"
        arguments = {
            "suffix": FTP_SUFFIX, "homedir": FTP_HOME,
            "password": make_ftp_password()
        }
    if api("ftp", action, arguments) is not True:
        raise RuntimeError(f"Beget FTP/{action} did not confirm success.")
    password = arguments["password"]
    # Confirm the scoping on the server *after* account creation/password update.
    entries = api("ftp", "getList")
    scoped = [
        row for row in entries if isinstance(row, dict)
        and row.get("login") == FTP_USER
        and str(row.get("homedir", "")).rstrip("/") == FTP_HOME
    ]
    if len(scoped) != 1:
        raise RuntimeError("FTP account scoping could not be verified; upload stopped.")
    print(f"Restricted FTP account verified: {FTP_USER} -> {FTP_HOME}")
    return password


def assets_to_upload():
    assets = [ROOT / name for name in ("index.html", "styles.css", "app.js")]
    assets.extend(sorted(p for p in (ROOT / "images").rglob("*") if p.is_file()))
    for asset in assets:
        if not asset.is_file() or not asset.resolve().is_relative_to(ROOT):
            raise RuntimeError(f"Invalid build asset: {asset}")
    if len(assets) < 10:
        raise RuntimeError(f"Site build incomplete ({len(assets)} files).")
    return assets


def upload(ftp_password):
    """Use lftp's FTPS data channel to avoid Python ftplib EOF on Beget STOR."""
    import shutil
    import subprocess

    assets = assets_to_upload()
    staging = ROOT / ".beget-build"
    staging.mkdir(exist_ok=True)
    revision_marker = f'<meta name="gh-leather-beget-version" content="{BUILD_SHA}">'
    for asset in assets:
        relative = asset.relative_to(ROOT)
        target = staging / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        data = asset.read_bytes()
        if relative.as_posix() == "index.html":
            data = data.replace(b"</head>", revision_marker.encode() + b"\n</head>", 1)
        target.write_bytes(data)

    commands = """set cmd:fail-exit true
set ftp:ssl-force true
set ftp:ssl-protect-data true
set ssl:verify-certificate true
set ftp:passive-mode true
set ftp:prefer-epsv false
set ftp:fix-pasv-address true
set net:max-retries 1
set net:timeout 12
cd /
mirror --reverse --transfer-all --parallel=1 --no-perms --verbose=1 .beget-build .
get index.html -o .beget-verify.html
bye
"""
    env = os.environ.copy()
    env["LFTP_PASSWORD"] = ftp_password
    env.pop("BEGET_API_PASSWORD", None)
    print("Starting verified TLS-only lftp upload", flush=True)
    try:
        process = subprocess.run(
            ["lftp", "--norc", "--env-password", "--user", FTP_USER,
             "ftp://" + FTP_SERVER],
            input=commands,
            capture_output=True,
            text=True,
            timeout=240,
            env=env,
            cwd=str(ROOT),
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("Encrypted FTPS upload timed out") from None

    if process.returncode != 0:
        # Do not output untrusted raw FTP server logs, which may contain paths.
        msg = "FTP server rejected transfer or verification command"
        if "certificate" in (process.stderr or "").lower():
            msg = "FTPS certificate verification failed"
        elif "permission denied" in (process.stderr or "").lower():
            msg = "FTP write permission denied"
        elif "550" in (process.stderr or ""):
            msg = "Beget FTP server returned 550 (path/permission error)"
        raise RuntimeError(f"lftp upload failed (exit={process.returncode}): {msg}")

    verify = ROOT / ".beget-verify.html"
    if not verify.is_file() or hashlib.sha256(verify.read_bytes()).digest() != hashlib.sha256((staging / "index.html").read_bytes()).digest():
        raise RuntimeError("FTPS upload finished but remote index.html checksum mismatch")
    print(f"Transferred and verified {len(assets)} GH-Leather files over explicit FTPS")


def public_check():
    marker = BUILD_SHA.encode()
    for proto in ("https", "http"):
        url = f"{proto}://{DOMAIN}/index.html?deploy={BUILD_SHA[:10]}"
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "GH-Leather-deploy-check/1.0",
                              "Cache-Control": "no-cache"})
            with urllib.request.urlopen(request, timeout=25) as response:
                payload = response.read(200000)
                if b"GH-LEATHER" in payload.upper() and marker in payload:
                    print(f"PUBLIC VERIFIED: {url}")
                    return
        except (urllib.error.URLError, TimeoutError):
            continue
    raise RuntimeError(
        "Files uploaded to verified Beget directory, but ghleather.ru is not "
        "yet serving this revision. Check domain delegation, binding and HTTPS."
    )


def main():
    if not API_PASSWORD:
        raise RuntimeError(
            "GitHub Actions secret BEGET_API_PASSWORD was not found. "
            "Enable API authentication in Beget settings and add the secret."
        )
    verify_site()
    ftp_password = prepare_ftp()
    upload(ftp_password)
    public_check()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("DEPLOY ERROR:", type(exc).__name__, str(exc), file=sys.stderr)
        sys.exit(1)
