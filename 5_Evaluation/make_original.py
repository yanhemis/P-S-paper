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


    # 과거 OpenCV 실행 보고서에서 실제 Affine Matrix 불러오기
    with open(BASE / "opencv_historical_report.json", encoding="utf-8") as f:
        report = json.load(f)

    # Prediction과 실행 보고서의 정보 일치 여부 확인
    if report["source_image"] != data["source_image"]:
        raise ValueError("원본 이미지 불일치")

    if report["image"] != data["image"]:
        raise ValueError("정렬 이미지 불일치")

    if tuple(report["source_size"]) != (w, h):
        raise ValueError("원본 이미지 크기 불일치")

    if abs(float(report["rotation_deg"]) - float(data["rotation_deg"])) > 0.001:
        raise ValueError("회전각 불일치")

    # 확장 캔버스의 이동 보정이 포함된 회전 행렬
    M = np.asarray(report["deskew"]["affine"], dtype=np.float64)

    if M.shape != (2, 3):
        raise ValueError("Affine Matrix 형식 오류")

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
