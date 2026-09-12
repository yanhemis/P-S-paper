import json
import os

# 1. IoU 계산 함수
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

# 2. 1:1 매칭 및 평가 함수 (임계값 리스트를 인자로 받음)
def evaluate_model(gt_data, pred_boxes, iou_thresholds=[0.3, 0.5, 0.7]):
    
    # 3가지 IoU 임계값(0.3, 0.5, 0.7)에 대해 각각 평가 진행
    for thresh in iou_thresholds:
        print(f"\n==================================================")
        print(f"📊 정량 평가 결과 (IoU Threshold: {thresh})")
        print(f"==================================================")

        stats = {
            "general": {"TP": 0, "FP": 0, "FN": 0},
            "merged": {"TP": 0, "FP": 0, "FN": 0},
            "background": {"FP": 0} # 어떤 정답과도 겹치지 않은 잉여 박스
        }

        # [단계 A] 모든 GT-Pred 쌍의 IoU 계산
        iou_pairs = []
        for g_idx, gt in enumerate(gt_data):
            for p_idx, pred in enumerate(pred_boxes):
                iou = calculate_iou(gt["bbox"], pred)
                if iou > 0:
                    iou_pairs.append((g_idx, p_idx, iou))

        # [단계 B] 1:1 Greedy Matching을 위해 IoU가 높은 순으로 정렬
        iou_pairs.sort(key=lambda x: x[2], reverse=True)

        matched_gt = set()
        matched_pred = set()

        # [단계 C] 진짜 1:1 매칭 (TP 산출)
        for g_idx, p_idx, iou in iou_pairs:
            if iou >= thresh:
                # GT와 Pred 모두 아직 짝이 안 지어졌을 때만 매칭 성공!
                if g_idx not in matched_gt and p_idx not in matched_pred:
                    matched_gt.add(g_idx)
                    matched_pred.add(p_idx)
                    c_type = gt_data[g_idx]["type"]
                    stats[c_type]["TP"] += 1

        # [단계 D] 매칭 안 된 정답 (FN: 못 찾음)
        for g_idx, gt in enumerate(gt_data):
            if g_idx not in matched_gt:
                c_type = gt["type"]
                stats[c_type]["FN"] += 1

        # [단계 E] 매칭 안 된 예측 (FP: 오답 및 과분할 찌꺼기)
        for p_idx, pred in enumerate(pred_boxes):
            if p_idx not in matched_pred:
                # 이 쓰레기(FP)가 일반 칸을 쪼갠 건지, 병합 칸을 쪼갠 건지 추적
                best_iou = 0
                best_type = "background"
                for g_idx, gt in enumerate(gt_data):
                    iou = calculate_iou(gt["bbox"], pred)
                    if iou > best_iou:
                        best_iou = iou
                        best_type = gt["type"]

                if best_type in stats:
                    stats[best_type]["FP"] += 1
                else:
                    stats["background"]["FP"] += 1

        # [단계 F] 지표 계산 (Precision, Recall, F1)
        for c_type in ["general", "merged"]:
            TP = stats[c_type]["TP"]
            FP = stats[c_type]["FP"]
            FN = stats[c_type]["FN"]

            precision = (TP / (TP + FP)) * 100 if (TP + FP) > 0 else 0
            recall = (TP / (TP + FN)) * 100 if (TP + FN) > 0 else 0
            f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

            print(f"[{c_type.upper()} Cell]")
            print(f"  - TP(정답): {TP} | FP(오답/과분할): {FP} | FN(못찾음): {FN}")
            print(f"  - Precision (정밀도) : {precision:.1f}%")
            print(f"  - Recall    (재현율) : {recall:.1f}%")
            print(f"  - F1-Score  (종합)   : {f1_score:.1f}%\n")

        print(f"[BACKGROUND] 허공에 쳐진 잉여 박스(FP): {stats['background']['FP']}개\n")

if __name__ == "__main__":
    # 1. 정답지 로드
    gt_path = 'gt_sample.json'
    if os.path.exists(gt_path):
        with open(gt_path, 'r', encoding='utf-8') as f:
            gt_data = json.load(f)
    else:
        gt_data = []
        print(f"❌ '{gt_path}' 파일이 없습니다.")

    # 2. PP-Structure 예측 결과 로드
    pp_result_path = '../1_PaddleOCR-PP-Structure/output/sample/res_0.txt'
    pred_boxes = []
    
    if os.path.exists(pp_result_path):
        with open(pp_result_path, 'r', encoding='utf-8') as f:
            content = f.read()
            try:
                pp_data = json.loads(content)
                pred_boxes = pp_data['res']['cell_bbox']
                print(f"✅ PP-Structure 결과 로드 완료! (예측 박스: {len(pred_boxes)}개)")
            except Exception as e:
                print(f"❌ 데이터 파싱 실패: {e}")
    else:
        print(f"❌ 결과 파일이 없습니다: {pp_result_path}")

    # 3. 평가 실행 (0.3 / 0.5 / 0.7 민감도 비교)
    if gt_data and pred_boxes:
        evaluate_model(gt_data, pred_boxes, iou_thresholds=[0.3, 0.5, 0.7])

if __name__ == "__main__":
    # 1. 정답지(GT) 로드
    gt_path = 'gt_sample.json'
    if os.path.exists(gt_path):
        with open(gt_path, 'r', encoding='utf-8') as f:
            gt_data = json.load(f)
    else:
        gt_data = []
        print(f"❌ '{gt_path}' 파일이 없습니다.")

    # 2. 채점할 모델들의 결과 파일 경로 세팅
    models_to_evaluate = {
        "1. PP-Structure": "../1_PaddleOCR-PP-Structure/output/sample/res_0.txt",
        "2. TATR (Table Transformer)": "../2_TATR/tatr_result.json"  # 👈 TATR 결과 파일 이름에 맞게 수정 필요!
    }

    # 3. 모델별로 돌아가면서 채점 시작
    for model_name, result_path in models_to_evaluate.items():
        print(f"\n\n{'='*60}")
        print(f"🚀 [{model_name}] 모델 채점 시작!")
        print(f"{'='*60}")

        pred_boxes = []
        if os.path.exists(result_path):
            with open(result_path, 'r', encoding='utf-8') as f:
                content = f.read()
                try:
                    # PP-Structure 형식인 경우
                    if "res" in content and "cell_bbox" in content:
                        data = json.loads(content)
                        pred_boxes = data['res']['cell_bbox']
                    # TATR 형식인 경우 (리스트 형태라고 가정)
                    else:
                        pred_boxes = json.loads(content)
                    print(f"✅ {model_name} 결과 로드 완료! (예측 박스: {len(pred_boxes)}개)")
                except Exception as e:
                    print(f"❌ 데이터 파싱 실패: {e}")
        else:
            print(f"❌ 결과 파일이 없습니다: {result_path}")

        # 4. 채점 실행 (GT 데이터와 예측 박스가 모두 있을 때만)
        if gt_data and pred_boxes:
            evaluate_model(gt_data, pred_boxes, iou_thresholds=[0.3, 0.5, 0.7])    