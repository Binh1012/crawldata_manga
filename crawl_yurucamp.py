import os
import re
import json
import requests
from PIL import Image
from io import BytesIO

# ============================================
# CONFIG
# ============================================

START_CHAPTER = 1
END_CHAPTER = 18

BASE_URL = "https://dynasty-scans.com/chapters/yurucamp_ch{:02d}"

ROOT_DIR = "dataset"

MANGA_NAME = "Yurucamp"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    )
}

# ============================================
# LẤY DANH SÁCH ẢNH
# ============================================

def get_images(html):

    match = re.search(
        r"var\s+pages\s*=\s*(\[[\s\S]*?\]);",
        html
    )

    if not match:
        return []

    try:
        pages = json.loads(match.group(1))
    except Exception:
        return []

    images = []

    for page in pages:

        image = page.get("image")

        if not image:
            continue

        if image.startswith("/"):
            image = "https://dynasty-scans.com" + image

        images.append({
            "url": image,
            "name": page.get("name", ""),
            "width": page.get("width"),
            "height": page.get("height")
        })

    return images


# ============================================
# DOWNLOAD 1 CHAPTER
# ============================================

def crawl_chapter(chapter):

    url = BASE_URL.format(chapter)

    print("=" * 70)
    print(url)

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

    except Exception as e:

        print(e)
        return

    print("Status:", response.status_code)

    if response.status_code != 200:

        print("Không truy cập được chapter.")
        return

    image_list = get_images(response.text)

    print(f"Tìm thấy {len(image_list)} ảnh")

    if len(image_list) == 0:
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

    for index, item in enumerate(image_list, start=1):

        image_url = item["url"]

        filename = f"{index:03}.jpg"

        filepath = os.path.join(
            image_dir,
            filename
        )

        if os.path.exists(filepath):

            print(filename, "đã tồn tại")

        else:

            print("Download", filename)

            try:

                img_response = requests.get(
                    image_url,
                    headers=HEADERS,
                    timeout=60
                )

                if img_response.status_code != 200:

                    print("Lỗi", img_response.status_code)
                    continue

                image = Image.open(
                    BytesIO(img_response.content)
                )

                # JPG không hỗ trợ alpha
                if image.mode != "RGB":
                    image = image.convert("RGB")

                image.save(
                    filepath,
                    "JPEG",
                    quality=95,
                    optimize=True
                )

            except Exception as e:

                print("Lỗi:", e)
                continue

        pages.append({

            "page": index,
            "file": filename,
            "original_name": item["name"],
            "width": item["width"],
            "height": item["height"],
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