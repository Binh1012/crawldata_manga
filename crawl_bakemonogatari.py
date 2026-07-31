import os
import re
import json
import time
from playwright.sync_api import sync_playwright

# ============================================
# CONFIG
# ============================================

MANGA_NAME = "Bakemonogatari"

# Dán URL chương muốn crawl vào đây, đổi mỗi lần chạy
CHAPTER_URL = "https://comix.to/title/0y7jv-bakemonogatari/2051162-chapter-193"

ROOT_DIR = "dataset"

HEADERS_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

# BẮT BUỘC False lần đầu để bạn tự bấm "Verify you are human".
# Cookie sau khi verify sẽ được lưu vào USER_DATA_DIR, các lần chạy
# sau thường không bị hỏi lại nữa (trừ khi cookie hết hạn).
HEADLESS = False

# Thư mục lưu profile trình duyệt (cookie, local storage...) để
# giữ lại trạng thái đã verify Cloudflare giữa các lần chạy.
USER_DATA_DIR = "playwright_profile"


# ============================================
# LẤY SỐ CHƯƠNG TỪ URL
# ============================================

def get_chapter_number(url):

    match = re.search(r"chapter-(\d+)", url)

    if match:
        return match.group(1)

    return "unknown"


# ============================================
# LẤY DANH SÁCH ẢNH TRONG CHƯƠNG
# ============================================

def get_images(page):

    # Cuộn dần xuống để kích hoạt lazy-load toàn bộ ảnh
    prev_count = -1

    for _ in range(30):

        count = page.locator("img.rpage-page__img").count()

        if count == prev_count:
            break

        prev_count = count

        page.mouse.wheel(0, 3000)
        page.wait_for_timeout(400)

    srcs = page.eval_on_selector_all(
        "img.rpage-page__img",
        "els => els.map(e => e.getAttribute('src'))"
    )

    return [s for s in srcs if s and s.startswith("http")]


# ============================================
# DOWNLOAD CHƯƠNG
# ============================================

def crawl_chapter(page, url):

    chapter = get_chapter_number(url)

    print("=" * 70)
    print(f"Chapter {chapter}: {url}")

    page.goto(url, wait_until="domcontentloaded", timeout=60000)

    # Kiểm tra xem có đang bị Cloudflare chặn (verify human) không
    try:
        page.wait_for_selector("img.rpage-page__img", timeout=8000)

    except Exception:

        print(">>> Có vẻ đang bị Cloudflare chặn (verify human).")
        print(">>> Hãy chuyển qua cửa sổ trình duyệt vừa mở, tự bấm xác minh.")
        print(">>> Script sẽ tự chờ tối đa 2 phút cho tới khi ảnh xuất hiện...")

        try:
            page.wait_for_selector("img.rpage-page__img", timeout=120000)
        except Exception as e:
            print("Vẫn không qua được sau 2 phút:", e)
            return

    image_urls = get_images(page)

    print(f"Tìm thấy {len(image_urls)} ảnh")

    if len(image_urls) == 0:
        print("Không tìm thấy ảnh nào, dừng lại.")
        return

    chapter_dir = os.path.join(ROOT_DIR, MANGA_NAME, f"chapter_{chapter}")
    image_dir = os.path.join(chapter_dir, "images")
    os.makedirs(image_dir, exist_ok=True)

    pages = []

    # Dùng request context của chính trình duyệt (giữ nguyên cookie/session
    # đã qua Cloudflare) để tải ảnh, tránh bị chặn như dùng requests thường.
    request_ctx = page.context.request

    for i, image_url in enumerate(image_urls, start=1):

        clean_url = image_url.split("?")[0]
        ext = clean_url.split(".")[-1]

        if len(ext) > 5:
            ext = "jpg"

        filename = f"{i:03}.{ext}"
        filepath = os.path.join(image_dir, filename)

        if os.path.exists(filepath):
            print(filename, "đã tồn tại")

        else:
            print("Download", filename)

            try:
                resp = request_ctx.get(image_url, timeout=60000)

                if resp.ok:
                    with open(filepath, "wb") as f:
                        f.write(resp.body())
                else:
                    print("Lỗi", resp.status)
                    continue

            except Exception as e:
                print(e)
                continue

        pages.append({"page": i, "file": filename, "url": image_url})

    metadata = {
        "manga": MANGA_NAME,
        "chapter": chapter,
        "source": url,
        "total_pages": len(pages),
        "pages": pages
    }

    with open(os.path.join(chapter_dir, "chapter.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    print(f"✓ Chapter {chapter} hoàn thành")


# ============================================
# MAIN
# ============================================

def main():

    with sync_playwright() as p:

        # launch_persistent_context lưu cookie/localStorage vào USER_DATA_DIR
        # -> sau khi verify Cloudflare 1 lần, các lần chạy sau đỡ bị hỏi lại.
        context = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=HEADLESS,
            user_agent=HEADERS_UA,
            viewport={"width": 1280, "height": 900},
        )

        page = context.new_page()

        crawl_chapter(page, CHAPTER_URL)

        context.close()

    print("\nHoàn thành.")


if __name__ == "__main__":
    main()