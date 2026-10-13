"""
공통 10장(tail 브랜치 sample_data_jpg/sample_1~10.JPG) 일괄 실행

검출 알고리즘은 Task_0930.py 를 그대로 쓰고(PARAMS 변경 없음), 이 파일은
  10장 순회 → Task_0930.run_batch() → 이미지별 결과 저장 → 전달용 요약 정리
만 담당한다.

실행 (프로젝트 폴더에서)
  python Task_10_Renewal.py
  → 10장 실행 → 결과 저장 → tail 전달 파일 생성(tail_roi.py) → 담당 조건별 최종 결과 출력

입력  data/common10/sample_1~10.JPG   (tail 브랜치 sample_data_jpg 와 같은 파일)
출력  output/common10/
  <이미지명>/cells_original.json   최종 셀, 원본 좌표 (EXIF 회전 적용 후, 3024x4032)
  <이미지명>/cells.json            최종 셀, 보정본 좌표 (<이미지명>_aligned.png 기준)
  <이미지명>/report.json           status(ok/check/grid_fail), 실패 사례, 파라미터, 처리 시간
  <이미지명>/<이미지명>_aligned.png  보정본 이미지 (용량이 커서 git 에는 올리지 않음, 재실행하면 동일하게 생성)
  manifest.json                    10장 status·좌표 파일·좌표 변환 행렬 한눈에 보기
  summary.csv / failure_cases.csv  run_batch 기본 요약
  _preview/<이미지명>_final.jpg     3_final.png 축소본 (사례 확인용)
"""
import json
import re
from pathlib import Path

import cv2
import numpy as np

import Task_0930 as t

ROOT = Path(__file__).resolve().parent
INPUT_DIR = ROOT / "data" / "common10"
OUT_DIR = ROOT / "output" / "common10"
PREVIEW_HEIGHT = 1600


def _natural_key(name):
    """sample_2 가 sample_10 보다 앞에 오도록 숫자 기준 정렬"""
    return [int(s) if s.isdigit() else s for s in re.split(r"(\d+)", name)]


