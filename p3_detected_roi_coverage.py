"""
P3 Detected ROI Coverage — bang_ (05_current_team_tasks_20261101.md 2절, 04_data_collection_gt_protocol.md 7절)

구조 복원(Task_0930.py)과 필드 셀 선택 기준(field_roi.py)은 동결 상태 그대로 쓰고, 이 파일은
이미 만들어진 결과(<image_id>/cells_original.json, cells.json, report.json)를 읽어
  1) 필드별 Detected ROI 후보 목록 (원본 좌표)
  2) GT BBox 기준 ROI Coverage = Area(GT ∩ ROI) / Area(GT), 후보가 여럿이면 max
  3) 이미지별 summary.csv / summary.json (image_id, target_fields, detected_fields, roi_coverage, failure_reason)
을 만든다. 파이프라인을 다시 돌리지 않으며 파라미터도 바꾸지 않는다.

실행 (프로젝트 폴더에서)
  python Task_10_Renewal.py --dataset development        # 셀 결과 생성 + 이 파일까지 자동 실행
  python p3_detected_roi_coverage.py --dataset development   # 셀 결과는 그대로 두고 Coverage 만 다시 계산
  python Task_10_Renewal.py --dataset holdout_test       # 동결 후 1회: 셀 결과 + Coverage
  holdout_test 는 코드·환경이 frozen_params.json 과 같을 때만 계산한다 (이 파일도 동결 대상).

입력
  output/eval_v1/<split>/<image_id>/{cells_original.json, cells.json, report.json}
  data/eval_v1_packages/<split>/{manifest.csv, field_gt.json}

평가 규칙 (04 문서 7절)
  - GT BBox 는 원본 이미지 픽셀 좌표 [x_min, y_min, x_max, y_max]. 비교 대상 ROI 도 원본 좌표(cells_original.json) 만 쓴다.
  - Coverage = Area(GT ∩ ROI) / Area(GT). IoU 는 쓰지 않는다.
  - Coverage >= 0.90 → Covered, 미만 → Not Covered. ROI 미생성 → Coverage 0.
  - P3: 한 필드에 ROI 후보가 여럿이면 max_i Coverage(GT, ROI_i).
  - status unreadable / not_present 필드는 분모에서 제외.
  - bbox null 필드는 ROI Coverage 미평가 (0 또는 1 을 임의로 주지 않음).
  - 보고: 평균 Coverage + Covered Rate = Covered 필드 수 / 평가 가능 필드 수.

ROI 후보 (GT 를 보지 않고 정한다)
  field_roi.py 와 같은 방식으로 기준 양식(sample_1)의 상대 위치를 새 이미지의 같은 표에 옮겨
  기대 영역 E 를 만든 뒤,
    - E 의 중심을 포함하는 셀 (= field_roi.py 가 고르는 셀, primary)
    - E 와 겹치는 면적이 min(셀 면적, E 면적)의 CAND_MIN_OVERLAP 이상인 같은 표의 셀
  을 후보로 둔다 (최대 MAX_CANDIDATES 개). 값이 두 셀로 나뉘어 검출된 경우를 후보로 남기기 위함이다.

실패 유형 (필드 단위, Covered 가 아닐 때만 기록)
  TABLE_MISSING     필드가 있어야 할 표를 못 찾았거나 그 위치에 셀이 없음 (ROI 미생성, Coverage 0)
  ROW_MERGE         primary 셀 높이 > 기준 셀 높이 × 1.8
  COLUMN_MERGE      primary 셀 폭 > 기준 셀 폭 × 1.8
  CELL_MERGE        높이·폭 모두 초과
  WRONG_MAPPING     후보는 GT 를 덮지 못하는데, 이미지의 다른 셀 중 GT 를 0.90 이상 덮는 셀이 있음
  COORDINATE_ERROR  GT 를 0.90 이상 덮는 셀이 이미지 어디에도 없음 (경계 어긋남/분할)
  RUN_ERROR         파이프라인 결과 파일이 없음
  Covered 인데 primary 셀이 병합 크기면 roi_flag 에 *_MERGE 를 남긴다 (실패로 세지 않음, ROI_TOO_LARGE 확인용).
"""
import argparse
import csv
import hashlib
import json
import sys
import time
from pathlib import Path

import field_roi as fr

ROOT = Path(__file__).resolve().parent
EVAL_DIR = ROOT / "data" / "eval_v1_packages"
EVAL_OUT = ROOT / "output" / "eval_v1"
FROZEN = ROOT / "frozen_params.json"

