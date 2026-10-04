"""
실험 B / C - ROI OCR

사용법:
    python roi_ocr.py <roi_json> <out_dir> [<image_dir>] [--pad 0.25]

    # 실험 B (GT ROI)
    python roi_ocr.py gt/gt_roi.json results/roi_gt
    # 실험 C (검출 ROI) - bang_/heewon 결과를 같은 포맷으로 변환해서 넣는다
    python roi_ocr.py <detected_roi.json> results/roi_detected

--pad: ROI를 칸 높이 대비 위아래로 늘리는 비율 (기본 0.25). 이미 여유를 크게 잡은
       검출 ROI(예: taegu value_roi)는 0으로 주는 것이 맞다.

ROI json 포맷 (gt/gt_roi.json 과 동일):
    { "<image file name>": { "fields": { "<field>": { "quad": [[x,y] x4] } } } }
    quad 순서: 좌상, 우상, 우하, 좌하 (원본 이미지 좌표, EXIF 회전 적용 후)
    quad 대신 "bbox": [x1, y1, x2, y2] 만 있어도 된다.

각 ROI를 원근 보정해서 잘라낸 뒤 실험 A와 같은 PaddleOCR 설정(det + rec)으로 인식한다.
- <out_dir>/<image_stem>_roi_ocr.json : 필드별 text / confidence / runtime / items
- <out_dir>/crops/<image_stem>_<field>.jpg : 잘라낸 ROI (실패 사례 확인용)
"""

import sys
import json
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ocr_baseline import get_ocr, run_meta  # noqa: E402  실험 A와 동일한 모델/설정 사용

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_IMAGE_DIR = ROOT / "sample_data_jpg"

# 손글씨가 칸 위아래 선을 넘는 경우가 많아서 칸 높이 대비 위아래로 여유를 준다.
PAD_RATIO = 0.25
# 작은 crop은 검출 모델이 가장자리 글자를 놓치기 쉬워서 흰 여백을 붙인다.
BORDER_PX = 32


def quad_of(roi):
    if "quad" in roi:
        return np.float32(roi["quad"])
    x1, y1, x2, y2 = roi["bbox"]
    return np.float32([[x1, y1], [x2, y1], [x2, y2], [x1, y2]])


def expand_quad(quad, pad_ratio=PAD_RATIO):
    """quad를 세로 방향(좌상->좌하 방향)으로 pad_ratio 만큼 위아래로 늘린다."""
    q = np.float32(quad)
    up_left = (q[0] - q[3]) * pad_ratio
    up_right = (q[1] - q[2]) * pad_ratio
    return np.float32([q[0] + up_left, q[1] + up_right, q[2] - up_right, q[3] - up_left])


def crop_quad(image, quad, pad_ratio=PAD_RATIO):
    q = expand_quad(quad, pad_ratio)
    w = int(round(max(np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[2] - q[3]))))
    h = int(round(max(np.linalg.norm(q[3] - q[0]), np.linalg.norm(q[2] - q[1]))))
    M = cv2.getPerspectiveTransform(q, np.float32([[0, 0], [w, 0], [w, h], [0, h]]))
    crop = cv2.warpPerspective(image, M, (w, h), borderValue=(255, 255, 255))
    return cv2.copyMakeBorder(
        crop, BORDER_PX, BORDER_PX, BORDER_PX, BORDER_PX, cv2.BORDER_CONSTANT, value=(255, 255, 255)
    )


def ocr_crop(crop):
    ocr = get_ocr()
    start = time.perf_counter()
    page = ocr.predict(crop)[0]
    runtime = time.perf_counter() - start

    items = []
    for text, score, poly in zip(page["rec_texts"], page["rec_scores"], page["rec_polys"]):
        xs = [int(p[0]) for p in poly]
        ys = [int(p[1]) for p in poly]
        items.append(
            {"text": text, "confidence": float(score), "bbox": [min(xs), min(ys), max(xs), max(ys)]}
        )
    # 한 칸 안에서도 박스가 여러 개로 쪼개질 수 있음 -> 왼쪽에서 오른쪽 순서로 이어 붙인다
    items.sort(key=lambda it: it["bbox"][0])
    text = " ".join(it["text"] for it in items)
    conf = float(np.mean([it["confidence"] for it in items])) if items else 0.0
    return {"text": text, "confidence": conf, "runtime_sec": runtime, "items": items}


def main():
    args = sys.argv[1:]
    pad = PAD_RATIO
    if "--pad" in args:
        i = args.index("--pad")
        pad = float(args[i + 1])
        del args[i:i + 2]
    if len(args) < 2:
        print("usage: python roi_ocr.py <roi_json> <out_dir> [<image_dir>] [--pad 0.25]")
        sys.exit(1)

    roi_path = Path(args[0]).resolve()
    out_dir = Path(args[1]).resolve()
    image_dir = Path(args[2]).resolve() if len(args) > 2 else DEFAULT_IMAGE_DIR
    crop_dir = out_dir / "crops"
    crop_dir.mkdir(parents=True, exist_ok=True)

    rois = json.loads(roi_path.read_text(encoding="utf-8"))
    for image_name, entry in rois.items():
        if image_name.startswith("_"):
            continue
        image_path = image_dir / image_name
        image = cv2.imread(str(image_path))
        stem = Path(image_name).stem

        fields = {}
        for field, roi in entry["fields"].items():
            crop = crop_quad(image, quad_of(roi), pad)
            cv2.imwrite(str(crop_dir / f"{stem}_{field}.jpg"), crop, [cv2.IMWRITE_JPEG_QUALITY, 90])
            fields[field] = ocr_crop(crop)

        result = {
            "image_id": image_name,
            "roi_source": str(roi_path.relative_to(ROOT)) if roi_path.is_relative_to(ROOT) else str(roi_path),
            "pad_ratio": pad,
            "runtime_sec": sum(f["runtime_sec"] for f in fields.values()),
            "meta": run_meta(),
            "fields": fields,
        }
        out_path = out_dir / f"{stem}_roi_ocr.json"
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        summary = ", ".join(f"{k}={v['text']!r}" for k, v in fields.items())
        print(f"[run] {image_name} ({result['runtime_sec']:.2f}s): {summary}")


if __name__ == "__main__":
    main()
