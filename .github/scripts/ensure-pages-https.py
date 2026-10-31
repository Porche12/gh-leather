#!/usr/bin/env python3
"""Refresh the attached GH-Leather Pages domain and require verified HTTPS.

Run in GitHub Actions with GH_TOKEN, GITHUB_REPOSITORY and pages: write.
Never detaches the domain or changes the audience/source. Certificate issuance
may take longer than this run: a pending certificate fails the run so a later
scheduled run can retry. No HTTP fallback can turn a TLS failure into success.
"""
from __future__ import annotations

import http.client
import json
import os
import re
import socket
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

DOMAIN = "ghleather.ru"
WWW_DOMAIN = "www." + DOMAIN
TIMEOUT = 20
REDIRECT_CODES = {301, 302, 303, 307, 308}


class VerificationError(RuntimeError):
    """A safe, user-facing diagnostic without credentials or response bodies."""


class GitHubPagesClient:
    def __init__(self, repository: str, token: str):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
            raise VerificationError("GITHUB_REPOSITORY must identify owner/repository.")
        if not token:
            raise VerificationError("GH_TOKEN is missing; supply a token with pages: write.")
        self.url = "https://api.github.com/repos/" + repository + "/pages"
        self.token = token

    def call(self, method: str, data: dict | None = None):
        body = json.dumps(data).encode("utf-8") if data is not None else None
        request = urllib.request.Request(
            self.url,
            data=body,
            method=method,
            headers={
                "Authorization": "Bearer " + self.token,
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
                "User-Agent": "GH-Leather-HTTPS-verification/1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                payload = response.read(262144)
        except urllib.error.HTTPError as error:
            code = error.code
            error.close()
            if code == 422 and data == {"https_enforced": True}:
                raise VerificationError(
                    "GitHub Pages cannot enable HTTPS yet (HTTP 422). The domain "
                    "certificate may still be pending. Domain remains attached; "
                    "retry after certificate issuance."
                ) from None
            if code in (401, 403, 404):
                raise VerificationError(
                    f"GitHub Pages API {method} failed (HTTP {code}). Check the "
                    "repository, Pages configuration and token pages: write permission."
                ) from None
            raise VerificationError(
                f"GitHub Pages API {method} failed (HTTP {code}); no response body logged."
            ) from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise VerificationError("Cannot reach the GitHub Pages API over verified HTTPS.") from None
        if not payload:
            return None
        try:
            result = json.loads(payload)
        except (ValueError, UnicodeError):
            raise VerificationError("GitHub Pages API returned an invalid JSON response.") from None
        if not isinstance(result, dict):
            raise VerificationError("GitHub Pages API returned an unexpected response shape.")
        return result


def require_attached_domain(settings):
    if not isinstance(settings, dict) or settings.get("cname") != DOMAIN:
        raise VerificationError(
            "Pages is not attached to exactly ghleather.ru. No domain change or "
            "detach was attempted; inspect the repository Pages configuration."
        )


def configure_https(client):
    require_attached_domain(client.call("GET"))
    # Repeat only the existing value. Never send null/empty cname or DELETE.
    client.call("PUT", {"cname": DOMAIN})
    require_attached_domain(client.call("GET"))
    # The API rejects enforcement while its certificate is unavailable. Let it
    # decide readiness rather than relying on undocumented certificate states.
    client.call("PUT", {"https_enforced": True})
    settings = client.call("GET")
    require_attached_domain(settings)
    if settings.get("https_enforced") is not True:
        raise VerificationError("Pages has not confirmed HTTPS enforcement; retry later.")
    print("Pages confirms ghleather.ru is attached and HTTPS enforcement is enabled.")


def verify_tls_host(hostname: str):
    # Direct origin connection on the Actions runner. create_default_context
    # requires a trusted chain and wrap_socket checks the requested hostname.
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, 443), timeout=TIMEOUT) as raw:
            with context.wrap_socket(raw, server_hostname=hostname) as secure:
                certificate = secure.getpeercert()
    except ssl.SSLCertVerificationError:
        raise VerificationError(
            f"Origin TLS certificate for {hostname} failed trusted-chain, "
            "hostname or validity verification. Certificate issuance may be pending."
        ) from None
    except (ssl.SSLError, OSError, TimeoutError):
        raise VerificationError(f"Cannot establish a verified origin TLS connection to {hostname}.") from None
    if not certificate:
        raise VerificationError(f"Origin {hostname} did not provide a verified TLS certificate.")
    print(f"Origin TLS chain, hostname and validity verified: {hostname}.")


