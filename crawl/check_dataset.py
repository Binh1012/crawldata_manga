import os
import json

ROOT_DIR = "dataset"


def check_dataset():

    total_manga = 0
    total_chapter = 0
    total_images = 0

    errors = []

    if not os.path.exists(ROOT_DIR):
        print("Không tìm thấy thư mục dataset.")
        return

    for manga in sorted(os.listdir(ROOT_DIR)):

        manga_path = os.path.join(ROOT_DIR, manga)

        if not os.path.isdir(manga_path):
            continue

        total_manga += 1

        print("=" * 70)
        print("Manga:", manga)

        for chapter in sorted(os.listdir(manga_path)):

            chapter_path = os.path.join(manga_path, chapter)

            if not os.path.isdir(chapter_path):
                continue

            total_chapter += 1

            json_path = os.path.join(chapter_path, "chapter.json")
            image_dir = os.path.join(chapter_path, "images")

            if not os.path.exists(json_path):
                errors.append(f"{chapter}: thiếu chapter.json")
                continue

            if not os.path.exists(image_dir):
                errors.append(f"{chapter}: thiếu thư mục images")
                continue

            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

            except Exception as e:
                errors.append(f"{chapter}: lỗi JSON ({e})")
                continue

            pages = data.get("pages", [])

            image_files = [
                f for f in os.listdir(image_dir)
                if os.path.isfile(os.path.join(image_dir, f))
            ]

            total_images += len(image_files)

            if len(image_files) != len(pages):

                errors.append(
                    f"{chapter}: json={len(pages)} ảnh, folder={len(image_files)} ảnh"
                )

            if data.get("total_pages") != len(pages):

                errors.append(
                    f"{chapter}: total_pages={data.get('total_pages')} nhưng pages={len(pages)}"
                )

            for page in pages:

                filename = page["file"]

                filepath = os.path.join(image_dir, filename)

                if not os.path.exists(filepath):

                    errors.append(
                        f"{chapter}: thiếu {filename}"
                    )

                    continue

                if os.path.getsize(filepath) == 0:

                    errors.append(
                        f"{chapter}: {filename} có kích thước 0 byte"
                    )

    print("\n")
    print("=" * 70)
    print("TỔNG KẾT")
    print("=" * 70)

    print(f"Manga   : {total_manga}")
    print(f"Chapter : {total_chapter}")
    print(f"Images  : {total_images}")

    print()

    if len(errors) == 0:

        print("✓ Dataset hợp lệ.")

    else:

        print(f"Phát hiện {len(errors)} lỗi:\n")

        for err in errors:
            print("-", err)


if __name__ == "__main__":
    check_dataset()