FIELDS = fr.FIELDS
COVERED_THRESHOLD = 0.90      # 04 문서 7절
CAND_MIN_OVERLAP = 0.5        # 후보 셀 판정: E 와의 겹침 / min(셀 면적, E 면적)
MAX_CANDIDATES = 5
EXCLUDED_STATUS = {"unreadable", "not_present"}
FAIL_ORDER = ["TABLE_MISSING", "ROW_MERGE", "COLUMN_MERGE", "CELL_MERGE", "WRONG_MAPPING",
              "COORDINATE_ERROR", "RUN_ERROR"]


# ----------------------------------------------------------------
# 공통 유틸
# ----------------------------------------------------------------
def _area(b):
    return max(0, b[2] - b[0]) * max(0, b[3] - b[1])


def _inter(a, b):
    return _area([max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])])


def coverage(gt, roi):
    """GT 면적 중 ROI 가 덮는 비율 (04 문서 7절)"""
    a = _area(gt)
    return _inter(gt, roi) / a if a else 0.0


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _write_csv(path, rows):
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def _rate(n, d):
    return round(n / d, 4) if d else None


# ----------------------------------------------------------------
# 데이터셋
# ----------------------------------------------------------------
def read_manifest(split):
    path = EVAL_DIR / split / "manifest.csv"
    if not path.exists():
        return None
    with open(path, encoding="utf-8-sig") as f:
        return [r for r in csv.DictReader(f) if r.get("split", "").strip() == split]


def read_gt(split, image_id):
    """
    반환: {field: {"bbox": [..] | None, "state": "eval" | "excluded" | "bbox_null", "reason": str}}
    """
    path = EVAL_DIR / split / "field_gt.json"
    entry = (_read_json(path).get(image_id) if path.exists() else None) or {}
    gf = entry.get("fields", {})
    out = {}
    for f in FIELDS:
        v = gf.get(f)
        if not isinstance(v, dict):
            out[f] = {"bbox": None, "state": "bbox_null", "reason": "GT_MISSING"}
            continue
        status = (v.get("status") or "").strip().lower()
        if status in EXCLUDED_STATUS:
            out[f] = {"bbox": None, "state": "excluded", "reason": status}
        elif not v.get("bbox"):
            out[f] = {"bbox": None, "state": "bbox_null", "reason": "GT_BBOX_NULL"}
        else:
            b = [int(round(x)) for x in v["bbox"]]
            out[f] = {"bbox": b, "state": "eval", "reason": ""}
    return out


# ----------------------------------------------------------------
# ROI 후보 (GT 미사용)
# ----------------------------------------------------------------
def field_candidates(folder, ref):
    """
    반환: {field: {"candidates": [{cell_id, type, bbox_original, primary}], "structure": 실패유형|None,
                   "size_ratio": [w, h] | None}}
    표·위치 판정은 aligned 좌표(cells.json, report.json), ROI 좌표는 같은 id 의 cells_original.json.
    """
    cells = _read_json(folder / "cells.json")["cells"]
    orig = {c["id"]: c["bbox"] for c in _read_json(folder / "cells_original.json")["cells"]}
    report = _read_json(folder / "report.json")
    H = report["image_size"][1]
    tables = report["tables"]
    by_table = {}
    for c in cells:
        by_table.setdefault(c["table"], []).append(c)

    out = {}
    for f in FIELDS:
        r = ref["fields"][f]
        item = {"candidates": [], "structure": None, "size_ratio": None}
        near = [(abs((tb["bbox"][1] + tb["bbox"][3]) / 2 / H - r["table_cy"]), tb) for tb in tables]
        near = [x for x in near if x[0] <= fr.TABLE_MATCH_TOL]
        if not near:
            item["structure"] = "TABLE_MISSING"
            out[f] = item
            continue
        tb = min(near, key=lambda x: x[0])[1]
        tx1, ty1, tx2, ty2 = tb["bbox"]
        tw, th = tx2 - tx1, ty2 - ty1
        px, py = tx1 + r["rx"] * tw, ty1 + r["ry"] * th
        ew, eh = r["rw"] * tw, r["rh"] * tw
        E = [px - ew / 2, py - eh / 2, px + ew / 2, py + eh / 2]

        same = by_table.get(tb["table"], [])
        primary = next((c for c in same
                        if c["bbox"][0] <= px < c["bbox"][2] and c["bbox"][1] <= py < c["bbox"][3]), None)
        if primary is None:
            item["structure"] = "TABLE_MISSING"
            out[f] = item
            continue

        x1, y1, x2, y2 = primary["bbox"]
        wr, hr = (x2 - x1) / ew, (y2 - y1) / eh
        item["size_ratio"] = [round(wr, 2), round(hr, 2)]
        if hr > fr.MERGE_RATIO and wr > fr.MERGE_RATIO:
            item["structure"] = "CELL_MERGE"
        elif hr > fr.MERGE_RATIO:
            item["structure"] = "ROW_MERGE"
        elif wr > fr.MERGE_RATIO:
            item["structure"] = "COLUMN_MERGE"

        others = []
        for c in same:
            if c["id"] == primary["id"]:
                continue
            denom = min(_area(c["bbox"]), _area(E))
            ov = _inter(c["bbox"], E) / denom if denom else 0.0
            if ov >= CAND_MIN_OVERLAP:
                others.append((ov, c))
        others.sort(key=lambda x: -x[0])
        chosen = [primary] + [c for _, c in others[:MAX_CANDIDATES - 1]]
        item["candidates"] = [{"cell_id": c["id"], "type": c["type"], "bbox_original": orig[c["id"]],
                               "primary": c["id"] == primary["id"]} for c in chosen]
        out[f] = item
    return out, list(orig.items())


