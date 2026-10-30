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
        for key in ("date_register","date_add","date_paid","date_end","status","is_under_control","is_delegated","registration_state"):
            if key in row: print(key+":",str(row[key])[:100])
except Exception as exc:
    print("Unable to retrieve registrar state:",type(exc).__name__)
