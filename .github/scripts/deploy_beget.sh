#!/usr/bin/env bash
# Deploy GH-Leather static files ONLY as a restricted b2000an4_gh account.
# Requires FTP over explicit TLS and GitHub Actions repository secrets.
set -Eeuo pipefail
umask 077

# FTP account b2000an4_gh MUST be rooted by its owner in
# ghleather.ru/public_html via the Beget control panel, never in account /.
BEGET_FTP_HOST="b2000an4.beget.tech"
BEGET_FTP_USER="b2000an4_gh"
BEGET_FTP_PATH="."
: "${BEGET_FTP_PASSWORD:?Add a GitHub Actions repository secret BEGET_FTP_PASSWORD}"

# No configurable target path: the restricted FTP account opens inside the site.
# This prevents any automated uploads to another Beget site.
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
