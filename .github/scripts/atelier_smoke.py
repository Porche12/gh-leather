#!/usr/bin/env python3
"""Exercise the editorial /atelier site locally; never contact messaging apps."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts" / "atelier"
VIEWPORTS = [(1440, 900), (1024, 768), (768, 1024), (390, 844), (320, 720)]
EXPECTED_PRICES = {
    "jacket": "3 500–5 500 ₽", "dye": "4 500–7 500 ₽",
    "bag": "2 800–5 000 ₽", "shoes": "2 200–4 500 ₽",
    "fur": "9 000–18 000 ₽", "tailoring": "18 000–35 000 ₽",
    "other": "После осмотра",
}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def exercise(page, width, url):
    response = page.goto(url, wait_until="load")
    assert response and response.status == 200, "Local atelier page failed to serve"
    expect(page.locator("h1")).to_contain_text("У любимых")
    page.evaluate("""async () => {
      document.querySelectorAll('img').forEach(img => img.loading = 'eager');
      await document.fonts.ready;
    }""")
    page.wait_for_function("""() => [...document.images].every(img => img.complete && img.naturalWidth > 0)""")
    overflow = page.evaluate("""() => ({viewport:innerWidth,
      document:document.documentElement.scrollWidth, body:document.body.scrollWidth})""")
    assert max(overflow["document"], overflow["body"]) <= overflow["viewport"] + 1, f"Horizontal overflow at {width}: {overflow}"

    # A real card opens the modal with its own service and price preselected.
    page.locator('.service-card[data-service="bag"]').click()
    dialog = page.locator("#consult-dialog")
    expect(dialog).to_be_visible()
    expect(page.locator("#service-select")).to_have_value("bag")
    for key, price in EXPECTED_PRICES.items():
        page.locator("#service-select").select_option(key)
        expect(page.locator("#estimate-price")).to_have_text(price)
    page.locator("#service-select").select_option("bag")
    page.locator("#request-note").fill("Потёрлись ручки любимой сумки")
    page.locator('#consult-form button[type="submit"]').click()
    opened = page.evaluate("window.__openedUrls")
    assert len(opened) == 1, "WhatsApp handoff did not prepare exactly one popup"
    target = urlsplit(opened[0]["url"])
    assert target.scheme == "https" and target.netloc == "wa.me" and target.path == "/79275103299", "Wrong WhatsApp recipient"
    message = parse_qs(target.query).get("text", [""])[0]
    assert "Реставрация ручек и уголков сумки" in message and "Потёрлись ручки" in message, "WhatsApp message lost the selected service or note"
    assert page.url == url, "Submitting the quote navigated the website"
    page.keyboard.press("Escape")
    expect(dialog).not_to_be_visible()
    assert page.evaluate("!document.body.classList.contains('modal-open')"), "Modal left page scrolling locked"

    # Native range must be usable without a pointer; tabs must support Tab/Enter.
    jacket = page.locator('[data-compare="jacket"]')
    jacket.focus()
    page.keyboard.press("Tab")
    expect(page.locator('[data-compare="bag"]')).to_be_focused()
    page.keyboard.press("Enter")
    expect(page.locator('[data-compare="bag"]')).to_have_attribute("aria-pressed", "true")
    expect(page.locator("#compare-source")).to_contain_text("Doria Bag Spa")
    expect(page.locator("#before-img")).to_have_attribute("src", "images/studio_bag_before.jpg")
    slider = page.locator("#compare-range")
    slider.focus()
    page.keyboard.press("ArrowRight")
    expect(slider).to_have_value("51")
    assert "51" in slider.get_attribute("aria-valuetext"), "Slider accessible value did not update"
    assert page.locator(".comparison").evaluate("el => el.style.getPropertyValue('--split')") == "51%", "Slider visual divider did not update"
    page.keyboard.press("Home")
    expect(slider).to_have_value("0")
    page.keyboard.press("End")
    expect(slider).to_have_value("100")
    page.locator('[data-compare="jacket"]').click()
    expect(slider).to_have_value("50")
    expect(page.locator("#compare-source")).to_contain_text("ReLeather")
    page.wait_for_function("""() => ['before-img','after-img'].every(id => {
      const img=document.getElementById(id); return img.complete && img.naturalWidth>0;
    })""")

    summaries = page.locator(".faq summary")
    summaries.nth(0).focus()
    page.keyboard.press("Enter")
    page.wait_for_function("document.querySelectorAll('.faq details')[0].open")
    summaries.nth(1).click()
    page.wait_for_function("""() => {const d=document.querySelectorAll('.faq details');return !d[0].open && d[1].open;}""")
    summaries.nth(1).click()

    if width <= 800:
        page.evaluate("window.scrollTo(0,0)")
        toggle = page.locator(".menu-toggle")
        toggle.click()
        expect(toggle).to_have_attribute("aria-expanded", "true")
        assert page.locator("#mobile-nav").evaluate("el => !el.inert"), "Mobile navigation stayed inert"
        page.locator('#mobile-nav a[href="#services"]').click()
        expect(toggle).to_have_attribute("aria-expanded", "false")
        assert page.locator("#mobile-nav").evaluate("el => el.inert"), "Closed navigation remained keyboard-active"
        page.evaluate("window.scrollTo(0,0)")
        toggle.click()
        page.keyboard.press("Escape")
        expect(toggle).to_have_attribute("aria-expanded", "false")
        expect(toggle).to_be_focused()
        assert page.evaluate("!document.body.classList.contains('modal-open')"), "Menu left page scrolling locked"
    else:
        expect(page.locator(".desktop-nav")).to_be_visible()
        expect(page.locator(".menu-toggle")).not_to_be_visible()
    page.evaluate("window.scrollTo(0,0)")


def main():
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    url = origin + "/atelier/"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                for width, height in VIEWPORTS:
                    context = browser.new_context(viewport={"width": width, "height": height}, reduced_motion="reduce")
                    errors, external, failed = [], [], []

                    def route_request(route):
                        if route.request.url.startswith(origin + "/"):
                            route.continue_()
                        else:
                            external.append(route.request.url)
                            route.abort()  # No third-party request or messaging navigation is sent.

                    context.route("**/*", route_request)
                    context.add_init_script("""window.__openedUrls=[];window.open=(url,target,features)=>{
                      window.__openedUrls.push({url:String(url),target,features});return null;
                    };""")
                    page = context.new_page()
                    page.set_default_timeout(10000)
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.on("response", lambda response: failed.append(f"{response.status} {response.url}") if response.status >= 400 else None)
                    page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
                    try:
                        exercise(page, width, url)
                        assert not errors, f"Browser errors at {width}: {errors}"
                        assert not external, f"Automatic external requests at {width}: {external}"
                        assert not failed, f"Broken assets at {width}: {failed}"
                        if width in (1440, 390, 320):
                            page.screenshot(path=str(ARTIFACTS / f"atelier-{width}.png"), full_page=True, animations="disabled")
                        print(f"PASS atelier {width}x{height}: layout, local assets and interactions")
                    except Exception:
                        page.screenshot(path=str(ARTIFACTS / f"failure-{width}.png"), full_page=True, animations="disabled")
                        raise
                    finally:
                        context.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
