"""
필드 단위 평가 - Full OCR vs GT ROI OCR (vs Detected ROI OCR)

사용법:
    python evaluate_fields.py [--detected <roi_ocr_dir>]

입력:
- gt/gt_fields.json         : 필드별 정답 텍스트
- gt/gt_roi.json            : 필드별 정답 ROI (Full OCR 결과를 필드에 배정할 때 사용)
- results/<stem>_ocr.json   : 실험 A (Full OCR, items[].poly 필요)
- results/roi_gt/<stem>_roi_ocr.json        : 실험 B
- <roi_ocr_dir>/<stem>_roi_ocr.json (선택)  : 실험 C

출력:
- results/eval/field_results.json : 이미지 x 필드 x 방법별 예측/정답/CER/EM/confidence
- results/eval/summary.md         : 방법별 비교표

Full OCR의 필드 배정 방식:
    전체 페이지 OCR 박스 하나에 여러 칸의 글자가 섞이는 경우가 많아서(예: "일천팔백만 원정은
    계약시에 지급하고 영수함."), 박스를 통째로 배정하지 않고 글자 단위로 배정한다.
    박스 polygon의 좌/우 변 중점을 잇는 선을 글자 수만큼 등분해 각 글자의 중심을 추정하고,
    그 중심이 GT ROI(실험 B와 같은 세로 여유 PAD_RATIO 적용) 안에 있는 글자만 모은다.
    박스 글자의 WHOLE_BOX_RATIO 이상이 칸 안에 있으면 박스 전체를 그 칸에 배정한다.
    한계: 글자 폭이 균일하다고 가정하므로 인쇄 글자와 손글씨가 섞인 긴 박스에서는 경계 글자가
    한두 개 어긋날 수 있다. (금액 끝에 "원정"의 "원"이 붙는 경우는 normalize에서 제거)
"""

import sys
import json
import re
import unicodedata
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from roi_ocr import expand_quad  # noqa: E402  실험 B와 같은 ROI 여유를 쓰기 위함

ROOT = Path(__file__).resolve().parent.parent
GT_FIELDS = ROOT / "gt" / "gt_fields.json"
GT_ROI = ROOT / "gt" / "gt_roi.json"
FULL_DIR = ROOT / "results"
ROI_GT_DIR = ROOT / "results" / "roi_gt"
EVAL_DIR = ROOT / "results" / "eval"

WHOLE_BOX_RATIO = 0.5

FIELDS = ["address", "deposit_num", "deposit_kor", "down_payment", "lessor_name", "lessee_name"]
FIELD_LABELS = {
    "address": "소재지",
    "deposit_num": "보증금 (숫자)",
    "deposit_kor": "보증금 (한글, 보조)",
    "down_payment": "계약금",
    "lessor_name": "임대인 성명",
    "lessee_name": "임차인 성명",
}


# ---------------------------------------------------------------- 정규화

def normalize(field, text):
    """인쇄된 양식 글자와 표기 차이(공백, 쉼표 등)를 지우고 손글씨 값만 비교한다."""
    if text is None:
        return None
    t = unicodedata.normalize("NFC", text)
    t = re.sub(r"\s+", "", t)
    if field == "deposit_num":
        return re.sub(r"\D", "", t)
    if field in ("deposit_kor", "down_payment"):
        # 양식에 인쇄된 "금", "원정(₩", "원정은", ")" 등 제거. 금액 숫자 사이의 "원"(천->원 오인식)은 남긴다.
        t = re.sub(r"원정은?", "", t)
        t = re.sub(r"[()₩W\\]", "", t)
        t = t.replace("금", "")
        # 금액은 항상 "만"으로 끝남. 끝에 붙은 "원"은 인쇄된 "원정"이 잘려 들어온 것
        return re.sub(r"원$", "", t)
    if field in ("lessor_name", "lessee_name"):
        t = re.sub(r"\(?인\)", "", t)
        t = t.replace("성명", "")
        return re.sub(r"[()|.,]", "", t)
    if field == "address":
        return re.sub(r"[,.·]", "", t)
    return t


