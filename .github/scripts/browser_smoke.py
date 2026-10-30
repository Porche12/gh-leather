#!/usr/bin/env python3
"""Browser smoke tests at desktop, tablet and phone sizes."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
os.chdir(ROOT)

class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args):
        pass

server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
Thread(target=server.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{server.server_port}/index.html"
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        for width,height in [(1440,900),(1024,768),(768,1024),(430,932),(390,844),(375,812),(320,720)]:
            page=browser.new_page(viewport={"width":width,"height":height},device_scale_factor=1)
            errors=[]
            offsite=[]
            page.on("pageerror",lambda error: errors.append(str(error)))
            page.on("request",lambda request: offsite.append(request.url) if not request.url.startswith("http://127.0.0.1:") else None)
            page.goto(url,wait_until="load",timeout=30000)
            page.wait_for_selector("#calc-price-display")
            page.locator("#calc-item-types [data-item='bag']").click()
            page.wait_for_timeout(80)
            assert "2 800" in page.locator("#calc-price-display").inner_text(), "Calculator did not update"
            page.locator("#portfolio-tabs [data-case='bag']").click()
            page.wait_for_function("""() => document.getElementById('ba-img-before').getAttribute('src').includes('studio_bag_before')""")
            images=page.evaluate("""() => ['ba-img-before','ba-img-after'].map(id => {
                const img=document.getElementById(id);
                return {loaded:img.complete && img.naturalWidth>0,width:img.naturalWidth,height:img.naturalHeight};
            })""")
            assert all(x["loaded"] for x in images), f"Image load failure {width}: {images}"
            assert images[0]["width"]==images[1]["width"] and images[0]["height"]==images[1]["height"], "Comparison images not aligned"
            page.locator("#ba-handle").focus()
            page.keyboard.press("ArrowLeft")
            assert int(page.locator("#ba-handle").get_attribute("aria-valuenow"))<50, "Keyboard slider failed"
            layout=page.evaluate("""() => {
                const cards=[...document.querySelectorAll('.adv-card')];
                const bad=cards.filter(card => [...card.querySelectorAll('h3,p')].some(x =>
                    x.getBoundingClientRect().right > card.getBoundingClientRect().right + 3
                    || x.getBoundingClientRect().left < card.getBoundingClientRect().left - 3));
                return {pageWidth:document.documentElement.scrollWidth, viewport:innerWidth,
                    badCards:bad.length, forms:document.querySelectorAll('form,input,textarea,iframe').length,
                    cards:cards.length, links:[...document.querySelectorAll('a')].filter(a=>a.getAttribute('href')==='#').length};
            }""")
            assert not errors, f"JS errors at {width}px: {errors[:3]}"
            assert not offsite, f"Unexpected third-party assets at {width}px: {offsite}"
            assert layout["pageWidth"]<=layout["viewport"]+5, f"Horizontal overflow at {width}: {layout}"
            assert layout["badCards"]==0 and layout["cards"]==6, f"Broken advantage layout at {width}: {layout}"
            assert layout["forms"]==0, f"Privacy regression at {width}: {layout}"
            # Header regression test: on phones only the brand and menu fit in
            # the top row. Full contact CTA and info strip must NOT be visible.
            if width<=900:
                nav=page.evaluate("""() => {
                    const rect=selector=>document.querySelector(selector)?.getBoundingClientRect().toJSON();
                    const hidden=selector=>getComputedStyle(document.querySelector(selector)).display==='none';
                    const row=rect('.navbar .nav-container');
                    const brand=rect('.navbar .brand-logo');
                    const menu=rect('#menu-toggle-btn');
                    const mainButton=rect('.navbar .desktop-only-btn');
                        const hero=rect('.hero-title');
                    return {
                      topBarHidden:hidden('.top-bar'),
                      fullCTAHidden:hidden('.navbar .desktop-only-btn'),
                      menuDisplayed:!hidden('#menu-toggle-btn'),
                      bottomDisplayed:!!document.querySelector('.mobile-bottom-bar') && !hidden('.mobile-bottom-bar'),
                      headerPosition:getComputedStyle(document.querySelector('.navbar')).position,
                      yandexBackground:getComputedStyle(document.querySelector('.yandex-badge')).backgroundColor,
                      headerHeight:row.height,
                      rowRight:row.right,
                      brandRight:brand.right,
                      menuLeft:menu.left,
                      menuRight:menu.right,
                      heroWidth:hero.width
                    };
                }""")
                assert nav["topBarHidden"] and nav["fullCTAHidden"], f"Mobile header overloaded at {width}: {nav}"
                assert nav["menuDisplayed"] and not nav["bottomDisplayed"], f"Unwanted mobile bottom overlay at {width}: {nav}"
                assert nav["headerPosition"] not in ("fixed","sticky"), f"Header obscures page during scroll at {width}: {nav}"
                assert nav["yandexBackground"] not in ("rgb(255, 204, 0)","rgb(255, 255, 0)"), f"Yellow Yandex badge remains at {width}: {nav}"
                assert nav["brandRight"] < nav["menuLeft"]+2, f"Brand overlaps menu at {width}: {nav}"
                assert nav["menuRight"]<=width+2, f"Menu clipped at {width}: {nav}"
                assert nav["headerHeight"] < 80, f"Mobile navbar is too tall at {width}: {nav}"
                assert nav["heroWidth"] > width*.6, f"Hero text too narrow {width}: {nav}"
                # Direct contact links remain available in the mobile menu.
                assert page.locator("#mobile-menu a[href^='tel:']").count() >= 1
                assert page.locator("#mobile-menu a[href^='https://wa.me/']").count() >= 1
                assert page.locator("#mobile-menu a[href='#prices']").count() >= 1
                # When scrolled to reviews, neither a fixed top bar nor a
                # bottom contact bar should cover content.
                page.get_by_role("heading", name="Отзывы на независимых картах").scroll_into_view_if_needed()
                scrolled = page.evaluate("""() => ({
                    navbarBottom: document.querySelector('.navbar').getBoundingClientRect().bottom,
                    bottomBarCount: document.querySelectorAll('.mobile-bottom-bar').length
                })""")
                assert scrolled["navbarBottom"] < 0, f"Mobile navbar remains over reviews at {width}: {scrolled}"
                assert scrolled["bottomBarCount"] == 0, f"Obstructing mobile bar markup at {width}: {scrolled}"
            if width<=768:
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(150)
                page.locator("#menu-toggle-btn").click()
                assert "open" in page.locator("#mobile-menu").get_attribute("class"), "Menu did not open"
                page.locator("#mobile-menu .mobile-nav-links a").first.click()
                assert "open" not in page.locator("#mobile-menu").get_attribute("class"), "Menu did not close"
            print(f"PASS {width}x{height}: calculator, slider, card text, layout, privacy")
            page.close()
        browser.close()
finally:
    server.shutdown()
