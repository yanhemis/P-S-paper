"""
공통 10장 검출 셀 → tail 실험 C(Detected ROI OCR) 입력 형식 변환

tail 규격 (tail 브랜치 docs/ocr_io_spec.md 1절)
  {"sample_1.JPG": {"fields": {"address": {"quad": [[x,y] x4]}, ...}}}
  좌표 = EXIF 회전 적용 후 원본 이미지 좌표, quad 순서 = 좌상 → 우상 → 우하 → 좌하

필드 ↔ 셀 대응
  Anchor 규칙은 이 작업 범위가 아니므로, 필드마다 tail GT ROI(data/common10/tail_gt_roi.json)를
  가장 많이 덮는 검출 셀을 고른다 (GT 기반 셀 선택). 즉 "필드 위치는 알려줬을 때, 검출된 셀 경계로
  잘랐을 때의 OCR 성능"을 보는 입력이다. 다음 경우는 그 필드를 빼서 평가에서 실패로 처리되게 한다.
    - GT ROI 를 MIN_COVER 이상 덮는 셀이 없음 (표/행을 못 찾음)
    - 덮는 셀의 높이가 GT ROI 높이의 MAX_HEIGHT_RATIO 배 초과 (여러 행이 합쳐진 과다 병합 셀)

quad 는 보정본(cells.json) bbox 의 네 꼭짓점을 원본 좌표로 정확히 되돌린 것이다
(cells_original.json 의 bbox 는 중심만 되돌린 축 정렬 박스라 회전량만큼 오차가 있다).

실행
  python tail_roi.py
출력
  output/common10/handoff_tail/detected_roi_cells.json   tail roi_ocr.py 입력
  output/common10/handoff_tail/field_cell_match.csv        필드별 선택 셀 id, GT 덮는 비율, 높이 비, 제외 사유
"""
import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
RESULT_DIR = ROOT / "output" / "common10"
GT_ROI = ROOT / "data" / "common10" / "tail_gt_roi.json"
OUT_DIR = RESULT_DIR / "handoff_tail"
FIELDS = ["address", "deposit_num", "deposit_kor", "down_payment", "lessor_name", "lessee_name"]
MIN_COVER = 0.5          # GT ROI 면적의 50% 이상을 덮는 셀만 인정
MAX_HEIGHT_RATIO = 2.0   # 셀 높이가 GT ROI 높이의 2배를 넘으면 여러 행이 합쳐진 셀로 보고 제외


def aligned_to_original_quad(bbox, affine):
    x1, y1, x2, y2 = bbox
    corners = np.array([[x1, y1, 1], [x2, y1, 1], [x2, y2, 1], [x1, y2, 1]], dtype=float)
    if not affine:
        return corners[:, :2].astype(int).tolist()
    Ai = np.linalg.inv(np.vstack([np.array(affine), [0, 0, 1]]))
    return [[int(round(x)), int(round(y))] for x, y, _ in (Ai @ corners.T).T]


def _area(b):
    return max(0, b[2] - b[0]) * max(0, b[3] - b[1])


def _inter(a, b):
    return _area([max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])])


def main():
    manifest = json.loads((RESULT_DIR / "manifest.json").read_text(encoding="utf-8"))
    gt = json.loads(GT_ROI.read_text(encoding="utf-8"))
    out, rows = {}, []

    for item in manifest["images"]:
        name = item["source_image"]
        fields = {}
        if item["status"] != "error":
            cells = json.loads((RESULT_DIR / item["aligned"]["cells"]).read_text(encoding="utf-8"))["cells"]
            affine = item["aligned"]["affine_original_to_aligned"]
            quads = {c["id"]: aligned_to_original_quad(c["bbox"], affine) for c in cells}
            boxes = {k: [min(x for x, _ in q), min(y for _, y in q), max(x for x, _ in q), max(y for _, y in q)]
                     for k, q in quads.items()}
        else:
            cells, quads, boxes = [], {}, {}

        for f in FIELDS:
            g = gt.get(name, {}).get("fields", {}).get(f)
            if g is None:
                continue
            gb = g["bbox"]
            best, cover, iou = None, 0.0, 0.0
            for cid, b in boxes.items():
                inter = _inter(gb, b)
                c = inter / _area(gb) if _area(gb) else 0.0
                if c > cover:
                    best, cover = cid, c
                    iou = inter / (_area(gb) + _area(b) - inter)
            h_ratio = (boxes[best][3] - boxes[best][1]) / max(1, gb[3] - gb[1]) if best is not None else 0.0
            if best is None or cover < MIN_COVER:
                reason = "no_cell"
            elif h_ratio > MAX_HEIGHT_RATIO:
                reason = "over_merged_cell"
            else:
                reason = ""
                fields[f] = {"quad": quads[best], "cell_id": best}
            rows.append({"image": name, "status": item["status"], "field": f,
                         "cell_id": best if best is not None else "", "gt_cover": round(cover, 3),
                         "height_ratio": round(h_ratio, 2), "iou_vs_gt": round(iou, 3),
                         "used": not reason, "reason": reason})

        out[name] = {"source": "bang_ opencv_grid_merge cells.json (GT ROI 기반 셀 선택)", "fields": fields}

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "detected_roi_cells.json").write_text(json.dumps(out, ensure_ascii=False, indent=2),
                                                     encoding="utf-8")
    with open(OUT_DIR / "field_cell_match.csv", "w", newline="", encoding="utf-8-sig") as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    used = sum(r["used"] for r in rows)
    print(f"필드 {len(rows)}개 중 셀 매칭 {used}개 (GT 덮는 비율 >= {MIN_COVER}, 높이 비 <= {MAX_HEIGHT_RATIO})")
    for name in out:
        print(f"  {name:<14} {len(out[name]['fields'])}/{sum(r['image'] == name for r in rows)}")
    print(f"저장: {OUT_DIR}")


if __name__ == "__main__":
    main()
