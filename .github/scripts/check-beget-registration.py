#!/usr/bin/env python3
"""Read-only Beget registrar status for GHLeather; no passwords printed."""
import json,os,urllib.parse,urllib.request,sys
password=os.environ.get("BEGET_API_PASSWORD")
if not password: sys.exit("Missing secret.")
body=urllib.parse.urlencode({"login":"b2000an4","passwd":password,"output_format":"json"}).encode()
req=urllib.request.Request("https://api.beget.com/api/domain/getList",data=body,method="POST",headers={"Content-Type":"application/x-www-form-urlencoded"})
try:
    with urllib.request.urlopen(req,timeout=25) as r: ans=json.load(r)
    rows=ans.get("answer",{}).get("result",[])
    if isinstance(rows,dict): rows=list(rows.values())
    if not isinstance(rows,list): raise ValueError("Unexpected API payload")
    matched=[r for r in rows if isinstance(r,dict) and str(r.get("fqdn","")).lower()=="ghleather.ru"]
    print("Beget registrar list includes ghleather.ru:",bool(matched))
    for row in matched:
        for key in ("date_register","date_add","date_paid","date_end","status","is_under_control","is_delegated","registration_state","registrar_status","register_order_status","registrar","date_expire"):
            if key in row: print(key+":",str(row[key])[:100])
except Exception as exc:
    print("Unable to retrieve registrar state:",type(exc).__name__)

# Inspect only public DNS records; do not print mail or verification TXT records.
payload=urllib.parse.urlencode({
 "login":"b2000an4","passwd":password,"input_format":"json","output_format":"json",
 "input_data":json.dumps({"fqdn":"ghleather.ru"})
}).encode()
try:
    request=urllib.request.Request("https://api.beget.com/api/dns/getData",
        data=payload,method="POST",headers={"Content-Type":"application/x-www-form-urlencoded"})
    with urllib.request.urlopen(request,timeout=25) as response:
        answer=json.load(response)
    root=answer.get("answer",{}).get("result",{})
    records=root.get("records",{})
    print("Beget DNS fields:",sorted(root.keys()))
    for kind in ("A","AAAA","DNS"):
        print("Beget",kind,":",[r.get("value") for r in records.get(kind,[]) if isinstance(r,dict)])
    print("Beget DNS record types:",sorted(records.keys()))
except Exception as exc:
    print("Beget DNS lookup failed:",type(exc).__name__)
