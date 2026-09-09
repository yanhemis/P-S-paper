from transformers import TableTransformerForObjectDetection, AutoImageProcessor
from PIL import Image, ImageDraw
import torch
import os

# 1. 이미지 불러오기 (최상위 경로에 있는 sample.jpg를 안전하게 불러오도록 경로 수정)
image_path = "../sample.jpg" if os.path.exists("../sample.jpg") else "sample.jpg"
try:
    image = Image.open(image_path).convert("RGB")
except FileNotFoundError:
    print(f"❌ 오류: '{image_path}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    exit()

# 2. Table Transformer 모델 및 프로세서 불러오기
print("모델을 불러오는 중입니다...")
processor = AutoImageProcessor.from_pretrained("microsoft/table-transformer-structure-recognition")
model = TableTransformerForObjectDetection.from_pretrained("microsoft/table-transformer-structure-recognition")

# 3. 이미지 전처리 및 모델 추론
inputs = processor(images=image, return_tensors="pt")
outputs = model(**inputs)

# 4. 결과 좌표 변환
target_sizes = torch.tensor([image.size[::-1]])
results = processor.post_process_object_detection(outputs, threshold=0.7, target_sizes=target_sizes)[0]

# ==========================================
# 💡 [핵심 추가 로직] TATR 결과에서 실제 Cell bbox 재구성
# ==========================================
rows = []
cols = []

# 4-1. 행(Row)과 열(Column) 좌표만 추출해서 각각의 리스트에 담기
for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
    box = [round(i, 2) for i in box.tolist()]
    label_name = model.config.id2label[label.item()]
    
    if label_name == "table row":
        rows.append(box)
    elif label_name == "table column":
        cols.append(box)

# 4-2. 추출한 좌표 정렬하기 (눈으로 읽는 순서대로)
# - 행(rows)은 위에서 아래로 (ymin 기준 정렬)
rows.sort(key=lambda x: x[1])
# - 열(cols)은 왼쪽에서 오른쪽으로 (xmin 기준 정렬)
cols.sort(key=lambda x: x[0])

# 4-3. 행과 열을 교차하여 셀(Cell) 좌표 계산하기
cells = []
for row in rows:
    for col in cols:
        # 셀 좌표 조합: [열의 x_min, 행의 y_min, 열의 x_max, 행의 y_max]
        cell_bbox = [col[0], row[1], col[2], row[3]]
        cells.append(cell_bbox)

# ==========================================
# 5. 재구성된 Cell 시각화 및 결과 저장
# ==========================================
draw = ImageDraw.Draw(image)

print(f"\n=== [분석 완료: 총 {len(cells)}개의 Cell 구조 재구성] ===")
# 계산된 네모 칸들을 원본 이미지 위에 빨간색 선으로 그리기
for cell in cells:
    draw.rectangle(cell, outline="red", width=2)

# 6. 새로운 결과 이미지 파일로 저장
output_filename = "tatr_cell_result.jpg"
image.save(output_filename)
print(f"✅ 셀 시각화 완료! '{output_filename}' 파일이 저장되었습니다.")