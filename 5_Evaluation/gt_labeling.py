import cv2
import os
import json

drawing = False
ix, iy = -1, -1
temp_box = None
gt_list = []
cell_counter = 1
image_filename = 'sample.jpg'
json_filename = f"{image_filename}_gt.json" # 팀장님 권장 포맷

# --- 기존 라벨링 파일 불러오기 (이어서 작업하기) ---
if os.path.exists(json_filename):
    with open(json_filename, 'r', encoding='utf-8') as f:
        gt_list = json.load(f)
        if gt_list:
            # 마지막 cell_id 다음 번호부터 시작
            cell_counter = max([item["cell_id"] for item in gt_list]) + 1
            print(f"🔄 기존 라벨링 파일 로드 완료! (현재 {len(gt_list)}개 존재)")

img_path = f'../{image_filename}' if os.path.exists(f'../{image_filename}') else image_filename
base_img = cv2.imread(img_path)
if base_img is None:
    print(f"❌ '{img_path}' 이미지를 찾을 수 없습니다.")
    exit()

def get_rendered_image():
    display = base_img.copy()
    for item in gt_list:
        b = item["bbox"]
        color = (255, 100, 0) if item["type"] == "general" else (0, 140, 255)
        cv2.rectangle(display, (b[0], b[1]), (b[2], b[3]), color, 2)
        label = f"ID:{item['cell_id']} ({item['type'][0].upper()})"
        cv2.putText(display, label, (b[0], max(20, b[1] - 8)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)
        
    if temp_box is not None:
        cv2.rectangle(display, (temp_box[0], temp_box[1]), (temp_box[2], temp_box[3]), (0, 255, 0), 2)
    return display

def draw_box(event, x, y, flags, param):
    global ix, iy, drawing, temp_box

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        temp_box = [ix, iy, x, y]

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            xmin, ymin = min(ix, x), min(iy, y)
            xmax, ymax = max(ix, x), max(iy, y)
            temp_box = [xmin, ymin, xmax, ymax]
            cv2.imshow('GT Labeling', get_rendered_image())

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        xmin, ymin = min(ix, x), min(iy, y)
        xmax, ymax = max(ix, x), max(iy, y)
        
        if (xmax - xmin) > 5 and (ymax - ymin) > 5:
            temp_box = [xmin, ymin, xmax, ymax]
        else:
            temp_box = None
        cv2.imshow('GT Labeling', get_rendered_image())

cv2.namedWindow('GT Labeling', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('GT Labeling', draw_box)

print("="*55)
print("🎯 GT 라벨링 툴 (자동 저장 지원)")
print(" - [g] : 일반 셀 (General) 저장")
print(" - [m] : 병합 셀 (Merged) 저장")
print(" - [z] : 직전 저장된 박스 삭제 (실행 취소)")
print(" - [q] : 종료 및 JSON 자동 저장")
print("="*55)

cv2.imshow('GT Labeling', get_rendered_image())

while True:
    key = cv2.waitKey(30) & 0xFF
    if key == 27:
        break

    if key == ord('g'):
        if temp_box is not None:
            gt_list.append({"image_id": image_filename, "cell_id": cell_counter, "type": "general", "bbox": temp_box})
            cell_counter += 1
            temp_box = None
            cv2.imshow('GT Labeling', get_rendered_image())

    elif key == ord('m'):
        if temp_box is not None:
            gt_list.append({"image_id": image_filename, "cell_id": cell_counter, "type": "merged", "bbox": temp_box})
            cell_counter += 1
            temp_box = None
            cv2.imshow('GT Labeling', get_rendered_image())

    elif key == ord('z'):
        if gt_list:
            gt_list.pop()
            cell_counter -= 1
            temp_box = None
            cv2.imshow('GT Labeling', get_rendered_image())

    elif key == ord('q'):
        break

cv2.destroyAllWindows()

# --- 자동 저장 로직 ---
with open(json_filename, 'w', encoding='utf-8') as f:
    json.dump(gt_list, f, indent=2, ensure_ascii=False)

g_count = sum(1 for item in gt_list if item['type'] == 'general')
m_count = sum(1 for item in gt_list if item['type'] == 'merged')

print("\n" + "="*50)
print(f"🎉 라벨링 파일 저장 완료: '{json_filename}'")
print(f"📊 총 {len(gt_list)}개 셀 (General: {g_count}개 / Merged: {m_count}개)")
print("="*50)