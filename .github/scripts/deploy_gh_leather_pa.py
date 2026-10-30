#!/usr/bin/env python3
"""Safely deploy ONLY GH-Leather static files via PythonAnywhere's API.

Set the GitHub Actions repository secret PA_API_TOKEN before running.
This script never reads or writes another site's directory or reloads the
shared PythonAnywhere web app.
"""
import datetime
import hashlib
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

USER = "piknickermarket"
REMOTE = f"/home/{USER}/webnicss_app/gh-leather"
BACKUPS = f"/home/{USER}/gh-leather-deploy-backups"
PUBLIC_URL = "https://piknickermarket.pythonanywhere.com/app/gh-leather/index.html"
API = f"https://www.pythonanywhere.com/api/v0/user/{USER}/files/path"
ROOT = Path(__file__).resolve().parents[2]
TOKEN = os.environ.get("PA_API_TOKEN", "").strip()
TIMEOUT = 40


def api_request(verb, path, content=None):
    safe_path = urllib.parse.quote(path, safe="/")
    url = API + safe_path
    headers = {"Authorization": "Token " + TOKEN, "User-Agent": "gh-leather-deploy/1.0"}
    if content is not None:
        boundary = "----gh-leather-" + uuid.uuid4().hex
        body = (
            ("--" + boundary + "\r\n" +
             'Content-Disposition: form-data; name="content"; filename="asset"\r\n' +
             "Content-Type: application/octet-stream\r\n\r\n").encode()
            + content + ("\r\n--" + boundary + "--\r\n").encode()
        )
        headers["Content-Type"] = "multipart/form-data; boundary=" + boundary
    else:
        body = None
    request = urllib.request.Request(url, data=body, headers=headers, method=verb)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        if verb == "GET" and exc.code == 404:
            return 404, b""
        raise RuntimeError(
            f"PythonAnywhere API: HTTP {exc.code} for {verb} {path}; "
            "check token, API permissions and target path"
        ) from None


def get_sources():
    sources = [ROOT / "index.html", ROOT / "styles.css", ROOT / "app.js"]
    sources += sorted((ROOT / "images").rglob("*"))
    sources = [p for p in sources if p.is_file()]
    for path in sources:
        if not path.resolve().is_relative_to(ROOT):
            raise RuntimeError("Unsafe source path")
        if path.stat().st_size > 10 * 1024 * 1024:
            raise RuntimeError(f"Unexpectedly large file: {path}")
    return sources


def main():
    if not TOKEN:
        raise RuntimeError(
            "Missing GitHub Actions secret PA_API_TOKEN. In the repository, "
            "open Settings > Secrets and variables > Actions > New repository secret."
        )
    sources = get_sources()
    if len(sources) < 4:
        raise RuntimeError("Expected HTML, CSS, JS and image assets.")
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    if "GH-LEATHER" not in html.upper() or "quick-services-grid" not in html:
        raise RuntimeError("Refusing to deploy an unexpected or outdated site revision.")

    status, current_page = api_request("GET", REMOTE + "/index.html")
    if status != 200 or b"GH-LEATHER" not in current_page.upper():
        raise RuntimeError(
            "Target index.html was not found or does not appear to be GH-Leather. "
            "Aborting without touching files."
        )

    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
    changed = 0
    skipped = 0
    for local_file in sources:
        relative_path = local_file.relative_to(ROOT).as_posix()
        dest = REMOTE + "/" + relative_path
        new_data = local_file.read_bytes()
        status, old_data = api_request("GET", dest)
        if status == 200 and hashlib.sha256(old_data).digest() == hashlib.sha256(new_data).digest():
            skipped += 1
            continue

        # Backups live OUTSIDE /app/, never accessible under the static site route.
        if status == 200:
            backup_path = f"{BACKUPS}/{timestamp}/{relative_path}"
            api_request("POST", backup_path, old_data)

        result_status, _ = api_request("POST", dest, new_data)
        if result_status not in (200, 201):
            raise RuntimeError(f"Upload failed for {relative_path}: HTTP {result_status}")
        read_status, check_data = api_request("GET", dest)
        if read_status != 200 or hashlib.sha256(check_data).digest() != hashlib.sha256(new_data).digest():
            raise RuntimeError(f"Upload verification failed for {relative_path}")
        changed += 1
        print(f"Uploaded: {relative_path}")

    print(f"PythonAnywhere file API verified. Updated: {changed}; unchanged: {skipped}.")
    # Static /app/ files are served directly. Do not reload the shared WSGI app.
    url = PUBLIC_URL + "?deploy=" + urllib.parse.quote(timestamp)
    request = urllib.request.Request(url, headers={"User-Agent": "gh-leather-deploy/1.0"})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        visible_html = response.read()
        if response.status != 200 or b"quick-services-grid" not in visible_html:
            raise RuntimeError("Files uploaded, but public page does not yet show new HTML.")
    print("Public GH-Leather page verified:", PUBLIC_URL)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("Deployment failed:", str(exc), file=sys.stderr)
        sys.exit(1)
