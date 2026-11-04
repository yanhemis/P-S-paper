"""P4 Anchor ROI 2nd-pass OCR smoke test for the existing single-image PoC.

Reads field_mapping_result.json created by anchor_field_mapper.py.
Crops each mapped ROI from its ORIGINAL image, performs PaddleOCR 3.x again,
and saves field_rois.json, final_fields.json, summary.csv and cropped PNGs.

This is a single-image integration test, not yet the final batch / hold-out pipeline.
"""

import os
os.environ.setdefault("FLAGS_enable_pir_api", "0")

import argparse
import csv
import json
import re
import time
import unicodedata
from pathlib import Path

import cv2
import numpy as np


KEY_MAP = {
    "소재지": "address",
    "보증금": "deposit",
    "계약금": "contract_amount",
    "임대인_성명": "lessor_name",
    "임차인_성명": "lessee_name",
}


def read_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)


def read_image(path):
    # Unicode-safe on Windows paths containing Korean characters.
    image_bytes = np.fromfile(str(path), dtype=np.uint8)
    return cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)


def save_crop(path, crop):
    ok, data = cv2.imencode(".png", crop)
    if not ok:
        raise RuntimeError(f"이미지 저장 실패: {path}")
    data.tofile(str(path))


def clipped_bbox(bbox, width, height, padding):
    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
        return None
    x1, y1, x2, y2 = [int(round(float(x))) for x in bbox]
    # Do not extend to the left: it can include the printed anchor label.
    x1 = max(0, min(width, x1))
    y1 = max(0, min(height, y1 - padding))
    x2 = max(0, min(width, x2 + padding))
    y2 = max(0, min(height, y2 + padding))
    if x2 <= x1 or y2 <= y1:
        return None
    return [x1, y1, x2, y2]


def extract_ocr_text(pages):
    collected = []
    for page in pages:
        result = page.json
        if isinstance(result, str):
            result = json.loads(result)
        info = result.get("res", result)
        texts = info.get("rec_texts", [])
        scores = info.get("rec_scores", [])
        boxes = info.get("rec_boxes", [])
        if texts is None:
            texts = []
        if scores is None:
            scores = []
        if boxes is None:
            boxes = []
        for i, text in enumerate(texts):
            if not str(text).strip():
                continue
            box = [int(v) for v in boxes[i]] if i < len(boxes) else None
            collected.append({
                "text": str(text),
                "score": float(scores[i]) if i < len(scores) else None,
                "bbox_in_crop": box,
            })
    # Keep OCR engine's order; note that address and mixed rows may need
    # field-specific text filtering in a later development iteration.
    joined = " ".join(token["text"] for token in collected) if collected else None
    return joined, collected


# Value selection relies only on OCR boxes, Korean amount/name syntax, and the
# first-pass ANCHOR coordinates. Ground truth and old first-pass VALUE strings
# are NEVER used for selecting the prediction.
HANGUL_AMOUNT = re.compile(r"^[일이삼사오육칠팔구십백천만억조]+(?:원)?$")
NUMBER_AMOUNT = re.compile(r"^[0-9][0-9,]*(?:원)?$")
PERSON_NAME = re.compile(r"^[가-힣]{2,5}$")
NOT_NAMES = {"성명", "임대인", "임차인", "본인", "주소", "서명", "인감"}


