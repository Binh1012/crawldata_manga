import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://mangaspyfamily.com/spy-x-family-chapter-{}"

START_CHAPTER = 1
END_CHAPTER = 20

ROOT_DIR = "dataset"

headers = {
    "User-Agent": "Mozilla/5.0"
}


def crawl_chapter(chapter):

    url = BASE_URL.format(chapter)

    print("=" * 60)
    print("Chapter", chapter)
    print(url)

    try:
        html = requests.get(url, headers=headers, timeout=20)
    except Exception as e:
        print(e)
        return

    if html.status_code != 200:
        print("Skip")
        return

    soup = BeautifulSoup(html.text, "html.parser")

    content = soup.select_one("div.entry-content")

    if content is None:
        print("No content")
        return

    save_dir = os.path.join(
        ROOT_DIR,
        "Spy x Family",
        f"chapter_{chapter:03}"
    )

    image_dir = os.path.join(save_dir, "images")

    os.makedirs(image_dir, exist_ok=True)

    pages = []

    index = 1

    for img in content.select("img"):

        src = img.get("data-lazy-src") or img.get("src")

        if not src:
            continue

        src = urljoin(url, src)

        if "/wp-content/uploads/" not in src:
            continue

        ext = src.split(".")[-1].split("?")[0]

        filename = f"{index:03}.{ext}"

        filepath = os.path.join(image_dir, filename)

        if not os.path.exists(filepath):

            print("Download", filename)

            try:
                r = requests.get(src, headers=headers, timeout=30)

                with open(filepath, "wb") as f:
                    f.write(r.content)

            except Exception as e:
                print(e)
                continue

        pages.append({
            "page": index,
            "file": filename,
            "url": src
        })

        index += 1

    metadata = {
        "title": "Spy x Family",
        "chapter": chapter,
        "source": url,
        "total_pages": len(pages),
        "pages": pages
    }

    with open(
        os.path.join(save_dir, "chapter.json"),
        "w",
        encoding="utf8"
    ) as f:

        json.dump(metadata, f, indent=4, ensure_ascii=False)

    print("Done", chapter)


for chapter in range(START_CHAPTER, END_CHAPTER + 1):
    crawl_chapter(chapter)

print("Finished")