def levenshtein(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def cer(pred, gt):
    return levenshtein(pred, gt) / max(len(gt), 1)


# ---------------------------------------------------------------- Full OCR -> 필드 배정

def point_in_quad(pt, quad):
    """볼록 사각형 내부 판정 (모든 변에 대해 같은 쪽에 있는지)."""
    sign = 0
    for i in range(4):
        a, b = quad[i], quad[(i + 1) % 4]
        cross = (b[0] - a[0]) * (pt[1] - a[1]) - (b[1] - a[1]) * (pt[0] - a[0])
        s = np.sign(cross)
        if s == 0:
            continue
        if sign == 0:
            sign = s
        elif s != sign:
            return False
    return True


def assign_full_ocr(items, quad):
    """quad 안에 중심이 들어오는 글자만 모아 quad의 가로 방향 순서대로 이어 붙인다."""
    q = expand_quad(quad)
    axis = (q[1] - q[0]) / np.linalg.norm(q[1] - q[0])
    chars, confs = [], []
    for it in items:
        text = it["text"]
        if not text:
            continue
        p = np.float32(it["poly"])  # 좌상, 우상, 우하, 좌하
        left = (p[0] + p[3]) / 2
        right = (p[1] + p[2]) / 2
        n = len(text)
        centers = [left + (right - left) * (k + 0.5) / n for k in range(n)]
        inside = [point_in_quad(c, q) for c in centers]
        if not any(inside):
            continue
        if sum(inside) / n >= WHOLE_BOX_RATIO:
            # 박스 대부분이 칸 안이면 통째로 쓴다 (균일 글자 폭 가정 때문에 경계 글자가 잘리는 것 방지)
            inside = [True] * n
        for c, ch, ok in zip(centers, text, inside):
            if ok:
                chars.append((float(np.dot(c - q[0], axis)), ch))
        confs.append(it["confidence"])
    chars.sort(key=lambda x: x[0])
    text = "".join(ch for _, ch in chars)
    return text, (float(np.mean(confs)) if confs else 0.0)


# ---------------------------------------------------------------- 평가

def evaluate_method(method, preds, gt_fields):
    """preds: {image: {field: (text, conf)}} -> 행 리스트"""
    rows = []
    for image, gt in gt_fields.items():
        if image.startswith("_") or image not in preds:
            continue
        for field in FIELDS:
            gt_text = gt.get(field)
            if gt_text is None:
                continue  # 미기입 필드는 평가 제외
            pred_raw, conf = preds[image].get(field, ("", 0.0))
            p = normalize(field, pred_raw)
            g = normalize(field, gt_text)
            rows.append(
                {
                    "method": method,
                    "image": image,
                    "set": gt["set"],
                    "field": field,
                    "gt": gt_text,
                    "pred_raw": pred_raw,
                    "pred_norm": p,
                    "gt_norm": g,
                    "cer": cer(p, g),
                    "exact_match": p == g,
                    "confidence": conf,
                }
            )
    return rows


def load_full_preds(gt_roi):
    preds, runtimes = {}, {}
    for image, entry in gt_roi.items():
        path = FULL_DIR / f"{Path(image).stem}_ocr.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["items"] and "poly" not in data["items"][0]:
            raise SystemExit(f"{path.name}에 poly가 없음 -> ocr_baseline.py를 다시 실행할 것")
        preds[image] = {
            f: assign_full_ocr(data["items"], np.float32(roi["quad"]))
            for f, roi in entry["fields"].items()
        }
        runtimes[image] = data["runtime_sec"]
    return preds, runtimes


def load_roi_preds(roi_dir):
    preds, runtimes, per_roi = {}, {}, []
    for path in sorted(Path(roi_dir).glob("*_roi_ocr.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        preds[data["image_id"]] = {
            f: (v["text"], v["confidence"]) for f, v in data["fields"].items()
        }
        runtimes[data["image_id"]] = data["runtime_sec"]
        per_roi += [v["runtime_sec"] for v in data["fields"].values()]
    return preds, runtimes, per_roi


def summarize(rows, methods):
    lines = []
    lines.append("## 방법별 전체 요약\n")
    lines.append("| 방법 | 평가 필드 수 | Field Accuracy (EM) | 평균 CER | 평균 confidence |")
    lines.append("|---|---|---|---|---|")
    for m in methods:
        r = [x for x in rows if x["method"] == m and x["field"] != "deposit_kor"]
        if not r:
            continue
        em = sum(x["exact_match"] for x in r)
        lines.append(
            f"| {m} | {len(r)} | {em}/{len(r)} ({em / len(r):.1%}) | "
            f"{np.mean([x['cer'] for x in r]):.3f} | {np.mean([x['confidence'] for x in r]):.3f} |"
        )
    lines.append("\n(보증금 한글 칸은 보조 지표라 전체 요약에서 제외)\n")

    lines.append("## 필드별 Exact Match (성공/전체) · 평균 CER\n")
    lines.append("| 필드 | " + " | ".join(methods) + " |")
    lines.append("|---|" + "---|" * len(methods))
    for f in FIELDS:
        cells = []
        for m in methods:
            r = [x for x in rows if x["method"] == m and x["field"] == f]
            if not r:
                cells.append("-")
                continue
            em = sum(x["exact_match"] for x in r)
            cells.append(f"{em}/{len(r)} · CER {np.mean([x['cer'] for x in r]):.3f}")
        lines.append(f"| {FIELD_LABELS[f]} | " + " | ".join(cells) + " |")

    lines.append("\n## 이미지별 Exact Match (5개 우선 필드)\n")
    lines.append("| 이미지 (세트) | " + " | ".join(methods) + " |")
    lines.append("|---|" + "---|" * len(methods))
    images = sorted({x["image"] for x in rows}, key=lambda s: int(re.sub(r"\D", "", s) or 0))
    for img in images:
        cells = []
        for m in methods:
            r = [x for x in rows if x["method"] == m and x["image"] == img and x["field"] != "deposit_kor"]
            cells.append(f"{sum(x['exact_match'] for x in r)}/{len(r)}" if r else "-")
        s = next(x["set"] for x in rows if x["image"] == img)
        lines.append(f"| {img} (#{s}) | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    detected_dir = None
    if "--detected" in sys.argv:
        detected_dir = Path(sys.argv[sys.argv.index("--detected") + 1]).resolve()

    gt_fields = json.loads(GT_FIELDS.read_text(encoding="utf-8"))
    gt_roi = json.loads(GT_ROI.read_text(encoding="utf-8"))

    rows, methods, perf = [], [], {}

    full_preds, full_rt = load_full_preds(gt_roi)
    rows += evaluate_method("Full OCR", full_preds, gt_fields)
    methods.append("Full OCR")
    perf["Full OCR"] = {"sec_per_image": float(np.mean(list(full_rt.values())))}

    for name, d in [("GT ROI OCR", ROI_GT_DIR), ("Detected ROI OCR", detected_dir)]:
        if d is None or not Path(d).exists():
            continue
        preds, rt, per_roi = load_roi_preds(d)
        if not preds:
            continue
        rows += evaluate_method(name, preds, gt_fields)
        methods.append(name)
        perf[name] = {
            "sec_per_image": float(np.mean(list(rt.values()))),
            "sec_per_roi": float(np.mean(per_roi)),
        }

    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    (EVAL_DIR / "field_results.json").write_text(
        json.dumps({"performance": perf, "rows": rows}, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = ["# 필드 단위 평가 결과\n", summarize(rows, methods), "\n## 처리 시간\n",
          "| 방법 | sec/image | sec/ROI |", "|---|---|---|"]
    for m, p in perf.items():
        md.append(f"| {m} | {p['sec_per_image']:.2f} | {p.get('sec_per_roi', float('nan')):.2f} |")
    md.append("\n(ROI 방법의 sec/image = 한 장의 ROI OCR 시간 합. Cell/ROI 검출 시간은 포함하지 않음)\n")

    md.append("\n## 전체 예측 (정규화 후)\n")
    md.append("| 이미지 | 필드 | 정답 | " + " | ".join(methods) + " |")
    md.append("|---|---|---|" + "---|" * len(methods))
    keyed = {(x["method"], x["image"], x["field"]): x for x in rows}
    for img in sorted({x["image"] for x in rows}, key=lambda s: int(re.sub(r"\D", "", s) or 0)):
        for f in FIELDS:
            base = keyed.get((methods[0], img, f))
            if base is None:
                continue
            cells = []
            for m in methods:
                x = keyed.get((m, img, f))
                cells.append("-" if x is None else ("✅ " if x["exact_match"] else "❌ ") + f"`{x['pred_norm']}`")
            md.append(f"| {img} | {FIELD_LABELS[f]} | `{base['gt_norm']}` | " + " | ".join(cells) + " |")

    (EVAL_DIR / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(summarize(rows, methods))
    print("\nperformance:", json.dumps(perf, ensure_ascii=False))


if __name__ == "__main__":
    main()
