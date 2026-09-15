import os

os.environ["FLAGS_enable_pir_api"] = "0"

import json
from paddleocr import PaddleOCR


IMAGE_PATH = "sample.jpg"
OUTPUT_PATH = "full_ocr_result.json"


# 전체 페이지 OCR
ocr = PaddleOCR(
    lang="korean",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    enable_mkldnn=False,
)

result = ocr.predict(IMAGE_PATH)

ocr_items = []

for page in result:
    data = page.json

    # PaddleOCR 3.x Result 객체의 JSON 구조 대응
    if isinstance(data, str):
        data = json.loads(data)

    res = data.get("res", data)

    texts = res.get("rec_texts", [])
    scores = res.get("rec_scores", [])
    boxes = res.get("rec_boxes", [])

    for text, score, box in zip(texts, scores, boxes):
        box = [int(v) for v in box]

        ocr_items.append({
            "text": text,
            "score": float(score),
            "bbox": box
        })


with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(
        ocr_items,
        f,
        ensure_ascii=False,
        indent=2
    )


print(f"OCR 개수: {len(ocr_items)}")
print(f"저장 완료: {OUTPUT_PATH}")

print("\n--- OCR 일부 확인 ---")
for item in ocr_items[:20]:
    print(item)