import json

GT_PATH = "field_gt.json"
RESULT_PATH = "field_mapping_result.json"

with open(GT_PATH, "r", encoding="utf-8") as f:
    gt_data = json.load(f)

with open(RESULT_PATH, "r", encoding="utf-8") as f:
    result_data = json.load(f)

image_name = result_data["image"]

gt_fields = gt_data[image_name]
pred_fields = result_data["fields"]


def calculate_coverage(gt_bbox, roi_bbox):
    gx1, gy1, gx2, gy2 = gt_bbox
    rx1, ry1, rx2, ry2 = roi_bbox

    gt_area = max(0, gx2 - gx1) * max(0, gy2 - gy1)

    if gt_area == 0:
        return 0.0

    ix1 = max(gx1, rx1)
    iy1 = max(gy1, ry1)
    ix2 = min(gx2, rx2)
    iy2 = min(gy2, ry2)

    intersection_area = (
        max(0, ix2 - ix1)
        * max(0, iy2 - iy1)
    )

    return intersection_area / gt_area


print("===== ROI Coverage Evaluation =====")

total_coverage = 0
count = 0
fully_covered = 0

for field, gt_item in gt_fields.items():

    gt_bbox = gt_item.get("bbox")

    result = pred_fields.get(field, {})
    roi_bbox = result.get("value_roi")

    if gt_bbox is None or roi_bbox is None:
        print(f"\n[{field}] 평가 불가")
        continue

    coverage = calculate_coverage(
        gt_bbox,
        roi_bbox
    )

    total_coverage += coverage
    count += 1

    if coverage >= 0.999:
        fully_covered += 1

    print(f"\n[{field}]")
    print("GT bbox :", gt_bbox)
    print("ROI     :", roi_bbox)
    print(f"Coverage: {coverage * 100:.2f}%")


average_coverage = (
    total_coverage / count
    if count > 0
    else 0
)

coverage_success_rate = (
    fully_covered / count
    if count > 0
    else 0
)

print("\n==============================")
print(f"평가 필드: {count}")
print(f"평균 ROI Coverage: {average_coverage * 100:.2f}%")
print(
    f"완전 포함 성공률: "
    f"{fully_covered}/{count} "
    f"({coverage_success_rate * 100:.2f}%)"
)