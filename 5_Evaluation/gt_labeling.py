import cv2
import os
import json

drawing = False
ix, iy = -1, -1
current_box = []
img, clone = None, None
gt_list = [] # 저장된 정답 리스트

# 화면을 현재 상태(저장된 박스들)로 다시 그리는 함수
def redraw_all():
    global img
    img = clone.copy()
    for gt in gt_list:
        box = gt["bbox"]
        # 일반은 파란색, 병합은 주황색으로 표시
        color = (255, 0, 0) if gt["type"] == "general" else (0, 165, 255)
        cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), color, 2)
    cv2.imshow('GT Labeling', img)

def draw_box(event, x, y, flags, param):
    global ix, iy, drawing, current_box, img
    
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_temp = img.copy()
            cv2.rectangle(img_temp, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow('GT Labeling', img_temp)
            
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        xmin, ymin = min(ix, x), min(iy, y)
        xmax, ymax = max(ix, x), max(iy, y)
        current_box = [xmin, ymin, xmax, ymax]
        
        cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)
        cv2.imshow('GT Labeling', img)
        print(f"\n[안내] 🟥 박스 그려짐! (저장: 'g' 또는 'm' / 이 박스 취소: 'r')")

img_path = '../sample.jpg' if os.path.exists('../sample.jpg') else 'sample.jpg'
img = cv2.imread(img_path)
if img is None:
    print("❌ 이미지 없음")
    exit()

clone = img.copy()
cv2.namedWindow('GT Labeling', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('GT Labeling', draw_box)

print("="*50)
print("🎯 GT 추출기 (업그레이드 버전)")
print(" - [g] : 일반 셀 저장")
print(" - [m] : 병합 셀 저장")
print(" - [r] : 방금 드래그한 빨간 박스 취소")
print(" - [z] : 실수로 저장한 마지막 셀 삭제 (Ctrl+Z 역할)")
print(" - [q] : 모두 완료 및 JSON 코드 출력")
print("="*50)

while True:
    cv2.imshow('GT Labeling', img)
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('g') and current_box:
        gt_list.append({"bbox": current_box, "type": "general"})
        print("✅ 일반 셀 저장 완료!")
        current_box = []
        redraw_all()
        
    elif key == ord('m') and current_box:
        gt_list.append({"bbox": current_box, "type": "merged"})
        print("✅ 병합 셀 저장 완료!")
        current_box = []
        redraw_all()
        
    elif key == ord('r'): # 그리기 취소
        current_box = []
        redraw_all()
        print("🗑️ 방금 그린 박스 취소됨.")
        
    elif key == ord('z'): # 뒤로 가기 (실행 취소)ㅂ
        if gt_list:
            removed = gt_list.pop()
            print(f"↩️ 되돌리기: {removed['type']} 셀 삭제됨!")
            current_box = []
            redraw_all()
        else:
            print("⚠️ 삭제할 셀이 없습니다.")
            
    elif key == ord('q'):
        break

cv2.destroyAllWindows()
print("\n🎉 [완료] 아래 [ ] 안의 텍스트를 gt_sample.json에 복붙하세요!\n")
print(json.dumps(gt_list, indent=2, ensure_ascii=False))