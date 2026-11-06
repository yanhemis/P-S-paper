"""Adapt Dataset v1.0 Development GT for the existing common evaluator."""

FIELD_MAP = {
    "address": "address",
    "deposit": "deposit_num",
    "contract_amount": "down_payment",
    "lessor_name": "lessor_name",
    "lessee_name": "lessee_name",
}


def adapt_development_gt(dataset_gt):
    """Convert Dataset v1.0 GT to the legacy evaluator's GT structure."""
    if not isinstance(dataset_gt, dict):
        raise ValueError("Dataset GT must be a dictionary")

    converted = {}

    for image_id, record in dataset_gt.items():
        if not isinstance(record, dict):
            raise ValueError(f"{image_id}: invalid image record")

        fields = record.get("fields")

        if not isinstance(fields, dict):
            raise ValueError(f"{image_id}: missing fields")

        if set(fields) != set(FIELD_MAP):
            raise ValueError(f"{image_id}: unexpected field set")

        flattened = {}

        for new_field, legacy_field in FIELD_MAP.items():
            item = fields[new_field]

            if not isinstance(item, dict):
                raise ValueError(
                    f"{image_id}/{new_field}: invalid field record"
                )

            if item.get("status") == "not_present":
                continue

            raw_text = item.get("raw_text")

            if (
                not isinstance(raw_text, str)
                or not raw_text.strip()
                or "?" in raw_text
                or "\ufffd" in raw_text
            ):
                raise ValueError(
                    f"{image_id}/{new_field}: invalid raw_text"
                )

            flattened[legacy_field] = raw_text

        converted[image_id] = flattened

    return converted