import layoutparser as lp
import cv2

# 1. 계약서 원본 이미지 불러오기 (OpenCV 활용)
image_path = "sample.jpg"
image = cv2.imread(image_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # RGB로 변환

# 2. LayoutParser 사전 훈련된 모델 불러오기 
# (PubLayNet 데이터셋으로 학습된 기본 모델을 활용해 문서 영역 검출)
print("LayoutParser 모델을 불러오는 중입니다...")
model = lp.Detectron2LayoutModel(
    'lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config', 
    extra_config=["MODEL.WEIGHTS", "https://huggingface.co/layoutparser/detectron2/raw/main/faster_rcnn_R_50_FPN_3x/model_final.pth"],
    label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}
)

# 3. 문서 레이아웃 검출 실행
layout = model.detect(image)

print(f"\n=== [검출된 문서 영역 개수: {len(layout)}개] ===")
for block in layout:
    print(f"종류: {block.type} | 정확도: {round(block.score, 3)} | 좌표: {block.coordinates}")

# 4. 검출된 영역을 이미지 위에 시각화하기
viz_image = lp.draw_box(image, layout, box_width=3, show_box_label=True)

# 5. 결과 이미지 저장 (다시 BGR로 변환하여 저장)
viz_image = cv2.cvtColor(viz_image, cv2.COLOR_RGB2BGR)
cv2.imwrite("layout_result.jpg", viz_image)
print("\n✅ 분석 완료! layout_result.jpg 파일이 저장되었습니다.")
