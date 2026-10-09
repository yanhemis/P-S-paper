import json
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

BASE = Path(__file__).resolve().parent

# EXIF 방향을 반영한 원본 이미지
img = ImageOps.exif_transpose(
    Image.open(BASE.parent / "sample.jpg")
).convert("RGB")

with open(BASE / "sample.jpg_gt.json", encoding="utf-8") as f:
    gt = json.load(f)

with open(BASE / "cells.json", encoding="utf-8") as f:
    pred = json.load(f)["cells"]

# 왼쪽: GT / 오른쪽: OpenCV 예측
gt_img = img.copy()
pred_img = img.copy()

draw_gt = ImageDraw.Draw(gt_img)
draw_pred = ImageDraw.Draw(pred_img)

for cell in gt:
    draw_gt.rectangle(cell["bbox"], outline="lime", width=8)

for cell in pred:
    draw_pred.rectangle(cell["bbox"], outline="red", width=8)

# 두 이미지를 나란히 배치
w, h = img.size
result = Image.new("RGB", (w * 2, h), "white")
result.paste(gt_img, (0, 0))
result.paste(pred_img, (w, 0))

result.thumbnail((1800, 1600))
result.save(BASE / "opencv_raw_overlay_check.jpg", quality=95)

print("GT:", len(gt))
print("OpenCV Prediction:", len(pred))
print("저장 완료: opencv_overlay_check.jpg")
