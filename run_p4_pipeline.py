"""P4 Anchor-ROI: input image(s) -> first OCR -> existing anchor mapper -> ROI reOCR.

Requires the repository's anchor_field_mapper.py and the verified helper file
run_p4_roi_reocr_v2.py in the same folder. Keeps both files unchanged.

Usage (from the project root with .venv activated):
    python run_p4_pipeline.py sample.jpg
    python run_p4_pipeline.py sample.jpg --first-pass-cache full_ocr_result.json
    python run_p4_pipeline.py data\\development --gt data\\eval_v1\\field_gt.json

Outputs per image: first_pass_ocr.json, field_rois.json, final_fields.json,
individual <field>_crop.png, summary.csv; plus combined summary.csv.

Development/PoC only. Never tune parameters on holdout_test.
"""

import os
os.environ.setdefault("FLAGS_enable_pir_api", "0")

import argparse
import csv
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from run_p4_roi_reocr_v2 import (
    KEY_MAP,
    clipped_bbox,
    extract_ocr_text,
    gt_coverage,
    normalize_for_output,
    read_image,
    read_json,
    save_crop,
    select_field_value,
    write_json,
)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
CSV_COLUMNS = [
    "image_id", "field", "roi_found", "prediction", "normalized_prediction",
    "failure_reason", "gt_raw_text", "field_exact_match_raw", "roi_gt_coverage",
    "full_image_ocr_sec", "roi_reocr_sec", "total_sec",
]


def list_images(path: Path):
    if path.is_file():
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"지원하지 않는 이미지 확장자: {path}")
        return [path]
    if not path.is_dir():
        raise FileNotFoundError(f"입력 이미지/폴더가 없습니다: {path}")
    images = sorted(p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS)
    if not images:
        raise ValueError(f"이미지가 없는 폴더: {path}")
    stems = [p.stem for p in images]
    if len(set(stems)) != len(stems):
        raise ValueError("같은 폴더 안에 확장자만 다른 동명이미지가 있습니다. image_id 충돌 방지가 필요합니다.")
    return images


def first_pass_items(engine, image):
    # PaddleOCR v3 recognizes numpy arrays, avoiding Windows Korean path issues.
    _joined, tokens = extract_ocr_text(engine.predict(image))
    return [
        {"text": token["text"], "score": token["score"], "bbox": token["bbox_in_crop"]}
        for token in tokens if token["bbox_in_crop"] is not None
    ]


def existing_anchor_mapper(ocr_items, mapper_script: Path):
    """Run the original, unchanged mapper with per-image input in a temp cwd.

    The old script is hardcoded to full_ocr_result.json and sample.jpg. Isolating
    it in a temporary working directory lets it be reused without overwriting
    any project-root files. Its reported 'image' is replaced by the caller.
    """
    with tempfile.TemporaryDirectory(prefix="p4_anchor_") as tmp:
        wd = Path(tmp)
        write_json(wd / "full_ocr_result.json", ocr_items)
        command = [sys.executable, "-X", "utf8", str(mapper_script)]
        run = subprocess.run(command, cwd=str(wd), capture_output=True, check=False)
        if run.returncode:
            error_text = run.stderr.decode("utf-8", errors="replace")[-2500:]
            raise RuntimeError(f"기존 Anchor 매퍼 실행 실패: {error_text}")
        result = read_json(wd / "field_mapping_result.json")
    return result.get("fields", {})


def gt_for_image(gt_data, image_path: Path):
    per_image = gt_data.get(image_path.name, gt_data.get(image_path.stem, {}))
    if not per_image:
        import csv
        manifest = Path("data/eval_v1_packages/development/manifest.csv")
        if manifest.exists():
            with manifest.open(encoding="utf-8-sig", newline="") as f:
                for row in csv.DictReader(f):
                    if Path(row["filename"]).name.lower() == image_path.name.lower():
                        per_image = gt_data.get(row["image_id"], {})
                        break
    if not isinstance(per_image, dict):
        return {}
    fields = per_image.get("fields", per_image)
    if not isinstance(fields, dict):
        return {}
    result = {}
    for korean, english in KEY_MAP.items():
        value = fields.get(english, fields.get(korean))
        if isinstance(value, dict):
            result[english] = value
    return result


