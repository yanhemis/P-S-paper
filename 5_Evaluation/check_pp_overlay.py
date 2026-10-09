
import json
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

BASE = Path(__file__).resolve().parent

# GT 기준 원본 이미지
img = ImageOps.exif_transpose(
    Image.open(BASE.parent / "sample.jpg")
).convert("RGB")

# 공통 Exhaustive GT
with open(BASE / "sample.jpg_gt.json", encoding="utf-8") as f:
    gt = json.load(f)

# PP-Structure Prediction
pp_path = (
    BASE.parent
    / "1_PaddleOCR-PP-Structure"
    / "output"
    / "sample"
    / "res_0.txt"
)

with open(pp_path, encoding="utf-8") as f:
    data = json.load(f)

pred = data["res"]["cell_bbox"]

gt_img = img.copy()
pred_img = img.copy()

draw_gt = ImageDraw.Draw(gt_img)
draw_pred = ImageDraw.Draw(pred_img)

for cell in gt:
    draw_gt.rectangle(
        cell["bbox"], outline="lime", width=8
    )

for box in pred:
    draw_pred.rectangle(
        [int(round(v)) for v in box],
        outline="red",
        width=8
    )

w, h = img.size
result = Image.new("RGB", (w * 2, h), "white")
result.paste(gt_img, (0, 0))
result.paste(pred_img, (w, 0))

result.thumbnail((1800, 1600))

output = BASE / "pp_overlay_check.jpg"
result.save(output, quality=95)

out_of_bounds = sum(
    not (0 <= b[0] < b[2] <= w and
         0 <= b[1] < b[3] <= h)
    for b in pred
)

print("GT:", len(gt))
print("PP-Structure Prediction:", len(pred))
print("이미지 범위 밖 Prediction:", out_of_bounds)
print("저장 완료:", output.name)