def request_status(url: str):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in ("http", "https") or parsed.hostname not in (DOMAIN, WWW_DOMAIN):
        raise VerificationError("Refusing an unexpected origin or protocol during redirect checks.")
    if parsed.username or parsed.password or parsed.port not in (None, 80 if parsed.scheme == "http" else 443):
        raise VerificationError("Unexpected credentials or port in a redirect URL.")
    connection_type = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
    kwargs = {"timeout": TIMEOUT}
    if parsed.scheme == "https":
        kwargs["context"] = ssl.create_default_context()
    connection = connection_type(parsed.hostname, **kwargs)
    path = urllib.parse.urlunsplit(("", "", parsed.path or "/", parsed.query, ""))
    try:
        connection.request("HEAD", path, headers={"User-Agent": "GH-Leather-HTTPS-verification/1.0"})
        response = connection.getresponse()
        status, location = response.status, response.getheader("Location")
        response.close()
        return status, location
    except (OSError, ssl.SSLError, http.client.HTTPException):
        raise VerificationError(f"Origin {parsed.hostname} failed the {parsed.scheme.upper()} response check.") from None
    finally:
        connection.close()


def verify_redirect_chain(start_url: str, *, require_redirect: bool):
    current = start_url
    seen = set()
    was_secure = current.startswith("https://")
    redirects = 0
    for _ in range(6):
        if current in seen:
            raise VerificationError("Origin returned a redirect loop.")
        seen.add(current)
        status, location = request_status(current)
        if status in REDIRECT_CODES:
            if not location:
                raise VerificationError("Origin returned a redirect without a Location header.")
            destination = urllib.parse.urljoin(current, location)
            parsed = urllib.parse.urlsplit(destination)
            if parsed.scheme not in ("http", "https") or parsed.hostname not in (DOMAIN, WWW_DOMAIN):
                raise VerificationError("Origin redirects visitors outside the expected GH-Leather domains.")
            if was_secure and parsed.scheme != "https":
                raise VerificationError("Origin redirects HTTPS visitors back to insecure HTTP.")
            was_secure = was_secure or parsed.scheme == "https"
            current = destination
            redirects += 1
            continue
        final = urllib.parse.urlsplit(current)
        if status != 200 or final.scheme != "https" or final.hostname != DOMAIN:
            raise VerificationError(
                "Origin must finish at HTTPS ghleather.ru with status 200; "
                f"observed HTTP status {status}."
            )
        if require_redirect and not redirects:
            raise VerificationError("HTTP/www entry point did not redirect to the canonical HTTPS domain.")
        print(f"Origin entry verified: {start_url} -> https://{DOMAIN}/ (HTTP 200).")
        return
    raise VerificationError("Origin returned too many redirects.")


def verify_live_site():
    verify_tls_host(DOMAIN)
    verify_tls_host(WWW_DOMAIN)
    verify_redirect_chain("https://" + DOMAIN + "/", require_redirect=False)
    verify_redirect_chain("http://" + DOMAIN + "/", require_redirect=True)
    verify_redirect_chain("https://" + WWW_DOMAIN + "/", require_redirect=True)
    verify_redirect_chain("http://" + WWW_DOMAIN + "/", require_redirect=True)


def main():
    client = GitHubPagesClient(os.environ.get("GITHUB_REPOSITORY", ""), os.environ.get("GH_TOKEN", ""))
    if "--verify-only" in sys.argv[1:]:
        settings = client.call("GET")
        require_attached_domain(settings)
        if settings.get("https_enforced") is not True:
            raise VerificationError(
                "HTTPS is not enforced. The repository owner must finish certificate "
                "provisioning and enable Enforce HTTPS in Settings > Pages. "
                "No administrative API write attempted."
            )
    else:
        configure_https(client)
    verify_live_site()
    print("PASS: real-origin certificates, HTTPS enforcement and canonical redirects verified.")


if __name__ == "__main__":
    try:
        main()
    except VerificationError as error:
        print("HTTPS VERIFICATION FAILED:", str(error), file=sys.stderr)
        sys.exit(1)
    except Exception:
        # Never expose an unexpected exception containing a request/header/token.
        print("HTTPS VERIFICATION FAILED: unexpected error; no sensitive details logged.", file=sys.stderr)
        sys.exit(1)