def select_field_value(field, all_tokens, anchor_bbox, crop_bbox):
    """Select second-pass OCR tokens on the expected anchor row.

    This is a first-pass heuristic for *single-line* Korean lease-contract
    fields; it must be evaluated on development images before code freeze.
    Return (predicted_text, selected_tokens, selection_info).
    """
    valid = [t for t in all_tokens if t.get("bbox_in_crop") and str(t.get("text", "")).strip()]
    info = {"method": "anchor_row_and_field_format_v1", "raw_token_count": len(valid)}
    if not valid:
        return None, [], info

    # Estimate the relevant OCR text row using the printed ANCHOR's y center.
    # The ROI image's origin is the *clipped* bbox (not raw_bbox).
    if anchor_bbox and crop_bbox:
        anchor_center_y = (anchor_bbox[1] + anchor_bbox[3]) / 2 - crop_bbox[1]
        anchor_height = max(1, anchor_bbox[3] - anchor_bbox[1])
        max_distance = max(18.0, 0.75 * anchor_height)
        anchor_top = anchor_bbox[1] - crop_bbox[1]
        anchor_bottom = anchor_bbox[3] - crop_bbox[1]
        def in_anchor_row(token):
            top, bottom = token["bbox_in_crop"][1], token["bbox_in_crop"][3]
            token_height = max(1, bottom - top)
            overlap = max(0, min(bottom, anchor_bottom) - max(top, anchor_top))
            token_center = (top + bottom) / 2
            return abs(token_center - anchor_center_y) <= max_distance and overlap / token_height >= 0.45
        near_row = [t for t in valid if in_anchor_row(t)]
        info["expected_row_center_y_in_crop"] = round(anchor_center_y, 2)
        info["allowed_row_center_distance"] = round(max_distance, 2)
    else:
        near_row = valid
        info["method"] = "no_anchor_row_fallback"

    # Do not let an empty row silently turn unrelated neighboring text into a
    # confident prediction; this can happen on a different form layout.
    if not near_row:
        info["no_tokens_near_anchor_row"] = True
        info["selected_token_count"] = 0
        return None, [], info

    info["near_row_token_count"] = len(near_row)

    if field in {"deposit", "contract_amount"}:
        # Exclude words from adjacent rows, e.g., '따라', '원정은', '사천2'.
        candidates = [t for t in near_row if HANGUL_AMOUNT.fullmatch(t["text"].strip())
                      or NUMBER_AMOUNT.fullmatch(t["text"].replace(" ", ""))]
        # Prefer a token closest to the printed-label row, then closest to
        # the LEFT edge of the mapped ROI. Do not inspect ground truth text.
        if anchor_bbox and crop_bbox:
            candidates.sort(key=lambda t: (
                abs((t["bbox_in_crop"][1] + t["bbox_in_crop"][3]) / 2 - anchor_center_y),
                t["bbox_in_crop"][0],
            ))
        else:
            candidates.sort(key=lambda t: t["bbox_in_crop"][0])
        selected = candidates[:1]

    elif field in {"lessor_name", "lessee_name"}:
        candidates = [t for t in near_row
                      if PERSON_NAME.fullmatch(t["text"].replace(" ", ""))
                      and t["text"].replace(" ", "") not in NOT_NAMES]
        # Adjacent stamp/seal text is to the right of the actual name.
        candidates.sort(key=lambda t: t["bbox_in_crop"][0])
        selected = candidates[:1]

    elif field == "address":
        # PaddleOCR does not guarantee reading order inside a large crop.
        # Reorder single-line address tokens in spatial left-to-right order.
        selected = sorted(near_row, key=lambda t: t["bbox_in_crop"][0])

    else:
        selected = sorted(near_row, key=lambda t: t["bbox_in_crop"][0])

    info["selected_token_count"] = len(selected)
    info["discarded_token_count"] = len(valid) - len(selected)
    if not selected:
        return None, [], info

    prediction = " ".join(t["text"].strip() for t in selected)
    return prediction, selected, info


def normalize_for_output(text):
    """Conservative provisional normalization; final comparison must use Dahye's rule."""
    if text is None:
        return None
    return " ".join(unicodedata.normalize("NFC", text).split())


def gt_coverage(gt_bbox, roi):
    if not gt_bbox or not roi:
        return None
    gx1, gy1, gx2, gy2 = gt_bbox
    rx1, ry1, rx2, ry2 = roi
    gt_area = max(0, gx2 - gx1) * max(0, gy2 - gy1)
    if gt_area == 0:
        return None
    intersection = max(0, min(gx2, rx2) - max(gx1, rx1)) * max(0, min(gy2, ry2) - max(gy1, ry1))
    return intersection / gt_area


