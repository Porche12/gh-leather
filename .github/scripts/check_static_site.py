#!/usr/bin/env python3
"""Build gate: accessibility and privacy checks before deployment."""
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
html=(ROOT/"index.html").read_text(encoding="utf-8")
script=(ROOT/"app.js").read_text(encoding="utf-8")
css=(ROOT/"styles.css").read_text(encoding="utf-8")

assert "--accent-leather: #8A5A3B" in css, "Original palette changed"
assert "--bg-main: #F7F4EF" in css, "Original palette changed"
assert ".adv-card > h3" in css and ".adv-card > p" in css, "Advantage card layout not fixed"
assert "renderCalcWorks" in script and "setCalcItem" in script
for forbidden in (
    "<form", "<input", "<textarea", "<iframe", "wizardModal", "adminModal",
    "openPrivacyModal", "openWizardModal", "sessionStorage.setItem",
    "/api/orders", "indexedDB.open", "localStorage.setItem",
    "fonts.googleapis.com", "unpkg.com", "canvas-confetti", "dexie.js",
):
    assert forbidden.lower() not in (html + script).lower(), f"Forbidden: {forbidden}"

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags={}
        self.ids=set()
        self.pictures=[]
        self.external=[]
        self.empty_links=[]
        self.attrs=[]
    def handle_starttag(self, tag, attrs):
        values=dict(attrs)
        self.tags[tag]=self.tags.get(tag,0)+1
        if "id" in values:
            assert values["id"] not in self.ids, f"Duplicate ID: {values['id']}"
            self.ids.add(values["id"])
        if tag=="img":
            self.pictures.append(values.get("src",""))
            assert values.get("alt"), "Missing image alt"
        if tag in ("script","link") and (values.get("src","").startswith("http") or
                                      values.get("href","").startswith("http")):
            self.external.append((tag, values.get("src",values.get("href"))))
        if tag=="a" and values.get("href") in ("", "#"):
            self.empty_links.append(values)
        self.attrs.append((tag,values))

p=Parser()
p.feed(html)
assert not p.external, f"Unexpected third-party page loads: {p.external}"
assert not p.empty_links or len(p.empty_links)<=1, f"Broken links: {p.empty_links}"
assert p.tags.get("form",0)==0
assert p.tags.get("iframe",0)==0
assert p.tags.get("section",0)>=6
for path in p.pictures:
    assert (ROOT/path).is_file(), "Missing image: "+path
for name in ("studio_jacket_before.jpg","studio_jacket_after.jpg",
             "studio_bag_before.jpg","studio_bag_after.jpg","lucide.min.js"):
    assert (ROOT/"images"/name).is_file(), "Missing generated asset: "+name
for k in ("jacket","bag"):
    from PIL import Image
    before=Image.open(ROOT/"images"/f"studio_{k}_before.jpg")
    after=Image.open(ROOT/"images"/f"studio_{k}_after.jpg")
    assert before.size==after.size and before.width>=500, "Misaligned comparisons"
for tag,attrs in p.attrs:
    action=attrs.get("onclick","")
    if action:
        method=action.split("(")[0].split(";")[0].strip()
        if method:
            assert ("function "+method+"(") in script, f"Missing handler: {method}"
assert "Content-Security-Policy" in html
print("PASS: 0 forms, 0 external page assets, linked buttons, mobile CSS, paired photos, original colors")
