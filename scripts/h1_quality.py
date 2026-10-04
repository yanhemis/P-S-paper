"""
H1 검증 - "Text bbox는 한국어 자체보다 이미지 품질의 영향을 더 크게 받는다"

양식에 인쇄된 글자(한글 약 1,700자)는 10장 모두 내용이 같다. 이 인쇄 글자의 재현율과 CER을 장별로
비교하면 글자 내용(한국어)을 고정한 채 이미지 품질의 영향만 볼 수 있다. 정답은 양식 PDF의 텍스트
레이어(pdftotext -bbox)에서 가져온다.

사용법:
    # 1) 호모그래피, 품질 지표, 전처리 이미지(CLAHE / 원근 보정) 생성
    python h1_quality.py prepare sample_data_jpg/sample_{1..10}.JPG

    # 2) 전처리 이미지 전체 OCR (ocr_baseline.py)
    python ocr_baseline.py results/h1/images/clahe/*.jpg --out-dir results/h1/ocr/clahe --no-vis
    python ocr_baseline.py results/h1/images/rectified/*.jpg --out-dir results/h1/ocr/rectified --no-vis

    # 3) 인쇄 글자 평가 (원본 / CLAHE는 촬영본 좌표, 원근 보정본은 양식 좌표)
    python h1_quality.py printed results original photo
    python h1_quality.py printed results/h1/ocr/clahe clahe photo
    python h1_quality.py printed results/h1/ocr/rectified rectified template

    # 4) 종합 표
    python h1_quality.py report

출력: results/h1/ (quality_metrics.json, printed_<variant>.json, summary.md)
"""

import sys
import json
import re
import subprocess
import html
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_gt_roi import (  # noqa: E402
    TEMPLATE_PATH, TEMPLATE_FIELDS, find_homography, local_homography,
)
from evaluate_fields import assign_full_ocr, levenshtein  # noqa: E402
from ocr_baseline import DET_LIMIT_SIDE_LEN  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
H1_DIR = ROOT / "results" / "h1"
FORM_PDF = ROOT / "contractForm" / "**부동산임대차계약서_양식.pdf"
WORDS_PATH = ROOT / "gt" / "template_words.json"
PT_TO_PX = 300 / 72  # gt/template.png 는 300dpi 렌더링

HANGUL = re.compile(r"[가-힣]")
# 인쇄 글자 평가: 위아래 여유를 작게 (인쇄 글자는 줄을 넘지 않음), 박스 통째 배정은 끔
LINE_PAD = 0.15
NO_WHOLE_BOX = 1.01


# ---------------------------------------------------------------- 인쇄 글자 정답

def template_words():
    if WORDS_PATH.exists():
        return json.loads(WORDS_PATH.read_text(encoding="utf-8"))
    out = subprocess.run(
        ["pdftotext", "-f", "1", "-l", "1", "-bbox", str(FORM_PDF), "-"],
        capture_output=True, text=True, check=True,
    ).stdout
    words = []
    for m in re.finditer(
        r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', out
    ):
        x1, y1, x2, y2 = (float(v) * PT_TO_PX for v in m.groups()[:4])
        words.append({"text": html.unescape(m.group(5)), "bbox": [round(x1), round(y1), round(x2), round(y2)]})
    WORDS_PATH.write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
    return words


# ---------------------------------------------------------------- 품질 지표