def main():
    parser = argparse.ArgumentParser(description="P4 single-image ROI reOCR smoke test")
    parser.add_argument("--mapping", default="field_mapping_result.json")
    parser.add_argument("--gt", default="field_gt.json")
    parser.add_argument("--padding", type=int, default=8, help="extra pixels around original ROI")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    if args.padding < 0:
        parser.error("--padding must be >= 0")

    mapping = read_json(args.mapping)
    image_path = Path(mapping["image"])
    image = read_image(image_path)
    if image is None:
        raise FileNotFoundError(f"이미지를 열 수 없습니다: {image_path}")

    height, width = image.shape[:2]
    out_dir = Path(args.output) if args.output else Path("results") / f"p4_{image_path.stem}_v2"
    out_dir.mkdir(parents=True, exist_ok=True)
    gt_fields = {}
    if Path(args.gt).is_file():
        gt_data = read_json(args.gt)
        gt_fields = gt_data.get(mapping["image"], gt_data.get(image_path.name, {}))

    # Exactly the same OCR parameters as the project's existing full_ocr.py.
    from paddleocr import PaddleOCR
    engine = PaddleOCR(
        lang="korean",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        enable_mkldnn=False,
    )

    roi_records = {}
    final_records = {}
    rows = []
    start = time.perf_counter()
    for source_field, standard_field in KEY_MAP.items():
        original = mapping.get("fields", {}).get(source_field, {})
        raw_bbox = original.get("value_roi")
        bbox = clipped_bbox(raw_bbox, width, height, args.padding)
        reason = None
        prediction = None
        raw_prediction = None
        tokens = []
        selected_tokens = []
        selection_info = {}
        time_sec = None
        if bbox is None:
            reason = "ANCHOR_NOT_FOUND" if not original.get("anchor_found") else "ROI_TOO_SMALL"
        else:
            x1, y1, x2, y2 = bbox
            crop = image[y1:y2, x1:x2]
            if crop.size == 0 or crop.shape[0] < 5 or crop.shape[1] < 5:
                reason = "ROI_TOO_SMALL"
            else:
                save_crop(out_dir / f"{standard_field}_crop.png", crop)
                t0 = time.perf_counter()
                try:
                    raw_prediction, tokens = extract_ocr_text(engine.predict(crop))
                    prediction, selected_tokens, selection_info = select_field_value(
                        standard_field, tokens, original.get("anchor_bbox"), bbox
                    )
                    if prediction is None:
                        reason = "OCR_FAILURE"
                except Exception as exc:
                    reason = "OCR_FAILURE"
                    print(f"[{standard_field}] OCR 실행 오류: {type(exc).__name__}: {exc}")
                time_sec = round(time.perf_counter() - t0, 4)

        confidence = min((t["score"] for t in selected_tokens if t["score"] is not None), default=None)
        roi_records[standard_field] = {
            "field": standard_field,
            "bbox": bbox,
            "raw_bbox": raw_bbox,
            "anchor_bbox": original.get("anchor_bbox"),
            "method": "anchor_relative_roi",
            "anchor_method": original.get("anchor_method", "exact_anchor"),
            "confidence": confidence,
            "roi_found": bbox is not None,
            "failure_reason": reason,
        }
        normalized = normalize_for_output(prediction)
        gt = gt_fields.get(source_field, {})
        ref_text = gt.get("value") if isinstance(gt, dict) else None
        coverage = gt_coverage(gt.get("bbox"), bbox) if isinstance(gt, dict) else None
        final_records[standard_field] = {
            "prediction": prediction,
            "normalized_prediction": normalized,
            "raw_reocr_prediction": raw_prediction,
            "ocr_tokens": tokens,
            "selected_tokens": selected_tokens,
            "selection_info": selection_info,
            "legacy_prediction_not_used": original.get("value"),
            "confidence": confidence,
            "failure_reason": reason,
        }
        rows.append({
            "image_id": image_path.name,
            "field": standard_field,
            "roi_found": bbox is not None,
            "prediction": prediction or "",
            "normalized_prediction": normalized or "",
            "raw_reocr_prediction": raw_prediction or "",
            "failure_reason": reason or "",
            "gt_value": ref_text or "",
            "field_exact_match_raw": "" if ref_text is None else prediction == ref_text,
            "roi_gt_coverage": "" if coverage is None else f"{coverage:.6f}",
            "reocr_sec": "" if time_sec is None else time_sec,
        })
        status = reason or ("MATCH" if ref_text is not None and prediction == ref_text
                            else "MISMATCH" if ref_text is not None else "OCR_DONE")
        print(f"{standard_field}: {prediction!r} | 기존={original.get('value')!r} | {status}")

    duration = time.perf_counter() - start
    write_json(out_dir / "field_rois.json", {
        "image_id": image_path.name,
        "image_width": width,
        "image_height": height,
        "padding_px": args.padding,
        "fields": roi_records,
    })
    write_json(out_dir / "final_fields.json", {
        "image_id": image_path.name,
        "pipeline": "P4 Anchor ROI (single-image second-pass OCR + row/value filtering test)",
        "selection_note": "rule-based filtering of second-pass OCR using anchor row and field syntax; no ground-truth-guided selection",
        "normalization_note": "NFC + collapse whitespace (provisional, must align with shared evaluation)",
        "roi_reocr_total_sec_excludes_full_page_ocr_and_anchor_mapping": round(duration, 4),
        "fields": final_records,
    })
    with open(out_dir / "summary.csv", "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    correct_rows = [r for r in rows if r["field_exact_match_raw"] != ""]
    correct = sum(r["field_exact_match_raw"] is True for r in correct_rows)
    print(f"\n2차 OCR + 값 선택 Field Exact Match (raw): {correct}/{len(correct_rows)}" if correct_rows else "\nGT가 없어 정확도 미계산")
    print(f"출력 폴더: {out_dir.resolve()}")
    print("주의: 이번 시간 측정에는 1차 전체 OCR과 Anchor 매핑이 포함되지 않습니다.")


if __name__ == "__main__":
    main()
