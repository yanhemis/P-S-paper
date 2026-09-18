import cv2
import os
import json

drawing = False
ix, iy = -1, -1
temp_box = None
gt_list = []
cell_counter = 1
image_filename = 'sample.jpg'

img_path = f'../{image_filename}' if os.path.exists(f'../{image_filename}') else image_filename
base_img = cv2.imread(img_path)
if base_img is None:
    print(f"❌ '{img_path}' 이미지를 찾을 수 없습니다.")
    exit()

def get_rendered_image():
    """저장된 모든 박스와 현재 드래그 중인 박스를 base_img 위에 합성하여 반환"""
    display = base_img.copy()
    
    # 1. 이미 저장 확정된 박스들 그리기
    for item in gt_list:
        b = item["bbox"]
        # 일반: 파란색, 병합: 주황색
        color = (255, 100, 0) if item["type"] == "general" else (0, 140, 255)
        cv2.rectangle(display, (b[0], b[1]), (b[2], b[3]), color, 3)
        label = f"ID:{item['cell_id']} ({item['type'][0].upper()})"
        cv2.putText(display, label, (b[0], max(20, b[1] - 8)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
        
    # 2. 현재 마우스로 그리는 중인 박스 (초록색)
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
        
        # 너무 작은 클릭 오작동 방지 (가로/세로 5px 이상)
        if (xmax - xmin) > 5 and (ymax - ymin) > 5:
            temp_box = [xmin, ymin, xmax, ymax]
            print(f"\n[대기] 박스 선택 완료: {temp_box}")
            print("👉 'g' (일반) 또는 'm' (병합) 눌러 확정 (취소하려면 빈 곳 클릭)")
        else:
            temp_box = None
        cv2.imshow('GT Labeling', get_rendered_image())

cv2.namedWindow('GT Labeling', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('GT Labeling', draw_box)

print("="*55)
print("🎯 GT 라벨링 도구 조작 가이드")
print("="*55)
print(" 1. 마우스 좌클릭 드래그 : 박스 지정 (초록색)")
print(" 2. 키보드 [g] 입력      : 일반 셀 (General) 저장")
print(" 3. 키보드 [m] 입력      : 병합 셀 (Merged) 저장")
print(" 4. 키보드 [z] 입력      : 직전 저장된 박스 1개 삭제 (실행 취소)")
print(" 5. 키보드 [r] 입력      : 전체 박스 초기화 (처음부터 다시)")
print(" 6. 키보드 [q] 입력      : 라벨링 종료 및 JSON 터미널 출력")
print("="*55)

cv2.imshow('GT Labeling', get_rendered_image())

while True:
    # 30ms 단위 대기하여 키 입력 반응성 확보
    key = cv2.waitKey(30) & 0xFF

    if key == 27:  # ESC 키로도 종료 가능
        break

    # 일반 셀 저장
    if key == ord('g'):
        if temp_box is not None:
            gt_list.append({
                "image_id": image_filename,
                "cell_id": cell_counter,
                "type": "general",
                "bbox": temp_box
            })
            print(f"✅ [저장 완료] 일반 셀 - ID: {cell_counter}")
            cell_counter += 1
            temp_box = None
            cv2.imshow('GT Labeling', get_rendered_image())
        else:
            print("⚠️ 드래그된 박스가 없습니다.")

    # 병합 셀 저장
    elif key == ord('m'):
        if temp_box is not None:
            gt_list.append({
                "image_id": image_filename,
                "cell_id": cell_counter,
                "type": "merged",
                "bbox": temp_box
            })
            print(f"✅ [저장 완료] 병합 셀 - ID: {cell_counter}")
            cell_counter += 1
            temp_box = None
            cv2.imshow('GT Labeling', get_rendered_image())
        else:
            print("⚠️ 드래그된 박스가 없습니다.")

    # 직전 1개 취소 (z)
    elif key == ord('z'):
        if gt_list:
            removed = gt_list.pop()
            cell_counter -= 1
            temp_box = None
            print(f"↩️ [실행 취소] ID: {removed['cell_id']} ({removed['type']}) 삭제됨")
            cv2.imshow('GT Labeling', get_rendered_image())
        else:
            temp_box = None
            print("⚠️ 취소할 저장 데이터가 없습니다.")
            cv2.imshow('GT Labeling', get_rendered_image())

    # 전체 리셋 (r)
    elif key == ord('r'):
        gt_list.clear()
        cell_counter = 1
        temp_box = None
        print("🔄 [전체 초기화] 모든 박스가 삭제되었습니다. 처음부터 다시 지정하세요.")
        cv2.imshow('GT Labeling', get_rendered_image())

    # 완료 후 종료 (q)
    elif key == ord('q'):
        break

cv2.destroyAllWindows()

print("\n" + "="*50)
print(f"🎉 라벨링 완료 (총 {len(gt_list)}개 셀 지정)")
print("="*50)
print(json.dumps(gt_list, indent=2, ensure_ascii=False))