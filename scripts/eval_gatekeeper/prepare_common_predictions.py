"""Adapt legacy OCR predictions for the common evaluator."""

from pathlib import PurePosixPath

EVALUATION_FIELDS = {
    "address",
    "deposit_num",
    "down_payment",
    "lessor_name",
    "lessee_name",
}

IGNORED_FIELDS = {"deposit_kor"}


def adapt_legacy_predictions(manifest_rows, prediction_rows, method):
    """Map legacy image names to Development image IDs.

    Only rows for the selected method are converted.
    This function does not run OCR or write files.
    """
    image_map = {}

    for record in manifest_rows:
        if record.get("split") != "development":
            continue

        filename = PurePosixPath(
            record["filename"].replace("\\", "/")
        ).name

        if filename in image_map:
            raise ValueError(f"Duplicate manifest filename: {filename}")

        image_map[filename] = record["image_id"]

    converted = []
    seen = set()

    for row in prediction_rows:
        if row.get("method") != method:
            continue

        field = row.get("field")

        if field in IGNORED_FIELDS:
            continue

        if field not in EVALUATION_FIELDS:
            raise ValueError(f"Unexpected prediction field: {field}")

        filename = row.get("image")
        image_id = image_map.get(filename)

        if image_id is None:
            raise ValueError(f"Unknown Development image: {filename}")

        key = (image_id, field)

        if key in seen:
            raise ValueError(f"Duplicate prediction: {key}")

        seen.add(key)

        pred_raw = row.get("pred_raw")
        if pred_raw is None:
            pred_raw = ""

        if not isinstance(pred_raw, str):
            raise ValueError(f"Invalid prediction text: {key}")

        converted.append({
            "image": image_id,
            "field": field,
            "method": method,
            "pred_raw": pred_raw,
        })

    return converted