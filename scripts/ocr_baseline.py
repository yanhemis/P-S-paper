"""
실험 A - 전체 페이지 Korean OCR baseline

사용법:
    python ocr_baseline.py <image_path> [<image_path> ...]

각 이미지에 대해 PaddleOCR(lang='korean')을 실행하고
- results/<image_stem>_ocr.json  : text bbox / text / confidence / runtime
- results/<image_stem>_vis.png   : bbox 시각화
를 저장한다.
"""

import sys
import json
import time
from pathlib import Path

import cv2
from paddleocr import PaddleOCR

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

_ocr = None


def get_ocr():
    global _ocr
    if _ocr is None:
        _ocr = PaddleOCR(
            lang="korean",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            # 서버급 검출 모델(PP-OCRv5_server_det)은 원본 해상도(예: 4000x3000
            # 스마트폰 촬영본)에서 peak memory 50GB+ 까지 치솟아 16GB RAM 환경에서
            # OOM(exit 137)으로 죽는 것을 확인함. mobile 검출 모델 + 입력 변 길이
            # 제한으로 메모리를 억제한다.
            # detection/recognition 모델명을 명시하면 `lang` 파라미터가 완전히
            # 무시되므로(경고 발생), 한국어 인식 모델도 함께 명시해야 한다.
            # (lang="korean" 단독으로는 무거운 PP-OCRv5_server_det가 선택되어
            # OOM이 났었음 — 위 주석 참고)
            text_detection_model_name="PP-OCRv5_mobile_det",
            text_recognition_model_name="korean_PP-OCRv5_mobile_rec",
            text_det_limit_side_len=1536,
            text_det_limit_type="max",
        )
    return _ocr


def run_full_page_ocr(image_path: Path) -> dict:
    ocr = get_ocr()

    start = time.perf_counter()
    result = ocr.predict(str(image_path))
    runtime = time.perf_counter() - start

    page = result[0]
    texts = page["rec_texts"]
    scores = page["rec_scores"]
    polys = page["rec_polys"]

    items = []
    for text, score, poly in zip(texts, scores, polys):
        xs = [int(p[0]) for p in poly]
        ys = [int(p[1]) for p in poly]
        bbox = [min(xs), min(ys), max(xs), max(ys)]
        items.append(
            {
                "text": text,
                "confidence": float(score),
                "bbox": bbox,
            }
        )

    return {
        "image_id": image_path.name,
        "runtime_sec": runtime,
        "num_text_boxes": len(items),
        "items": items,
    }


def visualize(image_path: Path, ocr_result: dict, out_path: Path):
    img = cv2.imread(str(image_path))
    for item in ocr_result["items"]:
        x1, y1, x2, y2 = item["bbox"]
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 140, 255), 2)
    cv2.imwrite(str(out_path), img)


def main():
    if len(sys.argv) < 2:
        print("usage: python ocr_baseline.py <image_path> [<image_path> ...]")
        sys.exit(1)

    for arg in sys.argv[1:]:
        image_path = Path(arg).resolve()
        if not image_path.exists():
            print(f"[skip] not found: {image_path}")
            continue

        print(f"[run] {image_path.name}")
        ocr_result = run_full_page_ocr(image_path)

        json_path = RESULTS_DIR / f"{image_path.stem}_ocr.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(ocr_result, f, ensure_ascii=False, indent=2)

        vis_path = RESULTS_DIR / f"{image_path.stem}_vis.png"
        visualize(image_path, ocr_result, vis_path)

        print(
            f"  -> {ocr_result['num_text_boxes']} boxes, "
            f"{ocr_result['runtime_sec']:.2f}s, "
            f"saved {json_path.name}, {vis_path.name}"
        )


if __name__ == "__main__":
    main()
