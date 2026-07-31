import os
import json
import time
import mimetypes
import requests
from bs4 import BeautifulSoup

# ============================================
# CONFIG
# ============================================

START_CHAPTER = 1160
END_CHAPTER = 1170

BASE_URL = "https://w76.onepiece-manga-online.net/manga/one-piece-chapter-{}/"

ROOT_DIR = "dataset"

MANGA_NAME = "One Piece"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://w76.onepiece-manga-online.net/",
    "Origin": "https://w76.onepiece-manga-online.net",
    "Connection": "keep-alive",
}

session = requests.Session()
session.headers.update(HEADERS)

# ============================================
# GET IMAGE URLS
# ============================================

def get_images(soup):

    images = []

    for img in soup.select("div.manga-images img.manga-image"):

        src = (
            img.get("src")
            or img.get("data-src")
            or img.get("data-lazy-src")
            or img.get("data-original")
        )

        if not src:
            continue

        if src.startswith("//"):
            src = "https:" + src

        if src.startswith("http"):
            images.append(src)

    return images


# ============================================
# DOWNLOAD IMAGE
# ============================================

def download_image(url, filepath):

    for attempt in range(3):

        try:

            r = session.get(
                url,
                timeout=60,
                stream=True,
                allow_redirects=True
            )

            if r.status_code == 200:

                with open(filepath, "wb") as f:

                    for chunk in r.iter_content(8192):
                        if chunk:
                            f.write(chunk)

                return True

            print(f"Status {r.status_code}")

        except Exception as e:

            print(e)

        time.sleep(2)

    return False


# ============================================
# CRAWL CHAPTER
# ============================================

def crawl_chapter(chapter):

    url = BASE_URL.format(chapter)

    print("=" * 70)
    print(url)

    try:

        response = session.get(url, timeout=30)

    except Exception as e:

        print(e)
        return

    if response.status_code != 200:

        print("Không truy cập được chapter.")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    image_urls = get_images(soup)

    print(f"Tìm thấy {len(image_urls)} ảnh")

    if not image_urls:

        return

    chapter_dir = os.path.join(
        ROOT_DIR,
        MANGA_NAME,
        f"chapter_{chapter}"
    )

    image_dir = os.path.join(
        chapter_dir,
        "images"
    )

    os.makedirs(image_dir, exist_ok=True)

    pages = []

    for page, image_url in enumerate(image_urls, start=1):

        ext = image_url.split(".")[-1].split("?")[0]

        if len(ext) > 5:

            ext = "jpg"

        filename = f"{page:03}.{ext}"

        filepath = os.path.join(image_dir, filename)

        if os.path.exists(filepath):

            print(filename, "đã tồn tại")

        else:

            print("Download", filename)

            ok = download_image(image_url, filepath)

            if not ok:

                print("Không tải được:", image_url)
                continue

        pages.append({

            "page": page,
            "file": filename,
            "url": image_url

        })

    metadata = {

        "manga": MANGA_NAME,
        "chapter": chapter,
        "source": url,
        "total_pages": len(pages),
        "pages": pages

    }

    with open(

        os.path.join(chapter_dir, "chapter.json"),
        "w",
        encoding="utf-8"

    ) as f:

        json.dump(
            metadata,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(f"✓ Chapter {chapter} hoàn thành")


# ============================================
# MAIN
# ============================================

for chapter in range(
    START_CHAPTER,
    END_CHAPTER + 1
):

    crawl_chapter(chapter)

print("\nHoàn thành.")