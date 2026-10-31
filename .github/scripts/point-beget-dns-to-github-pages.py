#!/usr/bin/env python3
"""Keep the canonical apex ghleather.ru on GitHub Pages without changing www.

The Beget API password is read from GitHub Actions secret BEGET_API_PASSWORD.
Only apex A records may change. The www host is intentionally left untouched
because it may carry mail records. Nameservers and apex mail records are preserved.
If the domain is not delegated to Beget DNS, abort instead of guessing.
"""
import json
import os
import subprocess
import time
import sys
import re
import urllib.parse
import urllib.request
import urllib.error

BEGET_LOGIN="b2000an4"
DOMAIN="ghleather.ru"
GITHUB_PAGE_IPS=["185.199.108.153","185.199.109.153","185.199.110.153","185.199.111.153"]
PASSWORD=os.environ.get("BEGET_API_PASSWORD","")
WWW="www."+DOMAIN
WWW_TARGET="porche12.github.io"


def call(method, params=None, section="dns"):
    if not PASSWORD: raise RuntimeError("GitHub secret BEGET_API_PASSWORD not found")
    data={
        "login":BEGET_LOGIN,
        "passwd":PASSWORD,
        "output_format":"json"
    }
    if params is not None:
        data["input_format"]="json"
        data["input_data"]=json.dumps(params,ensure_ascii=False)
    req=urllib.request.Request(
        "https://api.beget.com/api/"+section+"/"+method,
        data=urllib.parse.urlencode(data).encode(),
        headers={"Content-Type":"application/x-www-form-urlencoded",
                 "User-Agent":"GHLeather-GitHubPages-DNS/1.0"},
        method="POST")
    try:
        with urllib.request.urlopen(req,timeout=25) as response:
            answer=json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError("Beget DNS API HTTP "+str(error.code)) from None
    if answer.get("status")!="success" or answer.get("answer",{}).get("status")!="success":
        wrapped=answer.get("answer",{})
        errs=wrapped.get("errors",[]) if isinstance(wrapped,dict) else []
        codes=[str(e.get("error_code","unknown")) for e in errs if isinstance(e,dict)]
        messages=[str(e.get("error_text","")) for e in errs if isinstance(e,dict)]
        diagnostic=" ".join(messages).replace(PASSWORD,"[redacted]").replace(BEGET_LOGIN,"[account]")
        diagnostic=re.sub(r"[A-Za-z0-9_+/=-]{20,}","[redacted]",diagnostic)[:180]
        raise RuntimeError("Beget DNS request rejected: "+method+" "+",".join(codes)+" "+diagnostic)
    return answer["answer"].get("result")


def unwrap(reply):
    if isinstance(reply,list):
        if len(reply)!=1 or not isinstance(reply[0],dict):
            raise RuntimeError("Ambiguous Beget DNS domain response")
        return reply[0]
    if not isinstance(reply,dict):
        raise RuntimeError("Unexpected Beget DNS response")
    return reply


def snapshot():
    entry=unwrap(call("getData",{"fqdn":DOMAIN}))
    if str(entry.get("fqdn","")).lower().rstrip(".")!=DOMAIN:
        raise RuntimeError("Beget API returned wrong domain")
    print("Beget domain status: under_control=" + str(entry.get("is_under_control")) +
          ", is_beget_dns=" + str(entry.get("is_beget_dns")) +
          ", set_type=" + str(entry.get("set_type")),flush=True)
    dns=entry.get("records",{}).get("DNS",[])
    print("Nameservers in Beget zone:",[r.get("value") for r in dns if isinstance(r,dict)],flush=True)
    dns_ready = entry.get("is_beget_dns")
    if dns_ready not in (True, 1, "1", "true", "True"):
        raise RuntimeError("Domain is not using Beget DNS; no DNS changed")
    if entry.get("is_subdomain") not in (False, 0, "0", "false", "False"):
        raise RuntimeError("Expected apex domain, got subdomain")
    if int(entry.get("set_type",0))!=1:
        raise RuntimeError("Domain uses NS/CNAME mode; refusing to overwrite")
    records=entry.get("records",{})
    if not isinstance(records,dict):
        raise RuntimeError("No DNS record data")
    return records


def formatted(records):
    return [
       {"priority":int(r.get("priority",0) or 0),"value":str(r.get("value",""))}
       for r in records if isinstance(r,dict) and r.get("value") is not None
    ]


def public_a():
    # The Beget getData API can expose null placeholders even after its
    # authoritative zone is already serving the expected real A addresses.
    # The publicly served DNS is the definitive check.
    result=subprocess.run(
        ["dig","+short","A",DOMAIN,"@1.1.1.1"],
        capture_output=True,text=True,timeout=15,check=False)
    if result.returncode:
        return []
    return [line.strip() for line in result.stdout.splitlines()
            if line.strip().count(".")==3 and all(part.isdigit() for part in line.strip().split("."))]