# ----------------------------------------------------------------
# 한 이미지 평가
# ----------------------------------------------------------------
def evaluate_image(folder, ref, gt):
    run_ok = all((folder / n).exists() for n in ("cells.json", "cells_original.json", "report.json"))
    if run_ok:
        cands, all_cells = field_candidates(folder, ref)
    else:
        cands = {f: {"candidates": [], "structure": "RUN_ERROR", "size_ratio": None} for f in FIELDS}
        all_cells = []

    fields = {}
    for f in FIELDS:
        g, c = gt[f], cands[f]
        rec = {"gt_state": g["state"], "gt_bbox": g["bbox"], "roi_generated": bool(c["candidates"]),
               "candidates": c["candidates"], "size_ratio": c["size_ratio"],
               "coverage": None, "best_cell_id": None, "covered": None,
               "failure_reason": "", "roi_flag": "", "not_evaluated": ""}
        if g["state"] != "eval":
            rec["not_evaluated"] = g["reason"]
            fields[f] = rec
            continue
        for cd in c["candidates"]:
            cd["coverage"] = round(coverage(g["bbox"], cd["bbox_original"]), 4)
        if c["candidates"]:
            best = max(c["candidates"], key=lambda x: x["coverage"])
            rec["coverage"], rec["best_cell_id"] = best["coverage"], best["cell_id"]
        else:
            rec["coverage"] = 0.0
        rec["covered"] = rec["coverage"] >= COVERED_THRESHOLD
        if rec["covered"]:
            if c["structure"] in ("ROW_MERGE", "COLUMN_MERGE", "CELL_MERGE"):
                rec["roi_flag"] = c["structure"]
        elif c["structure"]:
            rec["failure_reason"] = c["structure"]
        else:
            any_cover = max((coverage(g["bbox"], b) for _, b in all_cells), default=0.0)
            rec["failure_reason"] = "WRONG_MAPPING" if any_cover >= COVERED_THRESHOLD else "COORDINATE_ERROR"
        fields[f] = rec
    return fields


