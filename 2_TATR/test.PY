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

# 2. Table Transformer 모델 및 프로세서 불러오기
print("⏳ TATR 모델을 불러오는 중입니다...")
processor = AutoImageProcessor.from_pretrained("microsoft/table-transformer-structure-recognition")
model = TableTransformerForObjectDetection.from_pretrained("microsoft/table-transformer-structure-recognition")

# 3. 이미지 전처리 및 모델 추론
inputs = processor(images=image, return_tensors="pt")
outputs = model(**inputs)

# 4. 결과 좌표 변환
target_sizes = torch.tensor([image.size[::-1]])
results = processor.post_process_object_detection(outputs, threshold=0.7, target_sizes=target_sizes)[0]

# ==========================================
# 💡 [핵심] TATR 결과에서 실제 Cell bbox 재구성 (팀장님 피드백 완벽 반영)
# ==========================================
rows = []
cols = []
spanning_cells = [] # 👈 병합 셀(Spanning-cell) 정보를 담을 리스트 추가!

# 4-1. 행, 열, 병합 셀 각각 추출
for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
    box = [round(i, 2) for i in box.tolist()]
    label_name = model.config.id2label[label.item()]
    
    if label_name == "table row":
        rows.append(box)
    elif label_name == "table column":
        cols.append(box)
    elif label_name == "table spanning cell":
        spanning_cells.append(box) # 👈 TATR이 찾은 병합 구조 저장

# 4-2. 정렬 (위->아래, 좌->우)
rows.sort(key=lambda x: x[1])
cols.sort(key=lambda x: x[0])

# 4-3. 1차 바둑판(기본 셀) 생성
base_cells = []
for row in rows:
    for col in cols:
        base_cells.append([col[0], row[1], col[2], row[3]])

# 4-4. 병합 셀(Spanning-cell) 덮어씌우기 (진짜 재구성 로직)
def get_intersection_area(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    return max(0, xB - xA) * max(0, yB - yA)

def get_area(box):
    return (box[2] - box[0]) * (box[3] - box[1])

final_cells = []
merged_indices = set()

# Spanning-cell 영역에 포함되는 자잘한 기본 셀들을 하나로 묶기
for span_box in spanning_cells:
    merged_box = None
    for i, base_cell in enumerate(base_cells):
        if i in merged_indices: continue
        inter_area = get_intersection_area(span_box, base_cell)
        base_area = get_area(base_cell)
        
        # 기본 셀 면적의 50% 이상이 Spanning 영역에 겹치면 병합 대상으로 판단
        if inter_area > 0.5 * base_area:
            merged_indices.add(i)
            if merged_box is None:
                merged_box = base_cell[:]
            else:
                merged_box[0] = min(merged_box[0], base_cell[0])
                merged_box[1] = min(merged_box[1], base_cell[1])
                merged_box[2] = max(merged_box[2], base_cell[2])
                merged_box[3] = max(merged_box[3], base_cell[3])
                
    if merged_box:
        final_cells.append(merged_box)

# 병합되지 않은 나머지 일반 칸들 추가
for i, base_cell in enumerate(base_cells):
    if i not in merged_indices:
        final_cells.append(base_cell)

# ==========================================
# 5. 재구성된 Cell 시각화 및 JSON 결과 저장
# ==========================================
draw = ImageDraw.Draw(image)

print(f"\n=== [분석 완료: 총 {len(final_cells)}개의 Cell 구조 재구성] ===")
for cell in final_cells:
    draw.rectangle(cell, outline="blue", width=3) # 시각적 구분을 위해 파란색으로 변경

output_filename = "tatr_cell_result.jpg"
image.save(output_filename)
print(f"✅ 셀 시각화 완료! '{output_filename}' 저장됨.")

# 👈 [추가] 평가 시스템용 JSON 저장!
json_filename = "tatr_result.json"
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(final_cells, f, indent=2)
print(f"✅ 정량 평가용 좌표 저장 완료! '{json_filename}' 저장됨.")