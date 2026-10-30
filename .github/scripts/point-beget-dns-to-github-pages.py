#!/usr/bin/env python3
"""Point ONLY ghleather.ru root A records on Beget DNS to GitHub Pages.

The Beget API password is read from GitHub Actions secret BEGET_API_PASSWORD.
No nameservers, MX, TXT, or unrelated domain/subdomain records are changed.
If the domain is not delegated to Beget DNS, abort instead of guessing.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error

BEGET_LOGIN="b2000an4"
DOMAIN="ghleather.ru"
GITHUB_PAGE_IPS=["185.199.108.153","185.199.109.153","185.199.110.153","185.199.111.153"]
PASSWORD=os.environ.get("BEGET_API_PASSWORD","")


def call(method, params):
    if not PASSWORD: raise RuntimeError("GitHub secret BEGET_API_PASSWORD not found")
    data={
        "login":BEGET_LOGIN,
        "passwd":PASSWORD,
        "output_format":"json",
        "input_format":"json",
        "input_data":json.dumps(params,ensure_ascii=False)
    }
    req=urllib.request.Request(
        "https://api.beget.com/api/dns/"+method,
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
        raise RuntimeError("Beget DNS request rejected: "+method+" "+",".join(codes))
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


def main():
    original=snapshot()
    current=[x["value"] for x in formatted(original.get("A",[]))]
    print("Current root A records:",", ".join(current) or "(none)")
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
    actual=snapshot()
    new=[x["value"] for x in formatted(actual.get("A",[]))]
    if set(new)!=set(GITHUB_PAGE_IPS):
        raise RuntimeError("Beget reported success but GitHub Pages A records differ")
    print("SUCCESS: ghleather.ru A records point to GitHub Pages.")
    print("MX/TXT values preserved; DNS propagation may take up to 24 hours.")


if __name__=="__main__":
    try:
        main()
    except Exception as e:
        print("DNS SETUP ERROR:",str(e),file=sys.stderr)
        sys.exit(1)
