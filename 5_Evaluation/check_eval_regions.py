
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

BASE = Path(__file__).resolve().parent

img = ImageOps.exif_transpose(
    Image.open(BASE.parent / "sample.jpg")
).convert("RGB")

draw = ImageDraw.Draw(img)

regions = {
    "Upper Table": [261, 576, 2692, 1427],
    "Lower Table": [256, 2980, 2789, 3776]
}

for name, box in regions.items():
    draw.rectangle(box, outline="red", width=12)
    draw.text((box[0], box[1] - 35), name, fill="red")

img.thumbnail((900, 1200))
img.save(BASE / "evaluation_regions_check.jpg")

print("평가 영역 확인 이미지 생성 완료")
