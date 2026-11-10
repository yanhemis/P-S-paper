"""
bang_ 일괄 실행 — OpenCV 구조 복원 / Detected ROI 공급 (issue/05_current_team_tasks_20261101.md 2절)

검출 알고리즘은 Task_0930.py 를 그대로 쓰고(PARAMS 변경 없음), 이 파일은
  이미지 순회 → Task_0930 파이프라인 실행 → 이미지별 결과 저장 → 핵심 5필드 ROI·실패 유형 요약
만 담당한다. 필드 → 셀 대응과 실패 분류는 field_roi.py.

실행 (프로젝트 폴더에서, requirements_frozen.txt 환경)
  python Task_10_Renewal.py                          공통 10장: 기존 결과 보존, 5필드 요약만 다시 계산
  python Task_10_Renewal.py --check-repro            공통 10장: 임시 폴더에 다시 실행해 기존 결과와 같은지 비교
  python Task_10_Renewal.py --rerun                  공통 10장: 파이프라인까지 다시 실행 (기존 결과 덮어씀)
  python Task_10_Renewal.py --dataset development    Dataset v1.0 development 일괄 실행
  python Task_10_Renewal.py --freeze                 파라미터·코드 해시·환경·commit 을 frozen_params.json 에 고정
  python Task_10_Renewal.py --dataset holdout_test --check-package   실행 전 패키지 형식만 확인
  python Task_10_Renewal.py --dataset holdout_test   동결 확인 후 holdout_test 1회 실행 (재실행 거부)

입력
  공통 10장   data/common10/sample_1~10.JPG, GT ROI = data/common10/tail_gt_roi.json
  Dataset v1  data/eval_v1_packages/<split>/ (dataset-v1 브랜치) — manifest.csv, field_gt.json, images/
              manifest 의 filename 은 패키지 폴더 기준 상대 경로

출력 (데이터셋마다 같은 구조)
  <image_id>/cells_original.json   최종 셀, 원본 좌표 (EXIF 회전 적용 후) — 원본 GT 와 비교할 때 사용
  <image_id>/report.json           status(ok/check/grid_fail), 실패 사례, 파라미터, 처리 시간
  <image_id>/cells.json            최종 셀, 보정본 좌표 (<image_id>_aligned.png 기준)
  <image_id>/<image_id>_aligned.png  보정본. 보정이 없었던 이미지는 생성되지 않음 (cells.json 좌표 = 원본)
  <image_id>/fields.json           핵심 5필드 ROI (원본 좌표) + 필드별 실패 유형
  summary.json                     전달용 요약: image_id / target_fields / detected_fields / roi_coverage / failure_reason
                                   (공통 10장 = ROI 생성 비율, Dataset v1 = p3_detected_roi_coverage.py 의 GT BBox Coverage)
  roi_coverage_*.json/csv, roi_candidates.json, summary.csv   Dataset v1 P3 Coverage (p3_detected_roi_coverage.py)
  field_summary.csv                ROI 생성 기준 요약 + 문서 그룹·조건·status·GT bbox 수
  field_results.csv                필드 단위 상세 (셀 id, 크기 비, GT 덮는 비율, 실패 유형)
  detected_roi.json                5필드 ROI 모음 (tail roi_ocr.py 입력 형식, 원본 좌표 quad)
  run_info.json                    실행 명령, 파라미터, 코드 해시, 환경, git commit, 데이터셋 해시, 실행 시각
  공통 10장 결과 폴더 = output/common10/,  Dataset v1 = output/eval_v1/<split>/
"""
import argparse
import csv
import hashlib
import json
import platform
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import cv2
import numpy as np
import PIL

import Task_0930 as t
import field_roi as fr
import p3_detected_roi_coverage as p3

ROOT = Path(__file__).resolve().parent
COMMON_DIR = ROOT / "data" / "common10"
COMMON_OUT = ROOT / "output" / "common10"
COMMON_GT = COMMON_DIR / "tail_gt_roi.json"
EVAL_DIR = ROOT / "data" / "eval_v1_packages"
EVAL_OUT = ROOT / "output" / "eval_v1"
FROZEN = ROOT / "frozen_params.json"
CODE_FILES = ["Task_0930.py", "field_roi.py", "Task_10_Renewal.py", "p3_detected_roi_coverage.py"]
CELL_FILES = ["cells.json", "cells_original.json", "cells_primitive.json", "cells_primitive_original.json"]
FAIL_TYPES = ["TABLE_MISSING", "ROW_MERGE", "COLUMN_MERGE", "CELL_MERGE", "WRONG_MAPPING",
              "COORDINATE_ERROR", "RUN_ERROR"]
