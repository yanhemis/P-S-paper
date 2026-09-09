import json
import os

# 1. IoU(겹침 비율) 계산 함수
def calculate_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    iou = interArea / float(boxAArea + boxBArea - interArea) if (boxAArea + boxBArea - interArea) > 0 else 0
    return iou

# 2. 모델 평가 함수 (일반 / 병합 분리)
def evaluate_model(gt_data, pred_boxes, iou_threshold=0.5):
    results = {"general": {"match": 0, "total": 0}, "merged": {"match": 0, "total": 0}}
    
    for gt in gt_data:
        gt_box = gt["bbox"]
        cell_type = gt["type"]
        results[cell_type]["total"] += 1
        
        best_iou = 0
        for pred_box in pred_boxes:
            iou = calculate_iou(gt_box, pred_box)
            if iou > best_iou:
                best_iou = iou
        
        if best_iou >= iou_threshold:
            results[cell_type]["match"] += 1

    print("=== 📊 정량 평가 결과 (IoU Threshold: 0.5) ===")
    for c_type in ["general", "merged"]:
        match = results[c_type]["match"]
        total = results[c_type]["total"]
        recall = (match / total * 100) if total > 0 else 0
        print(f"* {c_type.capitalize()} Cell 점수: {recall:.1f}% ({match}/{total}개 일치)")

# --- [실행 테스트] ---
if __name__ == "__main__":
    # 1. 내가 만든 진짜 정답지 로드
    with open('gt_sample.json', 'r', encoding='utf-8') as f:
        gt_data = json.load(f)
    
    # 2. 아까 뽑아둔 PP-Structure 예측 결과 로드
    pp_result_path = '../1_PaddleOCR-PP-Structure/output/sample/res_0.txt'
    
    if os.path.exists(pp_result_path):
        with open(pp_result_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # JSON 파싱 
            try:
                pp_data = json.loads(content)
                pred_boxes = pp_data['res']['cell_bbox']
                print(f"✅ PP-Structure 결과 로드 완료! (모델이 예측한 총 네모 칸: {len(pred_boxes)}개)\n")
            except Exception as e:
                print(f"❌ 데이터 읽기 실패: {e}")
    else:
        print(f"❌ '{pp_result_path}' 경로에 결과 파일이 없습니다.")
        pred_boxes = []
    
    # 3. 진짜 채점 시작!
    if pred_boxes:
        evaluate_model(gt_data, pred_boxes)