def ground_truth_text(value):
    if not isinstance(value, dict):
        return None
    # Evaluation here is raw text match; normalized comparison is owned by the
    # team's evaluator so pipeline normalization won't alter the experiment.
    for key in ("raw_text", "value"):
        if value.get(key) is not None:
            return str(value[key])
    return None


def process_one(image_path, engine, args, mapper_script, gt_data, cache=None):
    started = time.perf_counter()
    image = read_image(image_path)
    if image is None:
        raise RuntimeError(f"이미지 읽기 실패: {image_path}")
    height, width = image.shape[:2]
    out_dir = args.output / image_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    started_ocr = time.perf_counter()
    if cache is None:
        ocr_items = first_pass_items(engine, image)
    else:
        ocr_items = read_json(cache)
        if not isinstance(ocr_items, list):
            raise ValueError("1차 OCR 캐시는 OCR 토큰 배열(JSON list)이어야 합니다.")
    full_ocr_sec = round(time.perf_counter() - started_ocr, 4)
    write_json(out_dir / "first_pass_ocr.json", ocr_items)

    mapped = existing_anchor_mapper(ocr_items, mapper_script)
    gt = gt_for_image(gt_data, image_path)
    roi_fields = {}
    final_fields = {}
    rows = []

    for source_field, field in KEY_MAP.items():
        entry = mapped.get(source_field, {})
        anchor_found = bool(entry.get("anchor_found", False))
        raw_bbox = entry.get("value_roi")
        bbox = clipped_bbox(raw_bbox, width, height, args.padding)
        failure_reason = None
        raw_reocr = None
        prediction = None
        tokens = []
        selected = []
        selection_info = {}
        roi_ocr_sec = None
        if bbox is None:
            failure_reason = "ANCHOR_NOT_FOUND" if not anchor_found else "ROI_TOO_SMALL"
        else:
            x1, y1, x2, y2 = bbox
            crop = image[y1:y2, x1:x2]
            if crop.size == 0 or crop.shape[0] < 5 or crop.shape[1] < 5:
                failure_reason = "ROI_TOO_SMALL"
            else:
                save_crop(out_dir / f"{field}_crop.png", crop)
                started_roi = time.perf_counter()
                try:
                    raw_reocr, tokens = extract_ocr_text(engine.predict(crop))
                    prediction, selected, selection_info = select_field_value(
                        field, tokens, entry.get("anchor_bbox"), bbox
                    )
                    if prediction is None:
                        failure_reason = "OCR_FAILURE"
                except Exception as exc:
                    failure_reason = "OCR_FAILURE"
                    selection_info["error"] = f"{type(exc).__name__}: {exc}"
                roi_ocr_sec = round(time.perf_counter() - started_roi, 4)

        scores = [token["score"] for token in selected if token.get("score") is not None]
        confidence = min(scores) if scores else None
        normalized = normalize_for_output(prediction)
        ref = gt.get(field, {})
        ref_raw = ground_truth_text(ref)
        coverage = gt_coverage(ref.get("bbox"), bbox) if isinstance(ref, dict) else None
        match = prediction == ref_raw if ref_raw is not None else None
        # GT is used ONLY for evaluation labels, never for prediction or
        # selecting ROI/OCR tokens. These broad classes require manual review.
        evaluated_reason = failure_reason
        if evaluated_reason is None and match is False:
            evaluated_reason = "ROI_TOO_SMALL" if (coverage is not None and coverage < 0.90) else "OCR_FAILURE"

        roi_fields[field] = {
            "field": field,
            "bbox": bbox,
            "raw_bbox": raw_bbox,
            "anchor_bbox": entry.get("anchor_bbox"),
            "method": "anchor_relative_roi",
            "anchor_method": entry.get("anchor_method", "exact_anchor") if anchor_found else None,
            "confidence": confidence,
            "roi_found": bbox is not None,
            "failure_reason": failure_reason,
        }
        final_fields[field] = {
            "prediction": prediction,
            "normalized_prediction": normalized,
            "raw_reocr_prediction": raw_reocr,
            "confidence": confidence,
            "ocr_tokens": tokens,
            "selected_tokens": selected,
            "selection_info": selection_info,
            "failure_reason": evaluated_reason,
            "failure_review_note": "GT-based classification is provisional; OCR_FAILURE may include value-selection errors" if match is False else None,
        }
        rows.append({
            "image_id": image_path.name,
            "field": field,
            "roi_found": bbox is not None,
            "prediction": prediction or "",
            "normalized_prediction": normalized or "",
            "failure_reason": evaluated_reason or "",
            "gt_raw_text": ref_raw if ref_raw is not None else "",
            "field_exact_match_raw": "" if match is None else match,
            "roi_gt_coverage": "" if coverage is None else f"{coverage:.6f}",
            "full_image_ocr_sec": full_ocr_sec,
            "roi_reocr_sec": "" if roi_ocr_sec is None else roi_ocr_sec,
            "total_sec": "",  # filled in after all five fields
        })
        status = evaluated_reason or ("MATCH" if match is True else "NO_GT")
        print(f"  {field}: {prediction!r} | {status}")

    elapsed = round(time.perf_counter() - started, 4)
    for row in rows:
        row["total_sec"] = elapsed
    write_json(out_dir / "field_rois.json", {
        "image_id": image_path.name,
        "image_width": width,
        "image_height": height,
        "padding_px": args.padding,
        "fields": roi_fields,
    })
    write_json(out_dir / "final_fields.json", {
        "image_id": image_path.name,
        "pipeline": "P4 anchor ROI -> original image crop -> second-pass OCR -> conservative normalization",
        "normalization_note": "NFC/whitespace only; team-wide comparison must use Dahye's common evaluator",
        "first_pass_source": "cached_ocr" if cache is not None else "live_paddleocr",
        "total_sec": elapsed,
        "fields": final_fields,
    })
    write_summary(out_dir / "summary.csv", rows)
    return rows


