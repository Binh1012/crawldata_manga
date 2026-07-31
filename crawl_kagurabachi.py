import os
import json
import time
import requests

from playwright.sync_api import sync_playwright


# ==========================
# CONFIG
# ==========================

URL = "https://comix.to/title/0y7jv-bakemonogatari/2051162-chapter-193"

OUTPUT = "output"

HEADLESS = False

# ==========================


os.makedirs(OUTPUT, exist_ok=True)


def download(url, filename):
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()

        with open(filename, "wb") as f:
            f.write(r.content)

        print("✓", filename)

    except Exception as e:
        print("Download error:", e)


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=HEADLESS,
        args=[
            "--disable-blink-features=AutomationControlled"
        ]
    )

    page = browser.new_page(
        viewport={
            "width": 1400,
            "height": 2000
        }
    )

    print("Opening chapter...")

    page.goto(
        URL,
        wait_until="networkidle",
        timeout=120000
    )

    print(page.title())

    # ==========================
    # Scroll tới cuối
    # ==========================

    last_count = 0

    while True:

        page.evaluate("""
            window.scrollBy(0, 2500);
        """)

        page.wait_for_timeout(700)

        count = page.locator("img.rpage-page__img").count()

        print("Images:", count)

        if count == last_count:

            page.evaluate("""
                window.scrollBy(0, 4000);
            """)

            page.wait_for_timeout(1200)

            count2 = page.locator("img.rpage-page__img").count()

            if count2 == count:
                break

        last_count = count

    print("\nDone scrolling.\n")

    # ==========================
    # Lấy URL
    # ==========================

    imgs = page.locator("img.rpage-page__img")

    urls = []

    for i in range(imgs.count()):

        src = imgs.nth(i).get_attribute("src")

        if src:
            urls.append(src)

    urls = list(dict.fromkeys(urls))

    print("Total images:", len(urls))

    # ==========================
    # Save JSON
    # ==========================

    json_path = os.path.join(OUTPUT, "chapter.json")

    with open(json_path, "w", encoding="utf-8") as f:

        json.dump(
            {
                "url": URL,
                "pages": len(urls),
                "images": urls
            },
            f,
            indent=4,
            ensure_ascii=False
        )

    print("Saved:", json_path)

    # ==========================
    # Download
    # ==========================

    headers = {
        "Referer": "https://comix.to/",
        "User-Agent":
            "Mozilla/5.0"
    }

    session = requests.Session()
    session.headers.update(headers)

    for i, url in enumerate(urls, 1):

        ext = ".jpg"

        if ".png" in url:
            ext = ".png"

        filename = os.path.join(
            OUTPUT,
            f"{i:03}{ext}"
        )

        try:

            r = session.get(url, timeout=60)

            r.raise_for_status()

            with open(filename, "wb") as f:
                f.write(r.content)

            print(f"{i:03} OK")

        except Exception as e:

            print(i, e)

    browser.close()

print("\nFinished.")