def quality_metrics(photo, H):
    """원근 보정한 문서(양식 좌표계)에서 품질 지표를 잰다. 모든 장이 같은 좌표계라 비교 가능."""
    tw, th = 2481, 3508
    rect = cv2.warpPerspective(photo, np.linalg.inv(H), (tw, th), borderValue=(255, 255, 255))
    gray = cv2.cvtColor(rect, cv2.COLOR_BGR2GRAY)
    inner = gray[100:th - 100, 100:tw - 100]  # 가장자리(보정 경계) 제외

    # 조명 불균일: 글자를 지운 배경 밝기(큰 커널 closing)의 변동계수
    bg = cv2.morphologyEx(inner, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (61, 61)))
    bg = cv2.GaussianBlur(bg, (0, 0), 25)

    # 기하: 양식 중심에서의 국소 배율(=유효 해상도), 상단 변 기울기, 좌우 변 길이 비(원근 왜곡)
    def proj(pts):
        return cv2.perspectiveTransform(np.float32(pts).reshape(-1, 1, 2), H).reshape(-1, 2)

    c = np.array([tw / 2, th / 2])
    p0, px, py = proj([c, c + [1, 0], c + [0, 1]])
    scale = float(np.sqrt(abs(np.cross(px - p0, py - p0))))
    tl, tr, br, bl = proj([[0, 0], [tw, 0], [tw, th], [0, th]])
    tilt = float(np.degrees(np.arctan2(tr[1] - tl[1], tr[0] - tl[0])))
    left, right = np.linalg.norm(bl - tl), np.linalg.norm(br - tr)
    top, bottom = np.linalg.norm(tr - tl), np.linalg.norm(br - bl)

    return rect, {
        "brightness": float(inner.mean()),
        "contrast_p95_p5": float(np.percentile(inner, 95) - np.percentile(inner, 5)),
        "sharpness_lap_var": float(cv2.Laplacian(inner, cv2.CV_64F).var()),
        "illum_nonuniformity_cv": float(bg.std() / bg.mean()),
        "effective_dpi": round(300 * scale, 1),
        "tilt_deg": round(tilt, 2),
        "keystone_ratio": round(float(max(left / right, right / left, top / bottom, bottom / top)), 3),
    }


