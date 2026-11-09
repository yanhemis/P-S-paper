import json
import re
import subprocess
import unicodedata

from amount_normalizer import normalize_amount


# Canonical field -> legacy field
FIELDS = {
    "address": "address",
    "deposit": "deposit_num",
    "contract_amount": "down_payment",
    "lessor_name": "lessor_name",
    "lessee_name": "lessee_name",
}

MONEY_FIELDS = {"deposit", "contract_amount"}


def load_tail_json(path):
    raw = subprocess.check_output(
        ["git", "show", f"origin/tail:{path}"]
    )
    return json.loads(raw.decode("utf-8"))


def normalize_text(field, value):
    """Draft text normalization for CER."""
    if value is None:
        return ""

    text = unicodedata.normalize("NFC", str(value))
    text = re.sub(r"\s+", "", text)

    if field in MONEY_FIELDS:
        text = re.sub(r"원정은?", "", text)
        text = re.sub(r"[()₩W\\]", "", text)
        text = text.replace("금", "")
        text = re.sub(r"원$", "", text)
        return text.replace(",", "")

    if field in ("lessor_name", "lessee_name"):
        text = re.sub(r"\(?인\)", "", text)
        text = text.replace("성명", "")
        return re.sub(r"[()|.,]", "", text)

    if field == "address":
        return re.sub(r"[,.·]", "", text)

    return text

def parse_ocr_amount(raw):
    """Draft: form-aware monetary parsing without OCR error correction."""
    if raw is None or not str(raw).strip():
        return None

    text = unicodedata.normalize("NFC", str(raw)).strip()

    # Contract-form pattern:
    # [optional Korean amount] 원정(W [numeric amount]
    form = re.fullmatch(
        r"(.*?)원정\s*\(\s*[Ww₩]\s*(.*?)\s*'?\s*",
        text,
    )

    if form:
        korean_text = form.group(1).strip()
        numeric_text = form.group(2).strip().rstrip("'").strip()

        # Numeric amount must have valid three-digit grouping.
        if not re.fullmatch(
            r"\d+|\d{1,3}(?P<sep>[,.])\d{3}(?:(?P=sep)\d{3})*",
            numeric_text,
        ):
            return None

        numeric_value = normalize_amount(
            numeric_text.replace(".", "")
        )

        if not korean_text:
            return numeric_value

        korean_value = normalize_amount(korean_text)

        # Both expressions must be independently valid and agree.
        if korean_value is None or korean_value != numeric_value:
            return None

        return numeric_value

    # Validate grouping before removing punctuation.
    for fragment in re.findall(r"\d[\d,.]*", text):
        if "," in fragment or "." in fragment:
            if not re.fullmatch(
                r"\d+|\d{1,3}(?P<sep>[,.])\d{3}(?:(?P=sep)\d{3})*",
                fragment,
            ):
                return None

    # A dot is removed only after grouping validation.
    return normalize_amount(text.replace(".", ""))

def levenshtein(a, b):
    previous = list(range(len(b) + 1))

    for i, char_a in enumerate(a, start=1):
        current = [i]

        for j, char_b in enumerate(b, start=1):
            current.append(
                min(
                    current[j - 1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + (char_a != char_b),
                )
            )

        previous = current

    return previous[-1]


def evaluate(gt, rows, method):
    """Evaluate all eligible GT fields, including missing predictions."""

    predictions = {}

    for row in rows:
        if row.get("method") != method:
            continue

        key = (row["image"], row["field"])

        if key in predictions:
            raise ValueError(f"Duplicate prediction: {key}")

        predictions[key] = row

    details = []

    for image, gt_fields in sorted(gt.items()):
        if image.startswith("_") or not isinstance(gt_fields, dict):
            continue

        for field, legacy_field in FIELDS.items():
            gt_raw = gt_fields.get(legacy_field)

            # Only genuinely absent GT fields are excluded.
            if gt_raw is None:
                continue

            row = predictions.get((image, legacy_field))
            pred_raw = (
                row.get("pred_raw", "") if row is not None else ""
            )
            pred_raw = pred_raw or ""

            gt_text = normalize_text(field, gt_raw)
            pred_text = normalize_text(field, pred_raw)

            cer = (
                levenshtein(pred_text, gt_text)
                / max(len(gt_text), 1)
            )

            if field in MONEY_FIELDS:
                gt_value = normalize_amount(str(gt_raw))
                pred_value = parse_ocr_amount(pred_raw)

                exact = (
                    gt_value is not None
                    and pred_value is not None
                    and gt_value == pred_value
                )
                invalid_amount = pred_value is None
            else:
                exact = pred_text == gt_text
                invalid_amount = False

            details.append({
                "image": image,
                "field": field,
                "gt_raw": gt_raw,
                "pred_raw": pred_raw,
                "exact_match": exact,
                "cer": cer,
                "missing_row": row is None,
                "empty_prediction": not pred_raw.strip(),
                "invalid_amount": invalid_amount,
            })

    total = len(details)
    correct = sum(item["exact_match"] for item in details)

    return {
        "total": total,
        "correct": correct,
        "field_accuracy": correct / total if total else None,
        "mean_cer": (
            sum(item["cer"] for item in details) / total
            if total else None
        ),
        "missing_rows": sum(
            item["missing_row"] for item in details
        ),
        "empty_predictions": sum(
            item["empty_prediction"] for item in details
        ),
        "invalid_amounts": sum(
            item["invalid_amount"] for item in details
            if item["field"] in MONEY_FIELDS
        ),
        "details": details,
    }


if __name__ == "__main__":
    print("DRAFT: common-10 raw OCR evaluation")
    print("Monetary form preprocessing is not frozen.")

    gt = load_tail_json("gt/gt_fields.json")

    sources = [
        ("P0", "results/eval/field_results.json", "Full OCR"),
        ("P1", "results/h1/eval_rectified/field_results.json", "Full OCR"),
        ("P2", "results/eval/field_results.json", "GT ROI OCR"),
        (
            "P3",
            "results/eval/detected_bang_pad25/field_results.json",
            "Detected ROI OCR",
        ),
    ]

    for label, path, method in sources:
        rows = load_tail_json(path)["rows"]
        result = evaluate(gt, rows, method)

        print(
            label,
            "total=", result["total"],
            "correct=", result["correct"],
            "accuracy=", round(result["field_accuracy"], 4),
            "mean_cer=", round(result["mean_cer"], 4),
            "missing_rows=", result["missing_rows"],
            "empty=", result["empty_predictions"],
            "invalid_money=", result["invalid_amounts"],
        )

        if result["total"] != 49:
            raise AssertionError(
                f"{label}: expected 49 eligible fields, "
                f"got {result['total']}"
            )