PREVIEW_HEIGHT = 1600


def _natural_key(name):
    """sample_2 가 sample_10 보다 앞에 오도록 숫자 기준 정렬"""
    return [int(s) if s.isdigit() else s for s in re.split(r"(\d+)", name)]


def _rel(p):
    return Path(p).relative_to(ROOT).as_posix()


def _write_csv(path, rows):
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


# ==============================================================
# 파라미터·코드 동결
# ==============================================================
def _sha256(path):
    """줄바꿈(CRLF/LF) 차이는 무시한 내용 해시 — git 체크아웃 설정이 달라도 같은 코드면 같은 값"""
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _git_commit():
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", *CODE_FILES], cwd=ROOT,
                               capture_output=True, text=True).stdout.strip()
        return {"commit": sha or None, "code_files_modified": bool(dirty)}
    except OSError:
        return {"commit": None, "code_files_modified": None}


def code_state():
    return {f: _sha256(ROOT / f) for f in CODE_FILES}


def env_state():
    """결과에 영향을 주는 라이브러리 버전 (numpy/pillow 버전이 달라도 셀 결과가 바뀐다 — docs/09 참고)"""
    return {"python": platform.python_version(), "opencv": cv2.__version__, "numpy": np.__version__,
            "pillow": PIL.__version__}


def freeze():
    git = _git_commit()
    if git["code_files_modified"] is not False:
        print("[중단] 코드 파일에 commit 되지 않은 변경이 있습니다. 먼저 commit 해야 동결 commit SHA 가 코드와 일치합니다.")
        return None
    data = {"frozen_at": time.strftime("%Y-%m-%d %H:%M:%S"), "method": t.METHOD, "params": t.PARAMS,
            "reference": {"image": "sample_1.JPG", "cells": fr.REFERENCE_CELLS},
            "field_roi": {"table_match_tol": fr.TABLE_MATCH_TOL, "merge_ratio": fr.MERGE_RATIO,
                          "gt_min_cover": fr.GT_MIN_COVER},
            "code_sha256": code_state(), "environment": env_state(), "git": git,
            "p3_coverage": {"covered_threshold": p3.COVERED_THRESHOLD, "candidate_min_overlap": p3.CAND_MIN_OVERLAP,
                            "max_candidates": p3.MAX_CANDIDATES},
            "commands": {"common10": "python Task_10_Renewal.py",
                         "development": "python Task_10_Renewal.py --dataset development",
                         "holdout_test": "python Task_10_Renewal.py --dataset holdout_test"}}
    FROZEN.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"고정 완료: {_rel(FROZEN)} (commit {git['commit']})")
    return data


def check_frozen():
    """반환: (파라미터 일치, 코드·환경 일치, 메시지 목록)"""
    if not FROZEN.exists():
        return False, False, ["frozen_params.json 없음 → python Task_10_Renewal.py --freeze"]
    fz = json.loads(FROZEN.read_text(encoding="utf-8"))
    params_ok = fz["params"] == json.loads(json.dumps(t.PARAMS))
    now = code_state()
    changed = [f for f in CODE_FILES if fz["code_sha256"].get(f) != now[f]]
    env_now = env_state()
    env_diff = [k for k in env_now if fz.get("environment", {}).get(k) != env_now[k]]
    msgs = [] if params_ok else ["PARAMS 가 frozen_params.json 과 다름"]
    msgs += [f"{f} 가 동결 이후 변경됨" for f in changed]
    msgs += [f"환경 {k} 가 동결 기준과 다름 (현재 {env_now[k]})" for k in env_diff]
    return params_ok, not changed and not env_diff, msgs


def _dataset_hashes(split):
    pkg = EVAL_DIR / split
    return {n: _sha256(pkg / n) for n in ("manifest.csv", "field_gt.json") if (pkg / n).exists()}


