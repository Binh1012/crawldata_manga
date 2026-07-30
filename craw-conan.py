import os
import json
import requests
from bs4 import BeautifulSoup

# ============================================
# CONFIG
# ============================================

START_CHAPTER = 691
END_CHAPTER = 700

BASE_URL = "https://readdetectiveconan.website/manga/case-closed-chapter-{}/"

ROOT_DIR = "dataset"

MANGA_NAME = "Conan"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://readdetectiveconan.website/"
}

# ============================================
# LẤY DANH SÁCH ẢNH
# ============================================

def get_images(soup):

    images = []

    for img in soup.select("div.entry-content img"):

        src = img.get("src")

        if not src:
            continue

        if not src.startswith("http"):
            continue

        images.append(src)

    return images


# ============================================
# DOWNLOAD MỘT CHAPTER
# ============================================

def crawl_chapter(chapter):

    url = BASE_URL.format(chapter)

    print("=" * 70)
    print(url)

    try:
        r = requests.get(url, headers=HEADERS, timeout=30)

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

    for i, image_url in enumerate(image_urls, start=1):

        ext = image_url.split(".")[-1].split("?")[0]

        if len(ext) > 5:
            ext = "jpg"

        filename = f"{i:03}.{ext}"

        filepath = os.path.join(image_dir, filename)

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