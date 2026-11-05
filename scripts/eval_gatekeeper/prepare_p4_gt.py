import argparse
import csv
import json
from pathlib import Path, PurePosixPath

FIELDS = (
    "address",
    "deposit",
    "contract_amount",
    "lessor_name",
    "lessee_name",
)


def prepare(development_dir, output_path):
    manifest_path = development_dir / "manifest.csv"
    gt_path = development_dir / "field_gt.json"

    with manifest_path.open(encoding="utf-8-sig", newline="") as f:
        manifest = list(csv.DictReader(f))

    with gt_path.open(encoding="utf-8-sig") as f:
        gt = json.load(f)

    converted = {}
    errors = []

    for row in manifest:
        image_id = row["image_id"]
        filename = PurePosixPath(row["filename"]).name

        if row["split"] != "development":
            errors.append(f"{image_id}: not development")
            continue

        if row["usable"] != "yes":
            errors.append(f"{image_id}: not usable")
            continue

        if filename in converted:
            errors.append(f"{filename}: duplicate filename")
            continue

        record = gt.get(image_id)

        if not isinstance(record, dict):
            errors.append(f"{image_id}: missing GT record")
            continue

        if record.get("document_group_id") != row["document_group_id"]:
            errors.append(f"{image_id}: document group mismatch")
            continue

        fields = record.get("fields", {})
        flattened = {}

        for field in FIELDS:
            item = fields.get(field)

            if not isinstance(item, dict):
                errors.append(f"{image_id}/{field}: missing GT")
                continue

            if item.get("status") == "not_present":
                flattened[field] = {"status": "not_present"}
                continue

            raw = item.get("raw_text")
            normalized = item.get("normalized")

            if (
                not isinstance(raw, str)
                or not raw.strip()
                or "?" in raw
                or "\ufffd" in raw
            ):
                errors.append(f"{image_id}/{field}: invalid raw_text")

            if (
                not isinstance(normalized, str)
                or not normalized.strip()
                or "?" in normalized
                or "\ufffd" in normalized
            ):
                errors.append(f"{image_id}/{field}: invalid normalized GT")

            flattened[field] = item

        converted[filename] = flattened

    if errors:
        raise ValueError(
            "GT validation failed:\n" + "\n".join(errors)
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(converted, f, ensure_ascii=False, indent=2)

    print("P4 GT adapter created:", output_path)
    print("Images:", len(converted))
    print("Original Dataset files were not modified.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--development-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    prepare(args.development_dir, args.output)