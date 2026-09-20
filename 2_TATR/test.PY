from transformers import TableTransformerForObjectDetection, AutoImageProcessor
from PIL import Image, ImageDraw
import torch
import os
import json

# 1. 이미지 불러오기
image_path = "../sample.jpg" if os.path.exists("../sample.jpg") else "sample.jpg"
try:
    image = Image.open(image_path).convert("RGB")
except FileNotFoundError:
    print(f"❌ 오류: '{image_path}' 파일을 찾을 수 없습니다.")
    exit()

print("⏳ TATR 모델을 불러오는 중입니다...")
processor = AutoImageProcessor.from_pretrained("microsoft/table-transformer-structure-recognition")
model = TableTransformerForObjectDetection.from_pretrained("microsoft/table-transformer-structure-recognition")

inputs = processor(images=image, return_tensors="pt")
outputs = model(**inputs)

target_sizes = torch.tensor([image.size[::-1]])
results = processor.post_process_object_detection(outputs, threshold=0.7, target_sizes=target_sizes)[0]

rows = []
cols = []
raw_spanning = [] # 피드백 7번: raw spanning bbox 저장용

# 4-1. 행, 열, 병합 셀 각각 추출 (피드백 7번: confidence(score) 포함)
for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
    box = [round(i, 2) for i in box.tolist()]
    score_val = round(score.item(), 4)
    label_name = model.config.id2label[label.item()]
    
    if label_name == "table row":
        rows.append({"bbox": box, "score": score_val})
    elif label_name == "table column":
        cols.append({"bbox": box, "score": score_val})
    elif label_name == "table spanning cell":
        raw_spanning.append({"bbox": box, "score": score_val})

# 4-2. 정렬 (위->아래, 좌->우)
rows.sort(key=lambda x: x["bbox"][1])
cols.sort(key=lambda x: x["bbox"][0])

# 4-3. 1차 바둑판(기본 셀) 생성 - [Priority 2: row × column only]
grid_cells = []
for row in rows:
    for col in cols:
        box = [col["bbox"][0], row["bbox"][1], col["bbox"][2], row["bbox"][3]]
        # 교차 셀의 score는 row와 col의 평균으로 임의 산정
        avg_score = round((row["score"] + col["score"]) / 2, 4)
        # 피드백 4번 B안: type, score를 명시한 표준화 JSON 적용
        grid_cells.append({"bbox": box, "type": "general", "score": avg_score})

# [결과 1] Grid Only 저장
with open("tatr_result_grid.json", "w", encoding="utf-8") as f:
    json.dump(grid_cells, f, indent=2)
print("✅ Ablation 1: Grid Only 저장 완료 ('tatr_result_grid.json')")

# 4-4. 병합 셀(Spanning-cell) 덮어씌우기 - [Priority 2: + spanning reconstruction]
def get_intersection_area(boxA, boxB):
    xA, yA = max(boxA[0], boxB[0]), max(boxA[1], boxB[1])
    xB, yB = min(boxA[2], boxB[2]), min(boxA[3], boxB[3])
    return max(0, xB - xA) * max(0, yB - yA)

def get_area(box):
    return (box[2] - box[0]) * (box[3] - box[1])

final_cells = []
merged_indices = set()

# 피드백 7번: 여러 spanning이 겹칠 때를 대비해 score가 높은 놈부터 우선 처리
raw_spanning.sort(key=lambda x: x["score"], reverse=True)

for span in raw_spanning:
    span_box = span["bbox"]
    merged_box = None
    overlapping_scores = [span["score"]]
    
    for i, g_cell in enumerate(grid_cells):
        if i in merged_indices: continue
        base_box = g_cell["bbox"]
        inter_area = get_intersection_area(span_box, base_box)
        base_area = get_area(base_box)
        
        # 피드백 7번: 민감도 평가를 위한 overlap threshold 기준점 (현재 0.5)
        if inter_area > 0.5 * base_area:
            merged_indices.add(i)
            overlapping_scores.append(g_cell["score"])
            if merged_box is None:
                merged_box = base_box[:]
            else:
                merged_box[0] = min(merged_box[0], base_box[0])
                merged_box[1] = min(merged_box[1], base_box[1])
                merged_box[2] = max(merged_box[2], base_box[2])
                merged_box[3] = max(merged_box[3], base_box[3])
                
    if merged_box:
        final_score = round(sum(overlapping_scores) / len(overlapping_scores), 4)
        final_cells.append({"bbox": merged_box, "type": "merged", "score": final_score})

# 병합 안 된 일반 칸 추가
for i, g_cell in enumerate(grid_cells):
    if i not in merged_indices:
        final_cells.append(g_cell)

# 피드백 7번: raw spanning과 reconstructed cell 분리 저장
output_spanning = {
    "raw_spanning_bboxes": raw_spanning,
    "reconstructed_cells": final_cells
}
with open("tatr_result_spanning.json", "w", encoding="utf-8") as f:
    json.dump(output_spanning, f, indent=2)
print("✅ Ablation 2: Spanning 재구성 저장 완료 ('tatr_result_spanning.json')")

# 시각화 (Merged: 빨간색, General: 파란색)
draw = ImageDraw.Draw(image)
for cell in final_cells:
    color = "blue" if cell["type"] == "general" else "red"
    draw.rectangle(cell["bbox"], outline=color, width=3)
image.save("tatr_cell_result.jpg")
print("✅ 시각화 완료 ('tatr_cell_result.jpg')")