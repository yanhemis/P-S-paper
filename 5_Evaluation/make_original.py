import json
import cv2
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent
IMAGE = BASE.parent / "sample.jpg"

from PIL import Image, ImageOps

if not IMAGE.exists():
    raise FileNotFoundError(IMAGE)

pil_img = Image.open(IMAGE)
pil_img = ImageOps.exif_transpose(pil_img).convert("RGB")
img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

h, w = img.shape[:2]
print(f"원본 이미지: {w} x {h}")

def convert_file(input_name, output_name):
    with open(BASE / input_name, encoding="utf-8") as f:
        data = json.load(f)

    if data.get("source_image") != "sample.jpg":
        raise ValueError("원본 이미지 정보 확인 필요")

    angle = float(data["rotation_deg"])
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    M_inv = cv2.invertAffineTransform(M)

    converted = []

    for cell in data["cells"]:
        x1, y1, x2, y2 = cell["bbox"]

        corners = np.array([
            [x1, y1],
            [x2, y1],
            [x2, y2],
            [x1, y2]
        ], dtype=float)

        original = cv2.transform(
            corners.reshape(1, 4, 2), M_inv
        )[0]

        xs = original[:, 0]
        ys = original[:, 1]

        new_bbox = [
            max(0, int(np.floor(xs.min()))),
            max(0, int(np.floor(ys.min()))),
            min(w, int(np.ceil(xs.max()))),
            min(h, int(np.ceil(ys.max())))
        ]

        if new_bbox[0] >= new_bbox[2] or new_bbox[1] >= new_bbox[3]:
            raise ValueError(f"변환 bbox 확인 필요: {cell['id']}")

        new_cell = cell.copy()
        new_cell["bbox"] = new_bbox
        converted.append(new_cell)

    result = data.copy()
    result["image"] = "sample.jpg"
    result["cells"] = converted
    result["coordinate_system"] = "original_candidate"
    result["transform_note"] = (
        "Inverse rotation; overlay validation pending"
    )

    with open(BASE / output_name, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"생성: {output_name} ({len(converted)}개 셀)")

convert_file("cells.json", "cells_original.json")
convert_file("cells_primitive.json", "cells_primitive_original.json")