def clahe(photo):
    lab = cv2.cvtColor(photo, cv2.COLOR_BGR2LAB)
    lab[:, :, 0] = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(16, 16)).apply(lab[:, :, 0])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def cmd_prepare(paths):
    template_words()
    template_gray = cv2.imread(str(TEMPLATE_PATH), cv2.IMREAD_GRAYSCALE)
    for sub in ["images/clahe", "images/rectified", "homography"]:
        (H1_DIR / sub).mkdir(parents=True, exist_ok=True)

    metrics_path = H1_DIR / "quality_metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
    rect_roi = {}
    for p in paths:
        path = Path(p).resolve()
        photo = cv2.imread(str(path))  # EXIF 회전 적용. 저장본은 회전이 반영된 픽셀이라 좌표가 그대로 맞음
        H, src, dst, n_good = find_homography(template_gray, cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY))
        reproj = np.linalg.norm(cv2.perspectiveTransform(src.reshape(-1, 1, 2), H).reshape(-1, 2) - dst, axis=1)
        np.savez(H1_DIR / "homography" / f"{path.stem}.npz", H=H, src=src, dst=dst)

        rect, m = quality_metrics(photo, H)
        m["homography_inliers"] = int(len(src))
        m["reproj_err_median_px"] = round(float(np.median(reproj)), 2)
        metrics[path.name] = m

        stem = path.stem
        cv2.imwrite(str(H1_DIR / "images" / "clahe" / f"{stem}.jpg"), clahe(photo), [cv2.IMWRITE_JPEG_QUALITY, 95])
        cv2.imwrite(str(H1_DIR / "images" / "rectified" / f"{stem}.jpg"), rect, [cv2.IMWRITE_JPEG_QUALITY, 95])
        # 원근 보정본의 필드 ROI = 양식 좌표 그대로
        rect_roi[path.name] = {  # gt_fields.json 과 같은 키 (OCR json은 stem 으로 찾음)
            "fields": {k: {"bbox": v} for k, v in TEMPLATE_FIELDS.items()},
        }
        print(f"[ok] {path.name}: " + ", ".join(f"{k}={v}" for k, v in m.items()))

    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    (H1_DIR / "gt_roi_rectified.json").write_text(json.dumps(rect_roi, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------- 인쇄 글자 평가

def template_lines():
    """인쇄 단어를 같은 줄(yMin이 거의 같은 것)끼리 묶는다.

    단어 단위로 평가하면 호모그래피 오차 몇 px와 글자 폭 균일 가정 때문에 단어 경계가 한두 글자씩
    밀려서, OCR이 맞게 읽어도 틀린 것으로 잡힌다. 줄 단위로 묶으면 경계 오차는 줄 양끝에서만 생긴다.
    """
    words = sorted(template_words(), key=lambda w: (w["bbox"][1], w["bbox"][0]))
    lines = []
    for w in words:
        if lines and abs(lines[-1]["bbox"][1] - w["bbox"][1]) <= 6:
            ln = lines[-1]
            ln["words"].append(w)
            b = ln["bbox"]
            ln["bbox"] = [min(b[0], w["bbox"][0]), min(b[1], w["bbox"][1]), max(b[2], w["bbox"][2]), max(b[3], w["bbox"][3])]
        else:
            lines.append({"words": [w], "bbox": list(w["bbox"])})
    for ln in lines:
        ln["words"].sort(key=lambda w: w["bbox"][0])
        ln["text"] = hangul_only("".join(w["text"] for w in ln["words"]))
    # 한 글자짜리 줄 = 표 왼쪽 세로쓰기 라벨(임/대/인, 공/인/중/개/사). 가로 줄 단위 배정이 안 되므로 제외
    return [ln for ln in lines if len(ln["text"]) >= 2]


def hangul_only(t):
    # 문장부호 변형(ㆍ/·, ․/.)과 빈칸에 손으로 쓴 숫자는 비교에서 뺀다 -> 인쇄된 한국어만 본다
    return "".join(HANGUL.findall(t))


def lcs_len(a, b):
    prev = [0] * (len(b) + 1)
    for ca in a:
        cur = [0]
        for j, cb in enumerate(b, 1):
            cur.append(prev[j - 1] + 1 if ca == cb else max(prev[j], cur[j - 1]))
        prev = cur
    return prev[-1]


def bigram_recall(gt_lines, items):
    """위치를 쓰지 않는 보조 지표: 페이지 전체의 인쇄 한글 2글자 묶음(줄 안에서) 중 OCR 결과에 나온 비율.

    종이가 휘거나 접혀 호모그래피가 국소적으로 틀린 장(#4 클립보드, #7 접힘)에서도 정렬 오차 없이 비교된다.
    순서를 보지 않으므로 줄 단위 재현율보다 관대하다.
    """
    from collections import Counter
    def grams(t):
        return Counter(t[i:i + 2] for i in range(len(t) - 1))
    g = Counter()
    for ln in gt_lines:
        g += grams(ln["text"])
    p = Counter()
    for it in items:
        p += grams(hangul_only(it["text"]))
    return sum(min(c, p[k]) for k, c in g.items()) / sum(g.values())


def cmd_printed(ocr_dir, variant, coord_mode):
    """인쇄된 한국어 줄 단위 평가.

    - char_recall: 정답 한글 중 순서대로 맞게 읽힌 비율 (LCS / 정답 길이). 같은 줄의 손글씨(예: 소재지 칸의
      주소)가 끼어들어도 감점되지 않아 주 지표로 쓴다.
    - char_cer: 편집 거리 / 정답 길이. 손글씨 한글이 끼어든 줄에서는 과대 추정됨 (참고용).
    - line_detect_rate: 한 글자라도 읽힌 줄의 비율.
    """
    lines = template_lines()
    out = {}
    for ocr_path in sorted(Path(ocr_dir).glob("sample_*_ocr.json")):
        stem = ocr_path.name.replace("_ocr.json", "")
        if not re.fullmatch(r"sample_\d+", stem):
            continue
        items = json.loads(ocr_path.read_text(encoding="utf-8"))["items"]
        if coord_mode == "photo":
            hz = np.load(H1_DIR / "homography" / f"{stem}.npz")
            H, src, dst = hz["H"], hz["src"], hz["dst"]

        n_chars = n_lcs = n_err = n_det = 0
        for ln in lines:
            x1, y1, x2, y2 = ln["bbox"]
            quad = np.float32([[x1, y1], [x2, y1], [x2, y2], [x1, y2]])
            if coord_mode == "photo":
                Hl, _ = local_homography(H, src, dst, ln["bbox"])
                quad = cv2.perspectiveTransform(quad.reshape(-1, 1, 2), Hl).reshape(-1, 2)
            pred, _ = assign_full_ocr(items, quad, pad_ratio=LINE_PAD, whole_box_ratio=NO_WHOLE_BOX)
            pred = hangul_only(pred)
            gt = ln["text"]
            n_chars += len(gt)
            n_lcs += lcs_len(gt, pred)
            n_err += levenshtein(pred, gt)
            n_det += bool(pred)
        out[stem] = {
            "lines": len(lines),
            "hangul_chars": n_chars,
            "char_recall": n_lcs / n_chars,
            "page_bigram_recall": bigram_recall(lines, items),
            "char_cer": n_err / n_chars,
            "line_detect_rate": n_det / len(lines),
        }
        print(f"[{variant}] {stem}: " + ", ".join(f"{k}={v:.3f}" if isinstance(v, float) else f"{k}={v}" for k, v in out[stem].items()))
    (H1_DIR / f"printed_{variant}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------- 종합

def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    return float(np.corrcoef(ra, rb)[0, 1])


def cmd_report():
    q = json.loads((H1_DIR / "quality_metrics.json").read_text(encoding="utf-8"))
    printed = {
        v: json.loads((H1_DIR / f"printed_{v}.json").read_text(encoding="utf-8"))
        for v in ["original", "clahe", "rectified"] if (H1_DIR / f"printed_{v}.json").exists()
    }
    gt_fields = json.loads((ROOT / "gt" / "gt_fields.json").read_text(encoding="utf-8"))

    def field_stats(path):
        """이미지별 손글씨 5필드 평균 CER, 전체 EM (Full OCR)."""
        if not Path(path).exists():
            return {}, None
        rows = [r for r in json.loads(Path(path).read_text(encoding="utf-8"))["rows"]
                if r["method"] == "Full OCR" and r["field"] != "deposit_kor"]
        per = {}
        for r in rows:
            per.setdefault(Path(r["image"]).stem, []).append(r["cer"])
        return {k: float(np.mean(v)) for k, v in per.items()}, (sum(r["exact_match"] for r in rows), len(rows))

    hw = {
        "original": field_stats(ROOT / "results" / "eval" / "field_results.json"),
        "clahe": field_stats(H1_DIR / "eval_clahe" / "field_results.json"),
        "rectified": field_stats(H1_DIR / "eval_rectified" / "field_results.json"),
    }

    stems = sorted({Path(k).stem for k in q}, key=lambda s: int(s.split("_")[1]))
    nan = float("nan")
    # 검출 입력 해상도: 검출 모델은 이미지 긴 변을 DET_LIMIT_SIDE_LEN(1536)으로 줄여서 본다.
    # 문서가 프레임에서 작을수록(멀리서 촬영) 검출 단계에서 글자가 더 작아진다.
    for s_ in stems:
        h, w = cv2.imread(str(ROOT / "sample_data_jpg" / f"{s_}.JPG"), cv2.IMREAD_REDUCED_GRAYSCALE_8).shape
        long_side = max(h, w) * 8
        q[f"{s_}.JPG"]["det_input_dpi"] = q[f"{s_}.JPG"]["effective_dpi"] * min(1.0, DET_LIMIT_SIDE_LEN / long_side)
    L = ["# H1 — 이미지 품질과 인쇄 글자 / 손글씨 인식\n"]
    L.append("- 인쇄 글자: 양식 PDF 텍스트 레이어의 한글(세로 라벨 제외 53줄, 1,325자). 10장 모두 내용이 같아서 이미지 품질만 다르다")
    L.append("- 인쇄 재현율: 줄 단위로 정답 한글 중 순서대로 맞게 읽힌 비율(LCS). 위치 무관 재현율: 페이지 전체 한글 2글자 묶음 중 OCR에 나온 비율(정렬 오차 영향 없음)")
    L.append("- 손글씨 CER: 5필드 평균 (Full OCR, `results/eval`)")
    L.append("- 품질 지표는 원근 보정한 문서(양식 좌표계, 300dpi 기준)에서 측정\n")

    L.append("## 1. 장별 품질 지표와 인식 결과 (원본)\n")
    L.append("| 이미지 | 세트 | 밝기 | 대비 | 선명도 | 조명 불균일 | 유효 dpi | 검출 입력 dpi | 기울기° | 원근비 | 인쇄 재현율 | 위치 무관 재현율 | 손글씨 CER |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for s_ in stems:
        m = q[f"{s_}.JPG"]
        pr = printed.get("original", {}).get(s_, {})
        L.append(
            f"| {s_} | #{gt_fields[f'{s_}.JPG']['set']} | {m['brightness']:.0f} | {m['contrast_p95_p5']:.0f} | "
            f"{m['sharpness_lap_var']:.0f} | {m['illum_nonuniformity_cv']:.3f} | {m['effective_dpi']:.0f} | "
            f"{m['det_input_dpi']:.0f} | {m['tilt_deg']:.1f} | {m['keystone_ratio']:.3f} | "
            f"{pr.get('char_recall', nan):.3f} | {pr.get('page_bigram_recall', nan):.3f} | "
            f"{hw['original'][0].get(s_, nan):.3f} |"
        )

    L.append("\n## 2. 품질 지표와 인식 결과의 순위 상관 (Spearman ρ, n=10)\n")
    L.append("n=10에서는 |ρ| ≥ 0.65 정도여야 우연이 아니라고 볼 수 있다(양측 p≈0.05). 방향과 크기만 참고한다. "
             "재현율은 높을수록 좋고 CER은 낮을수록 좋으므로 부호가 반대로 나온다.\n")
    L.append("| 품질 지표 | ρ(인쇄 재현율) | ρ(위치 무관 재현율) | ρ(손글씨 CER) |")
    L.append("|---|---|---|---|")
    po = printed.get("original", {})
    rec = [po.get(s_, {}).get("char_recall", nan) for s_ in stems]
    bg = [po.get(s_, {}).get("page_bigram_recall", nan) for s_ in stems]
    hc = [hw["original"][0].get(s_, nan) for s_ in stems]
    labels = {
        "brightness": "밝기", "contrast_p95_p5": "대비", "sharpness_lap_var": "선명도",
        "illum_nonuniformity_cv": "조명 불균일", "effective_dpi": "유효 dpi", "det_input_dpi": "검출 입력 dpi",
        "tilt_deg": "기울기 (절댓값)", "keystone_ratio": "원근비", "reproj_err_median_px": "정합 오차",
    }
    for k, lab in labels.items():
        vals = [abs(q[f"{s_}.JPG"][k]) for s_ in stems]
        L.append(f"| {lab} | {spearman(vals, rec):+.2f} | {spearman(vals, bg):+.2f} | {spearman(vals, hc):+.2f} |")
    L.append(f"| (참고) 인쇄 재현율 | | | {spearman(rec, hc):+.2f} |")

    L.append("\n## 3. 원본 vs 전처리 (10장 평균)\n")
    L.append("| 입력 | 인쇄 재현율 | 위치 무관 재현율 | 인쇄 CER | 손글씨 EM (Full OCR) | 손글씨 CER |")
    L.append("|---|---|---|---|---|---|")
    for v, label in [("original", "원본"), ("clahe", "CLAHE 대비 보정"), ("rectified", "원근 보정")]:
        if v not in printed:
            continue
        pv = printed[v]
        per, em = hw[v]
        em_s = f"{em[0]}/{em[1]}" if em else "-"
        L.append(
            f"| {label} | {np.mean([x['char_recall'] for x in pv.values()]):.3f} | "
            f"{np.mean([x['page_bigram_recall'] for x in pv.values()]):.3f} | "
            f"{np.mean([x['char_cer'] for x in pv.values()]):.3f} | {em_s} | "
            f"{np.mean(list(per.values())) if per else nan:.3f} |"
        )
    L.append("\n### 장별 인쇄 재현율\n")
    L.append("| 이미지 | " + " | ".join(printed) + " |")
    L.append("|---|" + "---|" * len(printed))
    for s_ in stems:
        L.append(f"| {s_} | " + " | ".join(f"{printed[v].get(s_, {}).get('char_recall', nan):.3f}" for v in printed) + " |")

    (H1_DIR / "summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "prepare":
        cmd_prepare(sys.argv[2:])
    elif len(sys.argv) == 5 and sys.argv[1] == "printed":
        cmd_printed(sys.argv[2], sys.argv[3], sys.argv[4])
    elif len(sys.argv) == 2 and sys.argv[1] == "report":
        cmd_report()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
