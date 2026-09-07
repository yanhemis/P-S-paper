from transformers import TableTransformerForObjectDetection, AutoImageProcessor
from PIL import Image, ImageDraw
import torch

# 1. 이미지 불러오기 (아까 사용한 계약서 원본 사진)
image_path = "sample.jpg" 
image = Image.open(image_path).convert("RGB")

# 2. Table Transformer 모델 및 프로세서 불러오기 (표 구조 분석 모델)
print("모델을 불러오는 중입니다. (최초 실행 시 다운로드에 시간이 걸릴 수 있습니다.)")
processor = AutoImageProcessor.from_pretrained("microsoft/table-transformer-structure-recognition")
model = TableTransformerForObjectDetection.from_pretrained("microsoft/table-transformer-structure-recognition")

# 3. 이미지 전처리 및 모델 추론
inputs = processor(images=image, return_tensors="pt")
outputs = model(**inputs)

# 4. 결과 좌표 변환 (원본 이미지 크기에 맞게)
target_sizes = torch.tensor([image.size[::-1]])
# threshold=0.7 은 정확도가 70% 이상인 구조만 걸러내겠다는 의미입니다.
results = processor.post_process_object_detection(outputs, threshold=0.7, target_sizes=target_sizes)[0]

# 5. 결과 그리기 준비
draw = ImageDraw.Draw(image)

print("\n=== [검출된 표 구조] ===")
for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
    box = [round(i, 2) for i in box.tolist()]
    label_name = model.config.id2label[label.item()]
    print(f"발견: {label_name} (정확도: {round(score.item(), 3)}) | 좌표: {box}")
    
    # 구조별로 선 색상을 다르게 칠하기
    if label_name == "table":
        color = "red"        # 표 전체는 빨간색
    elif label_name == "table row":
        color = "blue"       # 가로줄(행)은 파란색
    elif label_name == "table column":
        color = "green"      # 세로줄(열)은 초록색
    else:
        color = "orange"     # 기타(헤더 등)는 주황색
        
    draw.rectangle(box, outline=color, width=3)

# 6. 결과 이미지 저장
image.save("tatr_result.jpg")
print("\n✅ 분석 완료! tatr_result.jpg 파일이 저장되었습니다.")