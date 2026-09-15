import json

GT_PATH = "field_gt.json"
RESULT_PATH = "field_mapping_result.json"

with open(GT_PATH, "r", encoding="utf-8") as f:
    gt_data = json.load(f)

with open(RESULT_PATH, "r", encoding="utf-8") as f:
    result_data = json.load(f)

image_name = result_data["image"]
predictions = result_data["fields"]
ground_truth = gt_data[image_name]

correct = 0
total = len(ground_truth)

print("===== Field Exact Match =====")

for field, gt_item in ground_truth.items():

    gt_value = gt_item["value"]
    
    pred_item = predictions.get(field, {})
    pred_value = pred_item.get("value") if isinstance(pred_item, dict) else pred_item

    is_correct = pred_value == gt_value

    if is_correct:
        correct += 1

    status = "PASS" if is_correct else "FAIL"

    print(f"\n[{field}] {status}")
    print(f"GT   : {gt_value}")
    print(f"PRED : {pred_value}")

accuracy = correct / total if total else 0

print("\n=============================")
print(f"Correct: {correct}/{total}")
print(f"Field Accuracy: {accuracy * 100:.2f}%")