# ----------------------------------------------------------------
# 실행
# ----------------------------------------------------------------
def run(split):
    rows = read_manifest(split)
    if rows is None:
        print(f"[대기] {EVAL_DIR / split / 'manifest.csv'} 없음")
        return 1
    out_dir = EVAL_OUT / split
    if not out_dir.exists():
        print(f"[대기] {out_dir} 없음 — 먼저 python Task_10_Renewal.py --dataset {split}")
        return 1
    if split == "holdout_test":
        import Task_10_Renewal as tr          # 순환 import 방지: holdout 일 때만
        p_ok, c_ok, msgs = tr.check_frozen()
        if not (p_ok and c_ok):
            print("[중단] holdout_test 는 동결된 코드·환경으로만 평가합니다:\n  - " + "\n  - ".join(msgs))
            return 1

    ref = fr.load_reference()
    summary, details, candidates_json = [], [], {}
    for row in rows:
        image_id = row["image_id"].strip()
        report_path = out_dir / image_id / "report.json"
        status = _read_json(report_path)["status"] if report_path.exists() else "error"
        gt = read_gt(split, image_id)
        res = evaluate_image(out_dir / image_id, ref, gt)

        ev = [f for f in FIELDS if res[f]["gt_state"] == "eval"]
        covered = [f for f in ev if res[f]["covered"]]
        covs = [res[f]["coverage"] for f in ev]
        summary.append({
            "image_id": image_id,
            "target_fields": len(ev),
            "detected_fields": len(covered),
            "roi_coverage": round(sum(covs) / len(covs), 4) if covs else None,
            "failure_reason": "; ".join(f"{f}:{res[f]['failure_reason']}" for f in ev if res[f]["failure_reason"]),
            "covered_rate": _rate(len(covered), len(ev)),
            "roi_generated_fields": sum(res[f]["roi_generated"] for f in FIELDS
                                        if res[f]["gt_state"] != "excluded"),
            "not_evaluated": "; ".join(f"{f}:{res[f]['not_evaluated']}" for f in FIELDS if res[f]["not_evaluated"]),
            "roi_flag": "; ".join(f"{f}:{res[f]['roi_flag']}" for f in FIELDS if res[f]["roi_flag"]),
            "document_group_id": row.get("document_group_id", ""),
            "condition": row.get("condition", ""),
            "pipeline_status": status,
        })
        for f in FIELDS:
            v = res[f]
            details.append({
                "image_id": image_id, "field": f, "gt_state": v["gt_state"],
                "gt_bbox": "" if v["gt_bbox"] is None else " ".join(map(str, v["gt_bbox"])),
                "roi_generated": v["roi_generated"], "n_candidates": len(v["candidates"]),
                "best_cell_id": "" if v["best_cell_id"] is None else v["best_cell_id"],
                "coverage": "" if v["coverage"] is None else v["coverage"],
                "covered": "" if v["covered"] is None else v["covered"],
                "failure_reason": v["failure_reason"], "roi_flag": v["roi_flag"],
                "not_evaluated": v["not_evaluated"],
                "size_ratio_wh": "" if v["size_ratio"] is None else " ".join(map(str, v["size_ratio"])),
            })
        candidates_json[image_id] = {
            "coordinate": "original image pixel [x_min, y_min, x_max, y_max] (cells_original.json)",
            "fields": {f: {"roi_generated": res[f]["roi_generated"], "candidates": res[f]["candidates"],
                           "max_coverage": res[f]["coverage"], "best_cell_id": res[f]["best_cell_id"]}
                       for f in FIELDS if res[f]["gt_state"] != "excluded"},
        }

    deliver = ("image_id", "target_fields", "detected_fields", "roi_coverage", "failure_reason")
    (out_dir / "summary.json").write_text(json.dumps([{k: s[k] for k in deliver} for s in summary],
                                                     ensure_ascii=False, indent=2), encoding="utf-8")
    _write_csv(out_dir / "summary.csv", summary)
    _write_csv(out_dir / "roi_coverage_fields.csv", details)
    (out_dir / "roi_candidates.json").write_text(json.dumps(candidates_json, ensure_ascii=False, indent=2),
                                                 encoding="utf-8")
    overall = write_overall(out_dir, split, summary, details)
    print_result(split, summary, overall)
    return 0


def _block(details, image_ids=None, sec=None):
    ev = [d for d in details if d["gt_state"] == "eval" and (image_ids is None or d["image_id"] in image_ids)]
    cov = [d["coverage"] for d in ev]
    fails = {k: sum(d["failure_reason"] == k for d in ev) for k in FAIL_ORDER}
    out = {"evaluable_fields": len(ev), "covered_fields": sum(d["covered"] is True for d in ev),
           "covered_rate": _rate(sum(d["covered"] is True for d in ev), len(ev)),
           "mean_coverage": round(sum(cov) / len(cov), 4) if cov else None,
           "roi_generated_fields": sum(d["roi_generated"] is True for d in ev),
           "failure_counts": {k: v for k, v in fails.items() if v}}
    if sec is not None:
        t = [v for k, v in sec.items() if v is not None and (image_ids is None or k in image_ids)]
        out["structure_sec_per_image"] = round(sum(t) / len(t), 3) if t else None
    return out


def _process_sec(out_dir, summary):
    """report.json 의 process_sec (Task_0930 구조 복원 시간). 필드 후보 선택·OCR 은 포함하지 않는다."""
    sec = {}
    for s in summary:
        p = out_dir / s["image_id"] / "report.json"
        sec[s["image_id"]] = _read_json(p).get("process_sec") if p.exists() else None
    return sec


