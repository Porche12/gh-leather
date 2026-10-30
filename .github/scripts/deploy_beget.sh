#!/usr/bin/env bash
# Deploy GH-Leather static files ONLY to a verified Beget public_html folder.
# Requires FTP over explicit TLS and GitHub Actions repository secrets.
set -Eeuo pipefail
umask 077

: "${BEGET_FTP_HOST:?Set BEGET_FTP_HOST secret from Beget FTP settings}"
: "${BEGET_FTP_USER:?Set BEGET_FTP_USER secret to the account FTP login}"
: "${BEGET_FTP_PASSWORD:?Set BEGET_FTP_PASSWORD in GitHub Secrets}"
: "${BEGET_FTP_PATH:?Set BEGET_FTP_PATH to a relative site path ending public_html}"

if [[ ! "$BEGET_FTP_HOST" =~ ^[a-zA-Z0-9][a-zA-Z0-9.-]*$ ]] ||
   [[ ! "$BEGET_FTP_USER" =~ ^[a-zA-Z0-9_]+$ ]]; then
    echo "Invalid FTP host/user." >&2; exit 2
fi
if [[ "$BEGET_FTP_PATH" == /* ]] ||
   [[ "$BEGET_FTP_PATH" == *'..'* ]] ||
   [[ "$BEGET_FTP_PATH" == *' '* ]] ||
   [[ "$BEGET_FTP_PATH" == *';'* ]] ||
   [[ ! "$BEGET_FTP_PATH" =~ (^|/)public_html/?$ ]]; then
    echo "Unsafe destination: expected relative path ending in public_html." >&2; exit 2
fi
for file in index.html app.js styles.css; do
    [[ -s "$file" ]] || { echo "Missing $file" >&2; exit 2; }
done
[[ -f images/studio_jacket_before.jpg && -f images/studio_bag_after.jpg ]] || {
    echo "Portfolio assets were not built" >&2; exit 2;
}

mkdir -p .beget-build
cp index.html app.js styles.css .beget-build/
cp -R images .beget-build/

# LFTP_PASSWORD is environment-only, never passed in command line arguments.
export LFTP_PASSWORD="$BEGET_FTP_PASSWORD"
unset BEGET_FTP_PASSWORD
lftp --norc --env-password --user "$BEGET_FTP_USER" "ftp://$BEGET_FTP_HOST" <<EOF
set cmd:fail-exit true
set ftp:ssl-force true
set ftp:ssl-protect-data true
set ssl:verify-certificate true
set ftp:passive-mode true
set net:max-retries 2
set net:timeout 20
cd "$BEGET_FTP_PATH"
mirror --reverse --verbose=1 --parallel=2 --no-perms ".beget-build" "."
bye
EOF
unset LFTP_PASSWORD

if [[ -n "${BEGET_PUBLIC_URL:-}" ]]; then
    if [[ ! "$BEGET_PUBLIC_URL" =~ ^https?://[a-zA-Z0-9.-]+(/.*)?$ ]]; then
        echo "Invalid public URL" >&2; exit 2
    fi
    url="${BEGET_PUBLIC_URL%/}"
    if [[ "$url" != */index.html ]]; then url="$url/index.html"; fi
    if ! curl -fsSL --retry 2 --max-time 25 "$url?deploy=${GITHUB_SHA:-manual}" | grep -qi 'GH-LEATHER'; then
        echo "Files uploaded but public page verification failed" >&2; exit 1
    fi
    echo "Beget public page verified: $url"
else
    echo "FTPS upload completed. Set BEGET_PUBLIC_URL GitHub variable for HTTP verification."
fi