def write_run_info(out_dir, dataset, n_images):
    info = {"dataset": dataset, "run_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "command": "python Task_10_Renewal.py" + (" --rerun" if dataset == "common10" else f" --dataset {dataset}"),
            "images": n_images, "params": t.PARAMS, "code_sha256": code_state(), "environment": env_state(),
            "git": _git_commit()}
    if dataset != "common10":
        info["dataset_sha256"] = _dataset_hashes(dataset)
    (out_dir / "run_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")


def check_repro():
    """공통 10장을 임시 폴더에 다시 실행해 기존 결과와 비교. 반환: 전부 같으면 True"""
    with tempfile.TemporaryDirectory() as tmp:
        t.run_batch(COMMON_DIR, out_dir=Path(tmp), params=None, save_roi=False)
        same, diff = 0, []
        for q in sorted(COMMON_DIR.glob("sample_*.JPG"), key=lambda x: _natural_key(x.name)):
            for name in CELL_FILES:
                a = json.loads((COMMON_OUT / q.stem / name).read_text(encoding="utf-8"))
                b = json.loads((Path(tmp) / q.stem / name).read_text(encoding="utf-8"))
                if a == b:
                    same += 1
                else:
                    diff.append(f"{q.stem}/{name}")
    print(f"\n재현 확인: 셀 파일 {same + len(diff)}개 중 {same}개 동일 | 환경 {env_state()}")
    if diff:
        print("  다름: " + ", ".join(diff) + "\n  → requirements_frozen.txt 환경인지 확인")
    return not diff


