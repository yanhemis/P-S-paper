import cv2
import json
import os

IMAGE_PATH = "sample.jpg"
GT_PATH = "field_gt.json"

# 화면에 표시할 배율
DISPLAY_SCALE = 0.25

FIELDS = [
    "소재지",
    "임대인_성명",
    "임차인_성명",
    "보증금",
    "계약금"
]

image = cv2.imread(IMAGE_PATH)

if image is None:
    print("이미지를 불러오지 못했습니다.")
    exit()

with open(GT_PATH, "r", encoding="utf-8") as f:
    gt_data = json.load(f)

image_name = os.path.basename(IMAGE_PATH)

if image_name not in gt_data:
    print("field_gt.json에 이미지 정보가 없습니다.")
    exit()


# 라벨링용 축소 이미지
display_image = cv2.resize(
    image,
    None,
    fx=DISPLAY_SCALE,
    fy=DISPLAY_SCALE,
    interpolation=cv2.INTER_AREA
)

print("===== Field GT BBox Labeling =====")
print("실제 값 영역만 드래그하세요.")
print("선택 후 ENTER 또는 SPACE")
print()


for field in FIELDS:

    print(f"\n현재 필드: {field}")
    print(f"정답값: {gt_data[image_name][field]['value']}")

    window_name = f"GT Label - {field}"

    x, y, w, h = cv2.selectROI(
        window_name,
        display_image,
        showCrosshair=True,
        fromCenter=False
    )

    cv2.destroyWindow(window_name)

    if w == 0 or h == 0:
        print("선택되지 않았습니다.")
        continue

    # 축소 화면 좌표 -> 원본 이미지 좌표
    original_x1 = int(x / DISPLAY_SCALE)
    original_y1 = int(y / DISPLAY_SCALE)
    original_x2 = int((x + w) / DISPLAY_SCALE)
    original_y2 = int((y + h) / DISPLAY_SCALE)

    bbox = [
        original_x1,
        original_y1,
        original_x2,
        original_y2
    ]

    gt_data[image_name][field]["bbox"] = bbox

    print("원본 기준 bbox:", bbox)


with open(GT_PATH, "w", encoding="utf-8") as f:
    json.dump(
        gt_data,
        f,
        ensure_ascii=False,
        indent=2
    )

cv2.destroyAllWindows()

print("\nGT bbox 저장 완료")
print(GT_PATH)