def write_summary(path, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.DictWriter(fp, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="P4 Anchor ROI End-to-End (development only)")
    parser.add_argument("input", type=Path, help="image file or folder of development images")
    parser.add_argument("--output", type=Path, default=Path("results") / "p4_e2e")
    parser.add_argument("--gt", type=Path, default=Path("field_gt.json"))
    parser.add_argument("--padding", type=int, default=8)
    parser.add_argument("--batch-cache-dir", type=Path, default=None)
    parser.add_argument("--first-pass-cache", type=Path, default=None,
                        help="single-image PoC reproduction only, not final measured e2e")
    args = parser.parse_args()
    if args.padding < 0:
        parser.error("--padding must be >= 0")

    images = list_images(args.input)
    if args.batch_cache_dir and args.first_pass_cache:
        parser.error("두 캐시 옵션은 동시에 사용할 수 없습니다")
    if args.first_pass_cache and len(images) != 1:
        parser.error("--first-pass-cache works only for a single image")
    mapper_script = Path(__file__).resolve().parent / "anchor_field_mapper.py"
    if not mapper_script.is_file():
        parser.error(f"기존 Anchor 매핑 파일이 없습니다: {mapper_script}")
    gt_data = read_json(args.gt) if args.gt.is_file() else {}
    args.output.mkdir(parents=True, exist_ok=True)

    from paddleocr import PaddleOCR
    engine = PaddleOCR(
        lang="korean",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        enable_mkldnn=False,
    )
    all_rows = []
    for idx, image_path in enumerate(images, 1):
        print(f"\n[{idx}/{len(images)}] {image_path}")
        cache = args.first_pass_cache
        if args.batch_cache_dir:
            cache = args.batch_cache_dir / image_path.stem / "first_pass_ocr.json"
            if not cache.is_file():
                raise FileNotFoundError(f"1차 OCR 캐시 없음: {cache}")
        rows = process_one(image_path, engine, args, mapper_script, gt_data,
                           cache=cache)
        all_rows.extend(rows)
    write_summary(args.output / "summary.csv", all_rows)
    scored = [r for r in all_rows if r["field_exact_match_raw"] != ""]
    matches = sum(r["field_exact_match_raw"] is True for r in scored)
    roi_count = sum(r["roi_found"] is True for r in all_rows)
    print(f"\nROI 생성: {roi_count}/{len(all_rows)}")
    if scored:
        print(f"Field Exact Match (raw): {matches}/{len(scored)}")
    else:
        print("GT 없는 이미지: Field Accuracy 계산 생략")
    print(f"결과: {args.output.resolve()}")
    print("참고: Field Accuracy 최종 수치는 공통 평가 규칙 확정 후 사용하세요.")


if __name__ == "__main__":
    main()
