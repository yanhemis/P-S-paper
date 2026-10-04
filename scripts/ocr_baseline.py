"""
실험 A - 전체 페이지 Korean OCR baseline

사용법:
    python ocr_baseline.py <image_path> [<image_path> ...] [--out-dir DIR] [--no-vis]

각 이미지에 대해 PaddleOCR(lang='korean')을 실행하고
- results/<image_stem>_ocr.json  : text bbox / text / confidence / runtime
- results/<image_stem>_vis.png   : bbox 시각화
를 저장한다. --out-dir 을 주면 results/ 대신 그 폴더에 저장한다 (전처리 비교 실험용).
"""

import sys
import json
import time
import platform
import resource
from pathlib import Path

import cv2
import paddle
import paddleocr
from paddleocr import PaddleOCR

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

_ocr = None

# 실험 A/B/C 공통 OCR 설정 (결과 json의 meta에도 그대로 기록)
DET_MODEL = "PP-OCRv5_mobile_det"
REC_MODEL = "korean_PP-OCRv5_mobile_rec"
DET_LIMIT_SIDE_LEN = 1536
DET_LIMIT_TYPE = "max"


def peak_rss_mb():
    """현재 프로세스의 최대 메모리 사용량(MB). 모델 로딩 포함, 프로세스 시작 이후 누적 최대값."""
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(rss / (1024 * 1024 if sys.platform == "darwin" else 1024), 1)  # macOS는 byte, Linux는 KB


def run_meta():
    """공통 문서 11절: 사용 모델/버전, 실행 환경을 결과에 남긴다."""
    return {
        "det_model": DET_MODEL,
        "rec_model": REC_MODEL,
        "text_det_limit_side_len": DET_LIMIT_SIDE_LEN,
        "text_det_limit_type": DET_LIMIT_TYPE,
        "paddleocr": paddleocr.__version__,
        "paddlepaddle": paddle.__version__,
        "opencv": cv2.__version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "device": "GPU" if paddle.device.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0 else "CPU",
        "process_peak_rss_mb": peak_rss_mb(),
    }


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
            text_detection_model_name=DET_MODEL,
            text_recognition_model_name=REC_MODEL,
            text_det_limit_side_len=DET_LIMIT_SIDE_LEN,
            text_det_limit_type=DET_LIMIT_TYPE,
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
                # 기울어진 촬영본에서 글자 위치를 추정하려면 4점 polygon이 필요함
                "poly": [[int(p[0]), int(p[1])] for p in poly],
            }
        )

    return {
        "image_id": image_path.name,
        "runtime_sec": runtime,
        "num_text_boxes": len(items),
        "meta": run_meta(),
        "items": items,
    }


def visualize(image_path: Path, ocr_result: dict, out_path: Path):
    img = cv2.imread(str(image_path))
    for item in ocr_result["items"]:
        x1, y1, x2, y2 = item["bbox"]
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 140, 255), 2)
    cv2.imwrite(str(out_path), img)


def main():
    args = sys.argv[1:]
    out_dir = RESULTS_DIR
    if "--out-dir" in args:
        i = args.index("--out-dir")
        out_dir = Path(args[i + 1]).resolve()
        del args[i:i + 2]
    save_vis = "--no-vis" not in args
    args = [a for a in args if a != "--no-vis"]
    if not args:
        print("usage: python ocr_baseline.py <image_path> [<image_path> ...] [--out-dir DIR] [--no-vis]")
        sys.exit(1)
    out_dir.mkdir(parents=True, exist_ok=True)

    for arg in args:
        image_path = Path(arg).resolve()
        if not image_path.exists():
            print(f"[skip] not found: {image_path}")
            continue

        print(f"[run] {image_path.name}")
        ocr_result = run_full_page_ocr(image_path)

        json_path = out_dir / f"{image_path.stem}_ocr.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(ocr_result, f, ensure_ascii=False, indent=2)

        saved = [json_path.name]
        if save_vis:
            vis_path = out_dir / f"{image_path.stem}_vis.png"
            visualize(image_path, ocr_result, vis_path)
            saved.append(vis_path.name)

        print(
            f"  -> {ocr_result['num_text_boxes']} boxes, "
            f"{ocr_result['runtime_sec']:.2f}s, "
            f"saved {', '.join(saved)}"
        )


if __name__ == "__main__":
    main()