def public_www_cname():
    result=subprocess.run(
        ["dig","+short","CNAME",WWW,"@1.1.1.1"],
        capture_output=True,text=True,timeout=15,check=False)
    return [line.strip().lower().rstrip(".") for line in result.stdout.splitlines()
            if line.strip()] if result.returncode==0 else []


def ensure_www():
    # A stale Beget A record on www prevents GitHub's apex+www certificate.
    if public_www_cname()==[WWW_TARGET]:
        print("SUCCESS: www CNAME already points at the GitHub Pages owner.")
        return
    try:
        entry=unwrap(call("getData",{"fqdn":WWW}))
    except RuntimeError as error:
        if "getData METHOD_FAILED" not in str(error):
            raise
        raise RuntimeError(
            "Beget's built-in www alias is unavailable through getData; "
            "the owner must set www CNAME to porche12.github.io in the DNS panel. "
            "No virtual www creation, blind DNS write or mail change attempted."
        ) from None
    if str(entry.get("fqdn","")).lower().rstrip(".")!=WWW:
        raise RuntimeError("Beget returned wrong www domain; no alias changed")
    if entry.get("is_beget_dns") not in (True,1,"1","true","True"):
        raise RuntimeError("www is not managed by Beget DNS; no alias changed")
    if entry.get("is_subdomain") not in (True,1,"1","true","True"):
        raise RuntimeError("Expected www subdomain; no alias changed")
    if int(entry.get("set_type",0)) not in (1,3):
        raise RuntimeError("www is delegated elsewhere; no alias changed")
    records=entry.get("records",{})
    if any(records.get(kind) for kind in ("CAA","SRV")):
        raise RuntimeError("www contains CAA/SRV records; no alias changed")
    # CNAME cannot coexist with mail/TXT records; never silently drop these.
    if any(x["value"] for kind in ("MX","TXT")
           for x in formatted(records.get(kind,[]))):
        raise RuntimeError("www contains mail/TXT records; alias needs manual review")
    if os.environ.get("DRY_RUN","0")=="1":
        print("DRY_RUN: would set only www CNAME to "+WWW_TARGET)
        return
    if call("changeRecords",{"fqdn":WWW,"records":{
            "CNAME":[{"priority":10,"value":WWW_TARGET}]}}) is not True:
        raise RuntimeError("Beget did not confirm www alias update")
    print("SUCCESS: Beget accepted www CNAME; public propagation may take time.")


def main():
    # Avoid requiring Beget credentials when the public apex records are
    # already correct. This workflow intentionally never changes the www host.
    public=public_a()
    print("Public apex A records:",", ".join(public) or "(none)",flush=True)
    if set(public)==set(GITHUB_PAGE_IPS) and len(public)==4:
        print("SUCCESS: apex DNS already points at GitHub Pages; no Beget API or www changes required.",flush=True)
        return

    original=snapshot()
    current=[x["value"] for x in formatted(original.get("A",[]))]
    print("Beget API A records:",", ".join(current) or "(API has no concrete A values)")
    print("Public A records:",", ".join(public) or "(none)")
    print("www is not managed by this workflow; existing www and mail records are preserved.")
    # Preserve existing MX and TXT data; never overwrite nameservers or mail.
    planned={
      "A":[{"priority":10,"value":value} for value in GITHUB_PAGE_IPS]
    }
    for kind in ("MX","TXT"):
        if kind in original:
            planned[kind]=formatted(original[kind])
    if set(current)==set(GITHUB_PAGE_IPS) and len(current)==4:
        print("Beget DNS already points to GitHub Pages.")
        return
    if os.environ.get("DRY_RUN","0")=="1":
        print("DRY_RUN: would update only root A; MX/TXT retained.")
        return
    result=call("changeRecords",{"fqdn":DOMAIN,"records":planned})
    if result is not True:
        raise RuntimeError("Beget did not confirm DNS record update")
    # Beget's API may display null A placeholders after an accepted update,
    # even when the authoritative DNS is publishing all four actual addresses.
    # Allow DNS propagation and verify the publicly resolved result instead.
    for attempt in range(4):
        public=public_a()
        if set(public)==set(GITHUB_PAGE_IPS) and len(public)==4:
            print("SUCCESS: all GitHub Pages A records publicly verified.")
            return
        if attempt<3:
            time.sleep(8)
    actual=snapshot()
    new=[x["value"] for x in formatted(actual.get("A",[]))]
    if set(new)==set(GITHUB_PAGE_IPS) and len(new)==4:
        print("SUCCESS: Beget API now reports GitHub Pages IPs; public DNS propagation pending.")
        return
    raise RuntimeError("Beget accepted update but published A records still differ.")


if __name__=="__main__":
    try:
        main()
    except Exception as e:
        print("DNS SETUP ERROR:",str(e),file=sys.stderr)
        sys.exit(1)
