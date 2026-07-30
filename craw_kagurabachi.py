import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# =====================================
# CẤU HÌNH
# =====================================

MANGA_NAME = "kagurabachi"

BASE_URL = f"https://readkagura.com/manga/kagurabachi-chapter-{{}}/"

START_CHAPTER = 3
END_CHAPTER = 13

ROOT_DIR = "dataset"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36"
    )
}


# =====================================
# LẤY DANH SÁCH ẢNH
# =====================================

def get_images(soup):

    selectors = [
        "div.reading-content div.page-break img",
        "div.reading-content img",
        "figure.wp-block-image img",
        "div.entry-content img"
    ]

    for selector in selectors:

        imgs = soup.select(selector)

        if imgs:

            print(f"✓ Selector: {selector}")
            print(f"✓ Tìm thấy {len(imgs)} ảnh")

            return imgs

    return []


# =====================================
# DOWNLOAD 1 CHAPTER
# =====================================

def crawl_chapter(chapter):

    url = BASE_URL.format(chapter)

    print("\n" + "=" * 70)
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

        print("Không truy cập được.")
        return

    soup = BeautifulSoup(r.text, "html.parser")

    images = get_images(soup)

    if len(images) == 0:

        print("Không tìm thấy ảnh.")
        return

    save_dir = os.path.join(
        ROOT_DIR,
        MANGA_NAME,
        f"chapter_{chapter:03}"
    )

    image_dir = os.path.join(
        save_dir,
        "images"
    )

    os.makedirs(image_dir, exist_ok=True)

    pages = []

    page = 1

    for img in images:

        image_url = (
            img.get("data-lazy-src")
            or img.get("data-src")
            or img.get("src")
        )

        if not image_url:
            continue

        image_url = urljoin(url, image_url)

        ext = image_url.split(".")[-1].split("?")[0]

        if len(ext) > 5:
            ext = "jpg"

        filename = f"{page:03}.{ext}"

        filepath = os.path.join(
            image_dir,
            filename
        )

        if os.path.exists(filepath):

            print(filename, "đã tồn tại")

        else:

            print("Download", filename)

            try:

                img_data = requests.get(
                    image_url,
                    headers=HEADERS,
                    timeout=60
                )

                if img_data.status_code == 200:

                    with open(filepath, "wb") as f:

                        f.write(img_data.content)

                else:

                    print("Lỗi tải:", image_url)
                    continue

            except Exception as e:

                print(e)
                continue

        pages.append({

            "page": page,
            "file": filename,
            "url": image_url

        })

        page += 1

    metadata = {

        "manga": MANGA_NAME,
        "chapter": chapter,
        "source": url,
        "total_pages": len(pages),
        "pages": pages

    }

    with open(

        os.path.join(save_dir, "chapter.json"),

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(
            metadata,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(f"✓ Hoàn thành Chapter {chapter}")
    print(f"✓ {len(pages)} trang")


# =====================================
# MAIN
# =====================================

for chap in range(
    START_CHAPTER,
    END_CHAPTER + 1
):

    crawl_chapter(chap)

print("\nHoàn thành.")