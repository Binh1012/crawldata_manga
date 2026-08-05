import random
import shutil
from pathlib import Path

# =====================================================
# CONFIG
# =====================================================

EXPORT_DIR = Path("annotations")

IMAGES_DIR = EXPORT_DIR / "images"
LABELS_DIR = EXPORT_DIR / "labels"

OUTPUT_DIR = Path("dataset")

TRAIN_RATIO = 0.8
RANDOM_SEED = 42

IMAGE_EXTS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

CLASS_NAMES = [
    "text"
]

# =====================================================
# CHECK INPUT
# =====================================================

if not IMAGES_DIR.exists():
    raise FileNotFoundError(f"Image folder not found:\n{IMAGES_DIR}")

if not LABELS_DIR.exists():
    raise FileNotFoundError(f"Label folder not found:\n{LABELS_DIR}")

# =====================================================
# REMOVE OLD DATASET
# =====================================================

if OUTPUT_DIR.exists():
    print("Removing old dataset...")
    shutil.rmtree(OUTPUT_DIR)

train_img = OUTPUT_DIR / "images" / "train"
val_img = OUTPUT_DIR / "images" / "val"

train_lbl = OUTPUT_DIR / "labels" / "train"
val_lbl = OUTPUT_DIR / "labels" / "val"

for folder in [
    train_img,
    val_img,
    train_lbl,
    val_lbl,
]:
    folder.mkdir(parents=True, exist_ok=True)

# =====================================================
# SCAN DATASET
# =====================================================

valid_samples = []

missing_label = 0
empty_label = 0

print("=" * 60)
print("Checking dataset...")
print("=" * 60)

for image_path in sorted(IMAGES_DIR.iterdir()):

    if image_path.suffix.lower() not in IMAGE_EXTS:
        continue

    label_path = LABELS_DIR / f"{image_path.stem}.txt"

    if not label_path.exists():
        print(f"[SKIP] Missing label : {image_path.name}")
        missing_label += 1
        continue

    if label_path.stat().st_size == 0:
        print(f"[SKIP] Empty label : {image_path.name}")
        empty_label += 1
        continue

    valid_samples.append((image_path, label_path))

print()
print(f"Valid samples : {len(valid_samples)}")
print(f"Missing label : {missing_label}")
print(f"Empty label   : {empty_label}")

# =====================================================
# RANDOM SPLIT
# =====================================================

random.seed(RANDOM_SEED)
random.shuffle(valid_samples)

split_index = int(len(valid_samples) * TRAIN_RATIO)

train_set = valid_samples[:split_index]
val_set = valid_samples[split_index:]

print()
print(f"Train samples : {len(train_set)}")
print(f"Val samples   : {len(val_set)}")

# =====================================================
# COPY DATASET
# =====================================================

print()
print("=" * 60)
print("Copying dataset...")
print("=" * 60)

for img, lbl in train_set:
    shutil.copy2(img, train_img / img.name)
    shutil.copy2(lbl, train_lbl / lbl.name)

for img, lbl in val_set:
    shutil.copy2(img, val_img / img.name)
    shutil.copy2(lbl, val_lbl / lbl.name)

# =====================================================
# CREATE data.yaml
# =====================================================

yaml_path = OUTPUT_DIR / "data.yaml"

with open(yaml_path, "w", encoding="utf-8") as f:

    f.write("path: .\n")
    f.write("train: images/train\n")
    f.write("val: images/val\n\n")

    f.write(f"nc: {len(CLASS_NAMES)}\n")

    f.write("names:\n")

    for i, name in enumerate(CLASS_NAMES):
        f.write(f"  {i}: {name}\n")

# =====================================================
# SUMMARY
# =====================================================

print()
print("=" * 60)
print("Dataset Summary")
print("=" * 60)

print(f"Train images : {len(train_set)}")
print(f"Validation   : {len(val_set)}")
print(f"Total        : {len(valid_samples)}")

print()
print("Dataset structure:")

print(OUTPUT_DIR)
print("├── data.yaml")
print("├── images")
print("│   ├── train")
print("│   └── val")
print("└── labels")
print("    ├── train")
print("    └── val")

print()
print("Done!")
print(f"YOLO dataset : {OUTPUT_DIR.resolve()}")
print(f"data.yaml    : {yaml_path.resolve()}")