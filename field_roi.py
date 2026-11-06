"""
핵심 5필드 Detected ROI + 실패 유형 분류 (05_current_team_tasks_20261101.md 2절, bang_ 작업)

검출된 셀(cells.json)에서 핵심 5필드가 들어가는 셀을 찾아 원본 좌표 ROI 로 전달한다.
셀 검출 알고리즘(Task_0930.py)은 그대로 쓰고, 이 파일은 '필드 → 셀' 대응과 실패 기록만 담당한다.

필드 → 셀 대응 (GT 없이 동작)
  기준 이미지(공통 10장 중 status ok 인 sample_1)에서 필드 셀이 표 안의 어느 상대 위치에 있는지 기록해 두고,
  새 이미지에서는 위치가 같은 표(페이지 세로 위치로 매칭)의 같은 상대 위치에 있는 셀을 고른다.
  같은 양식의 계약서라는 전제이며, 글자를 읽는 Anchor 규칙은 쓰지 않는다.

실패 유형 (필드 단위, 03 문서 기준)
  TABLE_MISSING     필드가 있어야 할 표를 못 찾았거나, 그 위치에 셀이 없음
  ROW_MERGE         셀 높이가 기대 크기의 MERGE_RATIO 배 초과 (여러 행이 합쳐짐)
  COLUMN_MERGE      셀 폭이 기대 크기의 MERGE_RATIO 배 초과 (여러 열이 합쳐짐)
  CELL_MERGE        높이·폭 모두 초과 (행과 열이 같이 합쳐진 덩어리)
  WRONG_MAPPING     GT bbox 가 있을 때: 고른 셀은 GT 를 못 덮는데, 다른 셀이 GT 를 덮음 (대응 오류)
  COORDINATE_ERROR  GT bbox 가 있을 때: GT 를 제대로 덮는 셀이 없음 (경계 어긋남/분할)
  RUN_ERROR         파이프라인 실행 자체가 실패 (성능 실패와 구분하기 위한 기록)
  WRONG_MAPPING / COORDINATE_ERROR 는 GT bbox 가 없으면(null) 판정하지 않는다.

평가 대상
  GT 가 status=not_present 인 필드(원본 문서에 값이 없음)는 분모에서 빼고 ROI 도 만들지 않는다.

좌표
  ROI 는 모두 원본 이미지 좌표 (EXIF 회전 적용 후). quad = 보정본 bbox 네 꼭짓점을 원본으로 정확히 되돌린 것.
  aligned(보정본) 좌표는 cells.json 에만 있고, 이 파일의 출력에는 섞지 않는다.
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent

FIELDS = ["address", "deposit", "contract_amount", "lessor_name", "lessee_name"]

# 기준 이미지와 필드별 셀 id (공통 10장 sample_1, status ok — tail GT ROI 와 대조해 확인한 셀)
REFERENCE_DIR = ROOT / "output" / "common10" / "sample_1"
REFERENCE_CELLS = {"address": 2, "deposit": 23, "contract_amount": 25, "lessor_name": 41, "lessee_name": 58}

TABLE_MATCH_TOL = 0.15   # 표 세로 중심 위치(페이지 높이 대비)가 기준과 이 이내면 같은 표로 본다
MERGE_RATIO = 1.8        # 셀 크기가 기대 크기의 이 배수를 넘으면 병합 오류
GT_MIN_COVER = 0.5       # GT bbox 면적의 50% 이상을 덮어야 맞는 셀

# tail GT ROI(공통 10장) 필드 키 → 03 문서 필드 키. deposit 은 숫자/한글 두 칸을 합친 영역
TAIL_KEY_MAP = {"address": ["address"], "deposit": ["deposit_num", "deposit_kor"],
                "contract_amount": ["down_payment"], "lessor_name": ["lessor_name"],
                "lessee_name": ["lessee_name"]}

# tail GT ROI 에는 값 유무 정보가 없어 공통 10장만 따로 적는다 (Dataset v1.0 common_007 = sample_7, not_present)
COMMON10_NOT_PRESENT = {"sample_7.JPG": {"contract_amount"}}


# ----------------------------------------------------------------
# 좌표 유틸
# ----------------------------------------------------------------
def aligned_to_original_quad(bbox, affine):
    x1, y1, x2, y2 = bbox
    corners = np.array([[x1, y1, 1], [x2, y1, 1], [x2, y2, 1], [x1, y2, 1]], dtype=float)
    if not affine:
        return corners[:, :2].astype(int).tolist()
    Ai = np.linalg.inv(np.vstack([np.array(affine), [0, 0, 1]]))
    return [[int(round(x)), int(round(y))] for x, y, _ in (Ai @ corners.T).T]


def quad_bbox(q):
    xs, ys = [p[0] for p in q], [p[1] for p in q]
    return [min(xs), min(ys), max(xs), max(ys)]


def _area(b):
    return max(0, b[2] - b[0]) * max(0, b[3] - b[1])


def _cover(gt, box):
    """GT bbox 면적 중 box 가 덮는 비율"""
    inter = _area([max(gt[0], box[0]), max(gt[1], box[1]), min(gt[2], box[2]), min(gt[3], box[3])])
    return inter / _area(gt) if _area(gt) else 0.0


def _load(folder):
    folder = Path(folder)
    cells = json.loads((folder / "cells.json").read_text(encoding="utf-8"))["cells"]
    report = json.loads((folder / "report.json").read_text(encoding="utf-8"))
    return cells, report


# ----------------------------------------------------------------
# 기준 구조
# ----------------------------------------------------------------
def load_reference():
    """기준 이미지에서 필드 셀의 (표 세로 위치, 표 안 상대 위치, 상대 크기)를 뽑는다"""
    cells, report = _load(REFERENCE_DIR)
    H = report["image_size"][1]
    tables = {tb["table"]: tb["bbox"] for tb in report["tables"]}
    ref = {}
    for f, cid in REFERENCE_CELLS.items():
        c = cells[cid]
        tx1, ty1, tx2, ty2 = tables[c["table"]]
        x1, y1, x2, y2 = c["bbox"]
        tw, th = tx2 - tx1, ty2 - ty1
        ref[f] = {
            "table_cy": (ty1 + ty2) / 2 / H,
            "rx": ((x1 + x2) / 2 - tx1) / tw, "ry": ((y1 + y2) / 2 - ty1) / th,
            "rw": (x2 - x1) / tw, "rh": (y2 - y1) / tw,   # 크기는 둘 다 표 폭 기준 (표 높이는 행 붕괴 시 같이 망가짐)
        }
    return {"image": report["source_image"], "cells": REFERENCE_CELLS, "fields": ref}


# ----------------------------------------------------------------
# GT
# ----------------------------------------------------------------
def load_gt_bboxes(path, image_key):
    """
    필드별 GT bbox(원본 좌표)를 읽는다. 없으면 None.
    - 04 문서 field_gt.json: {"<image_id>": {"fields": {"deposit": {"bbox": [..] 또는 null}}}}
    - tail gt_roi.json   : {"sample_1.JPG": {"fields": {"deposit_num": {"bbox": [..]}}}}
    """
    if not path or not Path(path).exists():
        return {}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    entry = data.get(image_key)
    if entry is None:
        return {}
    gf = entry.get("fields", {})
    out = {}
    for f in FIELDS:
        if f in gf:
            b = gf[f].get("bbox") if isinstance(gf[f], dict) else None
            out[f] = [int(v) for v in b] if b else None
        else:
            boxes = [gf[k]["bbox"] for k in TAIL_KEY_MAP[f] if k in gf and gf[k].get("bbox")]
            if boxes:
                out[f] = [min(b[0] for b in boxes), min(b[1] for b in boxes),
                          max(b[2] for b in boxes), max(b[3] for b in boxes)]
    return out


def load_not_present(path, image_key):
    """GT 가 status=not_present 로 표시한 필드 (원본 문서에 값이 없어 평가 대상이 아님)"""
    if not path or not Path(path).exists():
        return set()
    entry = json.loads(Path(path).read_text(encoding="utf-8")).get(image_key) or {}
    return {f for f, v in entry.get("fields", {}).items()
            if f in FIELDS and isinstance(v, dict) and v.get("status") == "not_present"}


# ----------------------------------------------------------------
# 한 이미지 처리
# ----------------------------------------------------------------
def map_fields(folder, ref, gt=None, excluded=()):
    """
    반환: {"fields": {field: {...}}, "targets": [...], "detected": [...], "failures": {field: reason}}
    각 필드: cell_id, quad/bbox(원본 좌표), failure(없으면 None), size_ratio, gt_cover
    excluded(not_present) 필드는 fields/targets 에 넣지 않는다.
    """
    gt = gt or {}
    targets = [f for f in FIELDS if f not in excluded]
    cells, report = _load(folder)
    H = report["image_size"][1]
    affine = report["deskew"]["affine"]
    tables = report["tables"]
    by_table = {}
    for c in cells:
        by_table.setdefault(c["table"], []).append(c)
    orig = {c["id"]: quad_bbox(aligned_to_original_quad(c["bbox"], affine)) for c in cells}

    out = {}
    for f in targets:
        r = ref["fields"][f]
        item = {"cell_id": None, "quad": None, "bbox": None, "failure": None,
                "size_ratio": None, "gt_cover": None}
        # 1) 같은 표 찾기 (페이지 세로 위치)
        cands = [(abs((tb["bbox"][1] + tb["bbox"][3]) / 2 / H - r["table_cy"]), tb) for tb in tables]
        cands = [x for x in cands if x[0] <= TABLE_MATCH_TOL]
        if not cands:
            item["failure"] = "TABLE_MISSING"
            out[f] = item
            continue
        tb = min(cands, key=lambda x: x[0])[1]
        tx1, ty1, tx2, ty2 = tb["bbox"]
        tw, th = tx2 - tx1, ty2 - ty1
        px, py = tx1 + r["rx"] * tw, ty1 + r["ry"] * th

        # 2) 그 위치의 셀
        hit = [c for c in by_table.get(tb["table"], [])
               if c["bbox"][0] <= px < c["bbox"][2] and c["bbox"][1] <= py < c["bbox"][3]]
        if not hit:
            item["failure"] = "TABLE_MISSING"
            out[f] = item
            continue
        c = hit[0]
        x1, y1, x2, y2 = c["bbox"]
        wr, hr = (x2 - x1) / (r["rw"] * tw), (y2 - y1) / (r["rh"] * tw)
        quad = aligned_to_original_quad(c["bbox"], affine)
        item.update({"cell_id": c["id"], "quad": quad, "bbox": quad_bbox(quad),
                     "size_ratio": [round(wr, 2), round(hr, 2)]})

        # 3) 병합 오류 (셀 크기 vs 기준 셀 크기)
        if hr > MERGE_RATIO and wr > MERGE_RATIO:
            item["failure"] = "CELL_MERGE"
        elif hr > MERGE_RATIO:
            item["failure"] = "ROW_MERGE"
        elif wr > MERGE_RATIO:
            item["failure"] = "COLUMN_MERGE"

        # 4) GT bbox 가 있으면 대응/좌표 확인
        g = gt.get(f)
        if g:
            cov = _cover(g, item["bbox"])
            item["gt_cover"] = round(cov, 3)
            if item["failure"] is None and cov < GT_MIN_COVER:
                best = max(orig, key=lambda k: _cover(g, orig[k]))
                item["failure"] = ("WRONG_MAPPING" if best != c["id"] and _cover(g, orig[best]) >= GT_MIN_COVER
                                   else "COORDINATE_ERROR")
        out[f] = item

    return {"fields": out, "targets": targets,
            "detected": [f for f in targets if out[f]["failure"] is None],
            "failures": {f: out[f]["failure"] for f in targets if out[f]["failure"]}}


def run_error_result(excluded=()):
    targets = [f for f in FIELDS if f not in excluded]
    item = {"cell_id": None, "quad": None, "bbox": None, "failure": "RUN_ERROR", "size_ratio": None, "gt_cover": None}
    return {"fields": {f: dict(item) for f in targets}, "targets": targets, "detected": [],
            "failures": {f: "RUN_ERROR" for f in targets}}