def write_overall(out_dir, split, summary, details):
    sec = _process_sec(out_dir, summary)
    groups, sources = {}, {}
    for s in summary:
        key = "common" if s["image_id"].startswith("common_") else "new"
        groups.setdefault(key, set()).add(s["image_id"])
        sources.setdefault(s["image_id"].rsplit("_", 1)[0], set()).add(s["image_id"])
    conds = {}
    for s in summary:
        conds.setdefault(s["condition"] or "unknown", set()).add(s["image_id"])
    not_eval = {}
    for d in details:
        if d["not_evaluated"]:
            not_eval[d["not_evaluated"]] = not_eval.get(d["not_evaluated"], 0) + 1
    frozen = _read_json(FROZEN) if FROZEN.exists() else {}
    overall = {
        "dataset": split, "pipeline": "P3 bang Detected ROI", "run_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "command": f"python p3_detected_roi_coverage.py --dataset {split}",
        "rule": {"coverage": "Area(GT ∩ ROI) / Area(GT)", "covered_threshold": COVERED_THRESHOLD,
                 "multi_candidate": "max over candidates", "no_roi": 0.0,
                 "excluded_status": sorted(EXCLUDED_STATUS), "bbox_null": "not evaluated",
                 "roi_coordinate": "original (cells_original.json)",
                 "candidate_min_overlap": CAND_MIN_OVERLAP, "max_candidates": MAX_CANDIDATES},
        "images": len(summary),
        "all": _block(details, sec=sec),
        "by_set": {k: {"images": len(v), **_block(details, v, sec)} for k, v in sorted(groups.items())},
        "by_source": {k: {"images": len(v), **_block(details, v, sec)} for k, v in sorted(sources.items())},
        "by_condition": {k: {"images": len(v), **_block(details, v, sec)} for k, v in sorted(conds.items())},
        "timing_note": "structure_sec_per_image = report.json process_sec 평균 (Task_0930 구조 복원만, "
                       "필드 후보 선택·OCR 제외, 캐시 없음)",
        "not_evaluated_fields": not_eval,
        "frozen_commit": frozen.get("git", {}).get("commit"),
        "script_sha256": _sha256(Path(__file__)),
        "dataset_sha256": {n: _sha256(EVAL_DIR / split / n) for n in ("manifest.csv", "field_gt.json")
                           if (EVAL_DIR / split / n).exists()},
    }
    (out_dir / "roi_coverage_overall.json").write_text(json.dumps(overall, ensure_ascii=False, indent=2),
                                                       encoding="utf-8")
    return overall


def print_result(split, summary, overall):
    line = "=" * 92
    print(f"\n{line}\n P3 Detected ROI Coverage — {split} (Covered >= {COVERED_THRESHOLD:.2f}, 후보 중 max)\n{line}")
    print(f"{'image_id':<12}{'cond':<13}{'covered':>9}  {'mean cov':>9}  failure_reason / not_evaluated")
    print("-" * 92)
    for s in summary:
        cov = "-" if s["roi_coverage"] is None else f"{s['roi_coverage']:.3f}"
        note = s["failure_reason"] or ("-" if not s["not_evaluated"] else f"(미평가 {s['not_evaluated']})")
        print(f"{s['image_id']:<12}{s['condition']:<13}{s['detected_fields']:>4}/{s['target_fields']:<4}  {cov:>9}  {note}")
    print("-" * 92)
    blocks = ([("전체", overall["all"])] + list(overall["by_set"].items())
              + [(f"  {k}", v) for k, v in overall["by_source"].items() if k != "common"])
    for name, b in blocks:
        mc = "-" if b["mean_coverage"] is None else f"{b['mean_coverage']:.3f}"
        cr = "-" if b["covered_rate"] is None else f"{b['covered_rate']:.1%}"
        print(f"{name:<8} Covered {b['covered_fields']}/{b['evaluable_fields']} ({cr}) | 평균 Coverage {mc}"
              f" | ROI 생성 {b['roi_generated_fields']} | {b['structure_sec_per_image']}s/img"
              f" | 실패 {b['failure_counts']}")
    if overall["not_evaluated_fields"]:
        print(f"분모 제외/미평가: {overall['not_evaluated_fields']}")
    print(line)
    print(f"결과: output/eval_v1/{split}/summary.csv, summary.json, roi_coverage_fields.csv, "
          f"roi_candidates.json, roi_coverage_overall.json")


def main():
    ap = argparse.ArgumentParser(description="P3 Detected ROI Coverage (bang_)")
    ap.add_argument("--dataset", choices=["development", "holdout_test"], default="development")
    return run(ap.parse_args().dataset)


if __name__ == "__main__":
    sys.exit(main())
