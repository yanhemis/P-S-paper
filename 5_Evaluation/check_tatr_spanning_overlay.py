import json
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

BASE = Path(__file__).resolve().parent

raw = Image.open(BASE.parent / "sample.jpg")
orientation = raw.getexif().get(274)

if orientation != 6:
    raise ValueError("EXIF Orientation 확인 필요")

raw_w, raw_h = raw.size
img = ImageOps.exif_transpose(raw).convert("RGB")
w, h = img.size

with open(BASE / "sample.jpg_gt.json", encoding="utf-8") as f:
    gt = json.load(f)

with open(BASE.parent / "2_TATR" / "tatr_result_spanning.json",
          encoding="utf-8") as f:
    cells = json.load(f)["reconstructed_cells"]

# EXIF 6: 가로 이미지 -> 세로 이미지 (시계 방향 90도)
def convert_box(box):
    x1, y1, x2, y2 = box
    return [
        raw_h - y2,
        x1,
        raw_h - y1,
        x2
    ]

converted = [convert_box(c["bbox"]) for c in cells]

bad = sum(
    not (0 <= b[0] < b[2] <= w and
         0 <= b[1] < b[3] <= h)
    for b in converted
)

gt_img = img.copy()
pred_img = img.copy()

draw_gt = ImageDraw.Draw(gt_img)
draw_pred = ImageDraw.Draw(pred_img)

for cell in gt:
    draw_gt.rectangle(cell["bbox"], outline="lime", width=8)

for box in converted:
    draw_pred.rectangle(box, outline="red", width=8)

result = Image.new("RGB", (w * 2, h), "white")
result.paste(gt_img, (0, 0))
result.paste(pred_img, (w, 0))
result.thumbnail((1800, 1600))

output = BASE / "tatr_spanning_overlay_check.jpg"
result.save(output, quality=95)

print("GT:", len(gt))
print("TATR Grid:", len(converted))
print("변환 후 범위 밖:", bad)
print("저장 완료:", output.name)
