"""Adapt P4 final_fields.json results for the common evaluator."""

from pathlib import PurePosixPath

FIELDS = {
    "address",
    "deposit",
    "contract_amount",
    "lessor_name",
    "lessee_name",
}


def adapt_p4_predictions(manifest_rows, p4_results):
    """Convert P4 results into common evaluator prediction rows.

    p4_results: list of parsed final_fields.json dictionaries.
    No OCR execution or file writes.
    """
    image_map = {}

    for record in manifest_rows:
        if record.get("split") != "development":
            continue

        if record.get("usable") != "yes":
            continue

        filename = PurePosixPath(
            record["filename"].replace("\\", "/")
        ).name

        if filename in image_map:
            raise ValueError(
                f"Duplicate manifest filename: {filename}"
            )

        image_map[filename] = record["image_id"]

    converted = []
    seen = set()

    for result in p4_results:
        if not isinstance(result, dict):
            raise ValueError("Invalid P4 result")

        filename = result.get("image_id")
        image_id = image_map.get(filename)

        if image_id is None:
            raise ValueError(
                f"Unknown Development image: {filename}"
            )

        # Cached PoC outputs must not enter final measured evaluation.
        if result.get("first_pass_source") != "live_paddleocr":
            raise ValueError(
                f"P4 result is not marked as live OCR: {filename}"
            )

        fields = result.get("fields")

        if not isinstance(fields, dict):
            raise ValueError(
                f"{filename}: invalid fields"
            )

        for field, entry in fields.items():
            if field not in FIELDS:
                raise ValueError(
                    f"Unexpected P4 field: {field}"
                )

            if not isinstance(entry, dict):
                raise ValueError(
                    f"{filename}/{field}: invalid field entry"
                )

            key = (image_id, field)

            if key in seen:
                raise ValueError(
                    f"Duplicate P4 prediction: {key}"
                )

            seen.add(key)

            prediction = entry.get("prediction")

            if prediction is None:
                prediction = ""

            if not isinstance(prediction, str):
                raise ValueError(
                    f"Invalid P4 prediction: {key}"
                )

            converted.append({
                "image": image_id,
                "field": field,
                "method": "P4",
                "pred_raw": prediction,
            })

    return converted