def _save_preview(folder, stem):
    src = folder / "vis" / "3_final.png"
    if not src.exists():
        return None
    img = cv2.imdecode(np.fromfile(str(src), dtype=np.uint8), cv2.IMREAD_COLOR)
    f = PREVIEW_HEIGHT / img.shape[0]
    small = cv2.resize(img, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
    dst = OUT_DIR / "_preview" / f"{stem}_final.jpg"
    dst.parent.mkdir(parents=True, exist_ok=True)
    ok, buf = cv2.imencode(".jpg", small, [cv2.IMWRITE_JPEG_QUALITY, 85])
    buf.tofile(str(dst))
    return dst.relative_to(OUT_DIR).as_posix()


def build_manifest(summary):
    """이미지별 status 와 좌표계 정보를 한 파일로 정리 (받는 쪽이 좌표계를 헷갈리지 않도록)"""
    items = []
    for s in sorted(summary, key=lambda x: _natural_key(x["image"])):
        folder = OUT_DIR / s["folder"]
        entry = {"source_image": s["image"], "folder": s["folder"], "status": s["status"]}
        if s["status"] == "error":
            entry["message"] = s.get("message")
            items.append(entry)
            continue
        r = json.loads((folder / "report.json").read_text(encoding="utf-8"))
        entry.update({
            "tables": r["counts"]["tables"],
            "grid": [tb["grid"] for tb in r["tables"]],
            "cells": r["counts"]["cells"],
            "merged": r["counts"]["merged"],
            "failure_counts": {k: r["counts"][k] for k in t.FAIL_LABEL if r["counts"].get(k)},
            "original": {
                "cells": f"{s['folder']}/cells_original.json",
                "image": s["image"],
                "size": r["source_size"],
                "note": "EXIF 회전 적용 후 원본 이미지 좌표",
            },
            "aligned": {
                "cells": f"{s['folder']}/cells.json",
                "image": f"{s['folder']}/{r['image']}",
                "size": r["image_size"],
                "rotation_deg": r["rotation_deg"],
                "affine_original_to_aligned": r["deskew"]["affine"],
                "note": "기울기 보정본 좌표 (aligned 이미지에서 img[y1:y2, x1:x2] 로 자름)",
            },
            "report": f"{s['folder']}/report.json",
            "preview": _save_preview(folder, s["folder"]),
        })
        items.append(entry)

    manifest = {
        "method": t.METHOD,
        "input": "tail 브랜치 sample_data_jpg/sample_1~10.JPG",
        "params": t.PARAMS,
        "status_count": {k: sum(i["status"] == k for i in items) for k in ("ok", "check", "grid_fail", "error")},
        "images": items,
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def _case_titles(doc, prefix):
    """docs 의 '공통 10장' 절에서 사례 제목(## S5. ...)만 뽑는다"""
    path = ROOT / "docs" / doc
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8").split("# 공통 10장", 1)
    if len(text) < 2:
        return []
    return [line[3:].strip() for line in text[1].splitlines() if line.startswith(f"## {prefix}")]


def print_final_check(manifest, n_input):
    """담당 조건(issue/assignment_bang_opencv_cell_roi.md)별 최종 결과 출력"""
    images = manifest["images"]
    done = [i for i in images if i["status"] != "error"]
    n = len(images)

    def has(i, key):
        return (OUT_DIR / i[key]["cells"]).exists() if key in i else False

    n_orig = sum(has(i, "original") for i in done)
    n_cells = sum(has(i, "aligned") for i in done)
    n_report = sum((OUT_DIR / i["report"]).exists() for i in done)
    n_aligned = sum((OUT_DIR / i["aligned"]["image"]).exists() for i in done)
    sc = manifest["status_count"]
    missing_table = [i["source_image"] for i in done if i["tables"] < 2]
    succ, fail = _case_titles("02_success_cases.md", "S"), _case_titles("03_failure_cases.md", "F")

    roi_path = OUT_DIR / "handoff_tail" / "detected_roi_cells.json"
    roi = json.loads(roi_path.read_text(encoding="utf-8")) if roi_path.exists() else {}
    roi_used = {k: len(v["fields"]) for k, v in roi.items()}
    spec = (ROOT / "docs" / "06_handoff_B_io_spec.md")
    b_ok = spec.exists() and "공통 10장" in spec.read_text(encoding="utf-8")

    def mark(ok):
        return "[완료]" if ok else "[미완]"

    line = "=" * 78
    print(f"\n{line}\n 최종 결과 — 담당 조건별 확인\n{line}")
    print(f"{mark(n == n_input == 10 and sc['error'] == 0)} 1. 공통 10장 run_batch() 실행      : 입력 {n_input}장 → 처리 {n}장 (error {sc['error']})")
    print(f"{mark(n_orig == len(done) == 10)} 2. 이미지별 cells_original.json   : {n_orig}/10")
    print(f"{mark(n_cells == n_report == len(done))} 3. cells.json / report.json / aligned : {n_cells}/10, {n_report}/10, {n_aligned}/10")
    print(f"{mark(True)} 4. 원본 / 보정본 좌표 구분          : 아래 표 (원본 크기 vs 보정본 크기, 회전 각도)")
    print(f"{mark(True)} 5. 실패 상태 기록                  : ok {sc['ok']} / check {sc['check']} / grid_fail {sc['grid_fail']} / error {sc['error']}")
    print(f"         표 누락(tables < 2, status 는 check): {', '.join(missing_table) or '없음'}")
    print(f"{mark(len(succ) >= 3 and len(fail) >= 3)} 6. 대표 성공 / 실패 사례           : 성공 {len(succ)}개, 실패 {len(fail)}개")
    for x in succ:
        print(f"         성공 {x}")
    for x in fail:
        print(f"         실패 {x}")
    print(f"{mark(bool(roi))} 7. tail 전달 (Detected ROI OCR)    : 필드 {sum(roi_used.values())}/{len(roi) * 6} 전달"
          f" → {roi_path.relative_to(ROOT).as_posix()}")
    print(f"{mark(b_ok)} 8. B 전달 (End-to-End 입출력 규격)  : docs/06_handoff_B_io_spec.md 10절 + output/common10/manifest.json")

    print(f"\n{'이미지':<14}{'status':<11}{'표':>3}{'셀':>5}{'merged':>8}{'회전°':>8}"
          f"{'원본 크기':>13}{'보정본 크기':>14}{'tail 필드':>10}")
    print("-" * 78)
    for i in images:
        if i["status"] == "error":
            print(f"{i['source_image']:<14}{'error':<11}{i.get('message', '')}")
            continue
        o, a = i["original"]["size"], i["aligned"]["size"]
        orig_size, aligned_size = f"{o[0]}x{o[1]}", f"{a[0]}x{a[1]}"
        used = f"{roi_used.get(i['source_image'], 0)}/6"
        print(f"{i['source_image']:<14}{i['status']:<11}{i['tables']:>3}{i['cells']:>5}{i['merged']:>8}"
              f"{i['aligned']['rotation_deg']:>8.2f}{orig_size:>13}{aligned_size:>14}{used:>10}")
    print(line)
    print("좌표: cells_original.json = 원본(EXIF 회전 적용 후) / cells.json = 보정본(<이미지명>_aligned.png)")
    print(f"결과 폴더: {OUT_DIR.relative_to(ROOT).as_posix()}/  (상세: docs/07_common10_results.md)")


def main():
    paths = [q for q in INPUT_DIR.iterdir() if q.suffix.lower() in t.IMG_EXTS] if INPUT_DIR.is_dir() else []
    if len(paths) != 10:
        print(f"[주의] {INPUT_DIR} 이미지 {len(paths)}장 (공통 데이터는 10장)")
    summary = t.run_batch(INPUT_DIR, out_dir=OUT_DIR, params=None, save_roi=False)
    if not summary:
        return
    m = build_manifest(summary)
    print(f"manifest: {OUT_DIR / 'manifest.json'} | status {m['status_count']}\n")

    import tail_roi
    tail_roi.main()

    print_final_check(m, len(paths))


if __name__ == "__main__":
    main()
