from ultralytics import YOLO
from pathlib import Path
import cv2

# ==========================================
# CONFIG
# ==========================================

MODEL_PATH = "models/best.pt"

IMAGE_DIR = Path("new_images/images")

OUTPUT_DIR = Path("output")

CONF = 0.25

IMG_SIZE = 1024

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

# ==========================================

OUTPUT_DIR.mkdir(exist_ok=True)

model = YOLO(MODEL_PATH)

images = []

for img in sorted(IMAGE_DIR.iterdir()):

    if img.suffix.lower() in IMAGE_EXTS:
        images.append(img)

print(f"Found {len(images)} images.\n")

# ==========================================

for image_path in images:

    print("=" * 60)
    print(image_path.name)

    results = model.predict(
        source=str(image_path),
        imgsz=IMG_SIZE,
        conf=CONF,
        verbose=False
    )

    result = results[0]

    image = cv2.imread(str(image_path))

    boxes = result.boxes.xyxy.cpu().numpy()

    print(f"Detected: {len(boxes)} text regions")

    for box in boxes:

        x1, y1, x2, y2 = map(int, box)

        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

    save_path = OUTPUT_DIR / image_path.name

    cv2.imwrite(str(save_path), image)

print("\nDone.")