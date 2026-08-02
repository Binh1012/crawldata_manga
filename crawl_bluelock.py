import os
import json
import requests

from bs4 import BeautifulSoup
from urllib.parse import urlparse

START_CHAPTER = 344
END_CHAPTER = 354

BASE_URL = "https://the-blue-lock.com/manga/blue-lock-chapter-{}/"

ROOT_DIR = "dataset"

MANGA_NAME = "Blue Lock"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://the-blue-lock.com/"
}

# ============================================
# LẤY DANH SÁCH ẢNH
# ============================================

def get_images(soup):

    images = []

    # Gallery của Kadence
    for img in soup.select("ul.kb-gallery-ul img"):

        src = (
            img.get("data-full-image")
            or img.get("src")
            or img.get("data-light-image")
            or img.get("data-src")
            or img.get("data-lazy-src")
            or img.get("data-original")
        )

        if not src:
            continue

        if src.startswith("//"):
            src = "https:" + src

        if not src.startswith("http"):
            continue

        # Chỉ lấy ảnh truyện
        if "img.the-blue-lock.com/uploads/" not in src:
            continue

        if src not in images:
            images.append(src)

    return images

# ============================================
# DOWNLOAD CHAPTER
# ============================================

def crawl_chapter(chapter):

    url = BASE_URL.format(chapter)

    print("=" * 70)
    print(url)

    try:

        r = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

    except Exception as e:

        print(e)
        return

    if r.status_code != 200:

        print("Không truy cập được chapter.")
        return

    soup = BeautifulSoup(r.text, "html.parser")

    image_urls = get_images(soup)

    print(f"Tìm thấy {len(image_urls)} ảnh")

    if len(image_urls) == 0:

        with open(
            "debug.html",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(r.text)

        print("Không tìm thấy ảnh.")
        print("Đã lưu debug.html")
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

    os.makedirs(
        image_dir,
        exist_ok=True
    )

    pages = []

    for i, image_url in enumerate(image_urls, start=1):

        path = urlparse(image_url).path

        ext = os.path.splitext(path)[1].lower()

        if ext:
            ext = ext[1:]
        else:
            ext = "jpg"

        filename = f"{i:03}.{ext}"

        filepath = os.path.join(
            image_dir,
            filename
        )

        if os.path.exists(filepath):

            print(filename, "đã tồn tại")

        else:

            print("Download", filename)

            try:

                img = requests.get(
                    image_url,
                    headers=HEADERS,
                    timeout=60
                )

                if img.status_code == 200:

                    with open(filepath, "wb") as f:
                        f.write(img.content)

                else:

                    print("Lỗi", img.status_code)
                    continue

            except Exception as e:

                print(e)
                continue

        pages.append({

            "page": i,
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

        os.path.join(
            chapter_dir,
            "chapter.json"
        ),

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