# ==============================================================
# 파이프라인 실행
# ==============================================================
def _save_preview(folder, dst_dir, name):
    src = folder / "vis" / "3_final.png"
    if not src.exists():
        return None
    img = cv2.imdecode(np.fromfile(str(src), dtype=np.uint8), cv2.IMREAD_COLOR)
    f = PREVIEW_HEIGHT / img.shape[0]
    small = cv2.resize(img, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
    dst = dst_dir / "_preview" / f"{name}_final.jpg"
    dst.parent.mkdir(parents=True, exist_ok=True)
    ok, buf = cv2.imencode(".jpg", small, [cv2.IMWRITE_JPEG_QUALITY, 85])
    buf.tofile(str(dst))
    return dst


def build_common_manifest(summary):
    """공통 10장 manifest.json (이미지별 status 와 좌표계 정보)"""
    items = []
    for s in sorted(summary, key=lambda x: _natural_key(x["image"])):
        folder = COMMON_OUT / s["folder"]
        entry = {"source_image": s["image"], "folder": s["folder"], "status": s["status"]}
        if s["status"] == "error":
            entry["message"] = s.get("message")
            items.append(entry)
            continue
        r = json.loads((folder / "report.json").read_text(encoding="utf-8"))
        prev = _save_preview(folder, COMMON_OUT, s["folder"])
        entry.update({
            "tables": r["counts"]["tables"],
            "grid": [tb["grid"] for tb in r["tables"]],
            "cells": r["counts"]["cells"],
            "merged": r["counts"]["merged"],
            "failure_counts": {k: r["counts"][k] for k in t.FAIL_LABEL if r["counts"].get(k)},
            "original": {"cells": f"{s['folder']}/cells_original.json", "image": s["image"],
                         "size": r["source_size"], "note": "EXIF 회전 적용 후 원본 이미지 좌표"},
            "aligned": {"cells": f"{s['folder']}/cells.json", "image": f"{s['folder']}/{r['image']}",
                        "size": r["image_size"], "rotation_deg": r["rotation_deg"],
                        "affine_original_to_aligned": r["deskew"]["affine"],
                        "note": "기울기 보정본 좌표 (aligned 이미지에서 img[y1:y2, x1:x2] 로 자름)"},
            "report": f"{s['folder']}/report.json",
            "preview": prev.relative_to(COMMON_OUT).as_posix() if prev else None,
        })
        items.append(entry)
    manifest = {"method": t.METHOD, "input": "tail 브랜치 sample_data_jpg/sample_1~10.JPG", "params": t.PARAMS,
                "status_count": {k: sum(i["status"] == k for i in items) for k in ("ok", "check", "grid_fail", "error")},
                "images": items}
    (COMMON_OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def run_common10(rerun):
    """공통 10장은 최종 기준 결과로 보존한다. --rerun 일 때만 파이프라인을 다시 돌린다."""
    paths = sorted((q for q in COMMON_DIR.iterdir() if q.suffix.lower() in t.IMG_EXTS), key=lambda q: _natural_key(q.name))
    have = all((COMMON_OUT / q.stem / "cells_original.json").exists() for q in paths)
    if rerun or not have:
        summary = t.run_batch(COMMON_DIR, out_dir=COMMON_OUT, params=None, save_roi=False)
        build_common_manifest(summary)
        import tail_roi                       # tail 실험 C(E4) 입력도 같이 갱신
        tail_roi.main()
    else:
        print(f"공통 10장: 기존 결과 보존 ({_rel(COMMON_OUT)}) — 파이프라인 재실행 없이 5필드 요약만 계산")
    items = []
    for q in paths:
        r = json.loads((COMMON_OUT / q.stem / "report.json").read_text(encoding="utf-8"))
        items.append({"image_id": q.stem, "filename": q.name, "gt_key": q.name, "folder": COMMON_OUT / q.stem,
                      "status": r["status"], "tables": r["counts"]["tables"],
                      "document_group_id": "common10", "condition": "", "usable": "yes"})
    return items


def read_eval_manifest(split):
    path = EVAL_DIR / split / "manifest.csv"
    if not path.exists():
        return None
    with open(path, encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if r.get("split", "").strip() == split]
    return rows


def _group_overlap(rows):
    """holdout_test 의 document_group_id 가 development 와 겹치면 안 된다 (이미지가 아니라 그룹 단위 분리)"""
    dev = read_eval_manifest("development") or []
    return sorted({r["document_group_id"] for r in rows} & {r["document_group_id"] for r in dev})


def check_package(split):
    """
    실행 전 패키지 형식만 확인한다 (이미지·GT 값은 열어 보지 않음, 개수만 출력).
    holdout_test 는 1회만 실행되므로 경로·형식 오류로 실행을 낭비하지 않기 위함.
    """
    pkg = EVAL_DIR / split
    rows = read_eval_manifest(split)
    if rows is None:
        print(f"[대기] {_rel(pkg / 'manifest.csv')} 없음")
        return False
    need = ["image_id", "filename", "split", "document_group_id"]
    with open(pkg / "manifest.csv", encoding="utf-8-sig") as f:
        header = next(csv.reader(f), [])
    gt_path = pkg / "field_gt.json"
    gt = json.loads(gt_path.read_text(encoding="utf-8-sig")) if gt_path.exists() else {}
    ids = [r["image_id"].strip() for r in rows]
    checks = [
        ("manifest 필수 열", not [c for c in need if c not in header]),
        (f"split={split} 이미지 수 {len(rows)}", len(rows) > 0),
        ("image_id 중복 없음", len(ids) == len(set(ids))),
        ("이미지 파일 모두 있음", all((pkg / r["filename"].strip()).exists() for r in rows)),
        ("field_gt.json 있음", gt_path.exists()),
        ("GT 에 모든 image_id 있음", all(i in gt for i in ids)),
        ("GT 에 5필드 키 있음", all(set(fr.FIELDS) <= set((gt.get(i) or {}).get("fields", {})) for i in ids)),
    ]
    if split == "holdout_test":
        checks.append(("development 와 document_group_id 겹치지 않음", not _group_overlap(rows)))
        checks.append(("아직 실행 안 함", not (EVAL_OUT / split / "run_info.json").exists()))
        p_ok, c_ok, _ = check_frozen()
        checks.append(("코드·파라미터·환경 = 동결 기록", p_ok and c_ok))
    for name, ok in checks:
        print(f"  [{'OK' if ok else '확인 필요'}] {name}")
    ok = all(v for _, v in checks)
    print("→ 실행 가능" if ok else "→ 위 항목을 먼저 해결 (실행하지 않음)")
    return ok


def _rename_aligned(folder, image_id):
    """보정본 이름을 전달 형식 <image_id>_aligned.png 로 맞추고, 이를 가리키는 JSON 도 같이 고친다"""
    report_path = folder / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    old, new = report["image"], f"{image_id}_aligned.png"
    if not old.endswith("_aligned.png") or old == new:
        return
    (folder / old).replace(folder / new)
    for path in (report_path, folder / "cells.json", folder / "cells_primitive.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        data["image"] = new
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def run_eval(split):
    pkg = EVAL_DIR / split
    rows = read_eval_manifest(split)
    if rows is None:
        print(f"[대기] {_rel(pkg / 'manifest.csv')} 없음 — 가은 학우가 {split} 패키지를 전달한 뒤 실행")
        return None
    if not rows:
        print(f"[대기] manifest.csv 에 split={split} 이미지가 없음")
        return None
    out_dir = EVAL_OUT / split
    if split == "holdout_test":
        p_ok, c_ok, msgs = check_frozen()
        if not (p_ok and c_ok):
            print("[중단] holdout_test 는 동결된 설정으로만 실행합니다:\n  - " + "\n  - ".join(msgs))
            return None
        if (out_dir / "run_info.json").exists():
            print(f"[중단] holdout_test 는 이미 1회 실행됨 ({_rel(out_dir / 'run_info.json')}). 재실행하지 않습니다.")
            return None
        overlap = _group_overlap(rows)
        if overlap:
            print(f"[중단] development 와 겹치는 document_group_id: {overlap}")
            return None
    out_dir.mkdir(parents=True, exist_ok=True)

    items = []
    for row in rows:
        image_id, filename = row["image_id"].strip(), row["filename"].strip()
        path = pkg / filename
        meta = {"image_id": image_id, "filename": filename, "gt_key": image_id, "folder": out_dir / image_id,
                "document_group_id": row.get("document_group_id", ""), "condition": row.get("condition", ""),
                "usable": row.get("usable", "")}
        try:
            s = t.run_pipeline(path, out_dir, params=None, show=False, save_roi=False,
                               folder_name=image_id, verbose=False)
            _rename_aligned(out_dir / image_id, image_id)
            meta.update({"status": s["status"], "tables": s["tables"]})
            _save_preview(out_dir / image_id, out_dir, image_id)
            print(f"[{s['status']:>9}] {image_id} ({filename}): 표 {s['tables']}, 셀 {s['cells']} | {s['process_sec']:.2f}s")
        except Exception as e:
            meta.update({"status": "error", "tables": 0, "message": f"{type(e).__name__}: {e}"})
            print(f"[    error] {image_id} ({filename}): {meta['message']}")
        items.append(meta)
    write_run_info(out_dir, split, len(items))
    return items


# ==============================================================
# 5필드 ROI 요약
# ==============================================================
def _load_gt(it, gt_path):
    """반환: (필드별 GT bbox, not_present 필드). Dataset GT bbox 가 비어 있으면 같은 파일의 tail GT ROI 를 쓴다."""
    gt = fr.load_gt_bboxes(gt_path, it["gt_key"])
    if not any(gt.values()):
        gt = fr.load_gt_bboxes(COMMON_GT, Path(it["filename"]).name)
    excluded = fr.load_not_present(gt_path, it["gt_key"]) | fr.COMMON10_NOT_PRESENT.get(it["gt_key"], set())
    return gt, excluded


def write_field_outputs(items, out_dir, gt_path, write_summary=True):
    """write_summary=False (Dataset v1): summary.json 은 p3_detected_roi_coverage.py 가 GT BBox Coverage 로 쓴다."""
    ref = fr.load_reference()
    summary, details, roi = [], [], {}
    for it in items:
        gt, excluded = _load_gt(it, gt_path)
        res = (fr.run_error_result(excluded) if it["status"] == "error"
               else fr.map_fields(it["folder"], ref, gt, excluded))
        if it["status"] != "error":
            (it["folder"] / "fields.json").write_text(json.dumps(
                {"image_id": it["image_id"], "source_image": it["filename"],
                 "coordinate": "original (EXIF 회전 적용 후)", "reference": ref["image"],
                 "not_present": sorted(excluded), **res},
                ensure_ascii=False, indent=2), encoding="utf-8")
        covers = [v["gt_cover"] for v in res["fields"].values()     # 검출 성공한 필드만 (병합 셀은 GT 를 덮어도 제외)
                  if v["gt_cover"] is not None and v["failure"] is None]
        n_target = len(res["targets"])
        summary.append({
            "image_id": it["image_id"], "document_group_id": it["document_group_id"], "condition": it["condition"],
            "usable": it["usable"], "status": it["status"], "tables": it["tables"],
            "target_fields": n_target, "detected_fields": len(res["detected"]),
            "roi_coverage": round(len(res["detected"]) / n_target, 3),
            "detected_list": " ".join(res["detected"]),
            "failure_reason": "; ".join(f"{f}:{r}" for f, r in res["failures"].items()),
            "gt_bbox_fields": sum(bool(gt.get(f)) for f in res["targets"]),   # 0 이면 위치 정합 미검증
            "gt_cover_mean": round(sum(covers) / len(covers), 3) if covers else "",
        })
        for f, v in res["fields"].items():
            details.append({"image_id": it["image_id"], "field": f, "detected": v["failure"] is None,
                            "failure_reason": v["failure"] or "", "cell_id": "" if v["cell_id"] is None else v["cell_id"],
                            "bbox_original": "" if v["bbox"] is None else " ".join(map(str, v["bbox"])),
                            "size_ratio_wh": "" if v["size_ratio"] is None else " ".join(map(str, v["size_ratio"])),
                            "gt_cover": "" if v["gt_cover"] is None else v["gt_cover"]})
        roi[it["gt_key"]] = {"image_id": it["image_id"], "source_image": it["filename"],
                             "source": f"bang_ {t.METHOD} + field_roi (reference {ref['image']})",
                             "fields": {f: {"quad": v["quad"], "cell_id": v["cell_id"]}
                                        for f, v in res["fields"].items() if v["failure"] is None}}
    if write_summary:
        deliver = ("image_id", "target_fields", "detected_fields", "roi_coverage", "failure_reason")
        (out_dir / "summary.json").write_text(json.dumps([{k: s[k] for k in deliver} for s in summary],
                                                         ensure_ascii=False, indent=2), encoding="utf-8")
    _write_csv(out_dir / "field_summary.csv", summary)
    _write_csv(out_dir / "field_results.csv", details)
    (out_dir / "detected_roi.json").write_text(json.dumps(roi, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


# ==============================================================
# 최종 출력 — 담당 조건별 확인
# ==============================================================
def _common_preserved():
    try:
        out = subprocess.run(["git", "status", "--porcelain", "--", "output/common10"], cwd=ROOT,
                             capture_output=True, text=True).stdout
    except OSError:
        return None
    changed = [l for l in out.splitlines() if re.search(r"(cells_original|cells|cells_primitive\w*)\.json$", l)]
    return not changed


def _dataset_state(out_dir):
    if not (out_dir / "field_summary.csv").exists():
        return None
    with open(out_dir / "field_summary.csv", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    n_orig = sum((out_dir / r["image_id"] / "cells_original.json").exists() for r in rows)
    n_rep = sum((out_dir / r["image_id"] / "report.json").exists() for r in rows)
    fails = {k: 0 for k in FAIL_TYPES}
    for r in rows:
        for part in filter(None, r["failure_reason"].split("; ")):
            fails[part.split(":")[1]] += 1
    det = sum(int(r["detected_fields"]) for r in rows)
    tgt = sum(int(r["target_fields"]) for r in rows)
    ov = out_dir / "roi_coverage_overall.json"
    cov = json.loads(ov.read_text(encoding="utf-8"))["all"] if ov.exists() else None
    return {"rows": rows, "n": len(rows), "orig": n_orig, "report": n_rep, "fails": fails, "det": det, "tgt": tgt,
            "cov": cov}


def print_final(current, current_rows):
    line = "=" * 86
    print(f"\n{line}\n 최종 결과 — 담당 조건별 확인 (05_current_team_tasks_20261101.md 2절)\n{line}")
    states = {"common10": _dataset_state(COMMON_OUT),
              "development": _dataset_state(EVAL_OUT / "development"),
              "holdout_test": _dataset_state(EVAL_OUT / "holdout_test")}
    p_ok, c_ok, msgs = check_frozen()
    kept = _common_preserved()

    def mark(ok):
        return "[완료]" if ok is True else "[대기]" if ok is None else "[확인]"

    def ds(name):
        s = states[name]
        return "미실행 (데이터 대기)" if s is None else f"{s['n']}장"

    print(f"{mark(FROZEN.exists() and p_ok and c_ok)} 1. 파라미터·실행 명령 고정        : {_rel(FROZEN) if FROZEN.exists() else '없음'}"
          f" | PARAMS {'일치' if p_ok else '불일치'} | 코드·환경 {'동결 상태와 같음' if c_ok else '동결 상태와 다름'}")
    for m in msgs:
        print(f"         - {m}")
    print(f"{mark(kept)} 2. 공통 10장 최종 기준 결과 보존   : "
          + ("셀 결과 변경 없음 (git 기준)" if kept else "셀 결과가 바뀜 — git status 확인" if kept is False else "git 확인 불가"))
    print(f"{mark(True if states['development'] else None)} 3. development 동일 설정 batch    : {ds('development')}")
    parts = []
    for name, s in states.items():
        if s:
            parts.append(f"{name} {s['orig']}/{s['n']}, {s['report']}/{s['n']}")
    print(f"{mark(all(s['orig'] == s['report'] == s['n'] for s in states.values() if s))} 4. 이미지별 cells_original / report : "
          + " | ".join(parts))
    print(f"{mark(True)} 5. 원본 / aligned 좌표 분리        : cells_original.json·fields.json·detected_roi.json = 원본 좌표,"
          f" cells.json = aligned")
    parts = [f"{n} ROI 생성 {s['det']}/{s['tgt']}"
             + (f", Covered {s['cov']['covered_fields']}/{s['cov']['evaluable_fields']}" if s["cov"] else "")
             for n, s in states.items() if s]
    print(f"{mark(True)} 6. 5필드 ROI Coverage 전달         : " + " | ".join(parts) + "  → summary.json")
    for n, s in states.items():
        if s:
            print(f"{mark(True)} 7. 실패 유형 기록 ({n:<12})   : "
                  + ", ".join(f"{k} {v}" for k, v in s["fails"].items() if v or k != "RUN_ERROR"))
    hs = states["holdout_test"]
    print(f"{mark(True if hs else None)} 8. holdout_test 동결 후 1회 실행   : "
          + (f"완료 {hs['n']}장 ({_rel(EVAL_OUT / 'holdout_test' / 'run_info.json')})" if hs
             else "미실행 — development 확정 → --freeze → --dataset holdout_test"))

    out = COMMON_OUT if current == "common10" else EVAL_OUT / current
    print(f"\n[{current}] {'image_id':<12}{'status':<11}{'표':>3}  {'5필드':>6}  {'ROI cov':>8}  failure_reason")
    print("-" * 86)
    for r in current_rows:
        print(f"{'':<{len(current) + 3}}{r['image_id']:<12}{r['status']:<11}{r['tables']:>3}  "
              f"{r['detected_fields']:>2}/{r['target_fields']:<3}  {r['roi_coverage']:>8.0%}  {r['failure_reason'] or '-'}")
    print(line)
    print(f"결과 폴더: {_rel(out)}/  (summary.json, field_summary.csv, field_results.csv, detected_roi.json, <image_id>/)")


def main():
    ap = argparse.ArgumentParser(description="bang_ 구조 복원 / Detected ROI 일괄 실행")
    ap.add_argument("--dataset", choices=["common10", "development", "holdout_test"], default="common10")
    ap.add_argument("--rerun", action="store_true", help="공통 10장 파이프라인을 다시 실행")
    ap.add_argument("--check-repro", action="store_true", help="공통 10장을 임시 폴더에 다시 실행해 기존 결과와 비교")
    ap.add_argument("--freeze", action="store_true", help="파라미터·코드 해시·환경·commit 을 frozen_params.json 에 고정")
    ap.add_argument("--check-package", action="store_true",
                    help="--dataset 패키지 형식만 확인 (실행하지 않음, 이미지·GT 값은 열어 보지 않음)")
    args = ap.parse_args()

    if args.freeze:
        return 0 if freeze() else 1
    if args.check_package:
        return 0 if check_package(args.dataset) else 1
    if args.check_repro:
        return 0 if check_repro() else 1
    if args.dataset == "common10":
        items = run_common10(args.rerun)
        out_dir, gt_path = COMMON_OUT, COMMON_GT
    else:
        items = run_eval(args.dataset)
        out_dir, gt_path = EVAL_OUT / args.dataset, EVAL_DIR / args.dataset / "field_gt.json"
    if items is None:
        print_final(args.dataset, [])
        return
    if args.dataset == "common10" and args.rerun:
        write_run_info(out_dir, "common10", len(items))
    rows = write_field_outputs(items, out_dir, gt_path, write_summary=args.dataset == "common10")
    print_final(args.dataset, rows)
    if args.dataset != "common10":
        p3.run(args.dataset)          # GT BBox 기준 P3 ROI Coverage → summary.json


if __name__ == "__main__":
    sys.exit(main())
