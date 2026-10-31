# GH-Leather: HTTPS and Russia access, 31 October 2026

## Confirmed diagnosis

The public `ghleather.ru` apex points at GitHub Pages. `www.ghleather.ru` answers with Beget's shared hosting address `5.101.153.205`.

Origin checks from Globalping probes in Rostelecom (Kostroma), MTS (Novosibirsk), and Vimpelcom (Samara) all received the website with HTTP 200, but certificate verification failed with `ERR_TLS_CERT_ALTNAME_INVALID`: the server presented `*.github.io`, not `ghleather.ru`. These checks establish reachability from those probes at that time, not every Russian network or a mobile handset test. SSL Labs independently observed the same certificate on all four Pages IPv4 addresses.

GitHub's current Pages diagnostics report `https_enforced=false` and no issued domain certificate. A successful GitHub Pages build does not establish valid HTTPS.

## Changes completed

- The new editorial design is also deployed at `/atelier/`, with all fonts, images, CSS and JS served from this domain. Its assets do not depend on ChatGPT or Cloudflare.
- Sites access was changed to public as requested for customers; ChatGPT sign-in is no longer required there. Russian probes still encountered a TLS timeout or HTTP 403 on that hosting address, so it is not the recommended primary customer link.
- Scheduled checks now reject certificate failure, HTTPS downgrade, an insecure HTTP 200, and invalid root/www redirects instead of reporting a green deployment.
- Browser tests cover five widths including 320px, quote estimates, WhatsApp handoff without sending a message, mobile navigation, FAQ, local images/fonts, slider tabs and keyboard input.

## Owner actions needed to finish HTTPS

The available APIs cannot perform these two remaining account-level actions:

1. **Beget → DNS → ghleather.ru**: edit the built-in `www` alias / its DNS subzone so the website record is `CNAME www → porche12.github.io`. The old Beget website A record for **www** must no longer be active. Preserve nameservers and the main domain's MX/TXT/mail records. Beget's hosting-domain API excludes this built-in alias from `getData` and explicitly rejects creating it: `INVALID_DATA: www нельзя создать www-поддомен`.
2. **GitHub → Porche12/gh-leather → Settings → Pages**: confirm custom domain `ghleather.ru`, refresh its DNS/certificate check after the www change propagates, then enable **Enforce HTTPS** when available. The Actions integration receives HTTP 403 for the settings PUT even with `pages: write`; it cannot perform an owner's Pages settings action. The automated workflow now verifies without retrying that prohibited administrative write. If certificate provisioning remains stuck, GitHub's official troubleshooting guide describes removing and re-adding the custom domain in the owner's settings; this was not done automatically.

Owner Pages URL: https://github.com/Porche12/gh-leather/settings/pages

After those changes, run **Check GH-Leather DNS and HTTPS** from Actions. It verifies the origin trusted certificate chain, domain name, validity and redirects for all four http/https + root/www entry points. Repeat the Russian network checks with TLS `authorized=true` before claiming the warning is fixed.

## Primary documentation

- GitHub HTTPS and custom-domain DNS: https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https
- Yandex certificate warnings: https://yandex.ru/support/browser/ru/security/untrusted-sertificates
- Beget DNS administration: https://beget.com/en/kb/manual/dns
