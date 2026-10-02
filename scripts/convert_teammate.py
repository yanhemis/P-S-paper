"""
팀원 결과(taegu)를 tail 평가 형식으로 변환

사용법:
    # taegu field_mapping_result.json -> 실험 C 입력 ROI json
    python convert_teammate.py taegu-roi <field_mapping_result.json> <out_roi.json>

    # taegu field_gt.json -> tail GT (정답 텍스트 + 정답 ROI)
    python convert_teammate.py taegu-gt <field_gt.json> <out_gt_fields.json> <out_gt_roi.json>

팀원 폴더(../taegu 등)는 읽기만 하고, 변환 결과는 tail 안에만 쓴다.
taegu 결과는 단일 이미지({"image", "fields"}) 또는 그 리스트를 모두 받는다.
"""

import sys
import json
from pathlib import Path

# taegu 필드명 -> tail 필드 키 (docs/ocr_io_spec.md 0절)
# taegu "보증금"은 한글 금액("일억")이므로 deposit_kor 로 매핑한다.
TAEGU_FIELD_MAP = {
    "소재지": "address",
    "보증금": "deposit_kor",
    "계약금": "down_payment",
    "임대인_성명": "lessor_name",
    "임차인_성명": "lessee_name",
}

# 팀원 GT를 이미지와 대조했을 때 다른 값 (tail 쪽 변환본에서만 고치고, 원본 파일은 건드리지 않음)
GT_CORRECTIONS = {
    # 이미지에는 "401호"로 기입됨 (taegu/field_gt.json 은 "401")
    ("sample.jpg", "address"): "서울특별시 강남구 테헤란로 123, 4층 401호",
}


def _entries(data):
    if isinstance(data, list):
        return data
    if "image" in data and "fields" in data:
        return [data]
    raise SystemExit("알 수 없는 형식: {'image', 'fields'} 또는 그 리스트여야 함")


def convert_roi(src, dst):
    data = json.loads(Path(src).read_text(encoding="utf-8"))
    out = {}
    for entry in _entries(data):
        fields = {}
        for name, item in entry["fields"].items():
            key = TAEGU_FIELD_MAP.get(name)
            roi = item.get("value_roi") if isinstance(item, dict) else None
            if key is None or roi is None:
                continue  # anchor를 못 찾은 필드는 빠짐 -> 평가에서 실패로 처리됨
            fields[key] = {"bbox": [int(v) for v in roi]}
        out[entry["image"]] = {"source": f"taegu {Path(src).name} value_roi", "fields": fields}
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    Path(dst).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] {dst}: " + ", ".join(f"{k}({len(v['fields'])} fields)" for k, v in out.items()))


def convert_gt(src, dst_fields, dst_roi):
    data = json.loads(Path(src).read_text(encoding="utf-8"))
    gt_fields = {"_meta": {"source": f"taegu {Path(src).name}", "corrections": {}}}
    gt_roi = {}
    for image, fields in data.items():
        gt_fields[image] = {}
        gt_roi[image] = {"fields": {}}
        for name, item in fields.items():
            key = TAEGU_FIELD_MAP.get(name)
            if key is None:
                continue
            value = item["value"]
            fixed = GT_CORRECTIONS.get((image, key))
            if fixed is not None and fixed != value:
                gt_fields["_meta"]["corrections"][f"{image}/{key}"] = {"taegu": value, "tail": fixed}
                value = fixed
            gt_fields[image][key] = value
            gt_roi[image]["fields"][key] = {"bbox": [int(v) for v in item["bbox"]]}
    for path, obj in [(dst_fields, gt_fields), (dst_roi, gt_roi)]:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] {dst_fields}, {dst_roi} (corrections: {len(gt_fields['_meta']['corrections'])})")


def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "taegu-roi":
        convert_roi(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 5 and sys.argv[1] == "taegu-gt":
        convert_gt(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
