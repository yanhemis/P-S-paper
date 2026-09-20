import json
import os

def calculate_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    return interArea / float(boxAArea + boxBArea - interArea) if (boxAArea + boxBArea - interArea) > 0 else 0

def evaluate_model(model_name, gt_data, pred_boxes, iou_thresholds, eval_mode="PARTIAL"):
    model_metrics = {}
    
    for thresh in iou_thresholds:
        print(f"\n[{model_name}] 📊 정량 평가 (IoU Threshold: {thresh} / 모드: {eval_mode})")
        
        # 전체 TP, FP, FN
        overall_stats = {"TP": 0, "FP": 0, "FN": 0}
        # 하위 그룹(Subset)별 매칭 추적
        subset_stats = {
            "general": {"total": 0, "matched": 0},
            "merged": {"total": 0, "matched": 0}
        }
        
        for gt in gt_data:
            subset_stats[gt["type"]]["total"] += 1

        iou_pairs = []
        for g_idx, gt in enumerate(gt_data):
            for p_idx, pred in enumerate(pred_boxes):
                iou = calculate_iou(gt["bbox"], pred)
                if iou > 0:
                    iou_pairs.append((g_idx, p_idx, iou))

        iou_pairs.sort(key=lambda x: x[2], reverse=True)
        matched_gt = set()
        matched_pred = set()

        # 1:1 Greedy Matching
        for g_idx, p_idx, iou in iou_pairs:
            if iou >= thresh:
                if g_idx not in matched_gt and p_idx not in matched_pred:
                    matched_gt.add(g_idx)
                    matched_pred.add(p_idx)
                    overall_stats["TP"] += 1
                    subset_stats[gt_data[g_idx]["type"]]["matched"] += 1

        overall_stats["FN"] = len(gt_data) - len(matched_gt)
        overall_stats["FP"] = len(pred_boxes) - len(matched_pred)

        # Partial 모드에서는 GT 대비 성공률(Recall)만 신뢰 가능
        g_total = subset_stats["general"]["total"]
        g_match = subset_stats["general"]["matched"]
        m_total = subset_stats["merged"]["total"]
        m_match = subset_stats["merged"]["matched"]
        
        g_recall = (g_match / g_total * 100) if g_total > 0 else 0
        m_recall = (m_match / m_total * 100) if m_total > 0 else 0
        
        print(f"  - General GT Subset Recall : {g_recall:.1f}% ({g_match}/{g_total})")
        print(f"  - Merged GT Subset Recall  : {m_recall:.1f}% ({m_match}/{m_total})")
        
        if eval_mode == "EXHAUSTIVE":
            TP, FP, FN = overall_stats["TP"], overall_stats["FP"], overall_stats["FN"]
            precision = (TP / (TP + FP) * 100) if (TP + FP) > 0 else 0
            recall = (TP / (TP + FN) * 100) if (TP + FN) > 0 else 0
            f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            print(f"  - [전체 셀] Precision: {precision:.1f}% | Recall: {recall:.1f}% | F1: {f1:.1f}%")
        else:
            print("  - ⚠️ Partial GT 모드이므로 전체 FP 및 Precision은 산출하지 않습니다.")

        model_metrics[str(thresh)] = {
            "general_recall": g_recall,
            "merged_recall": m_recall,
            "overall": overall_stats if eval_mode == "EXHAUSTIVE" else "N/A (Partial Mode)"
        }
    
    return model_metrics

if __name__ == "__main__":
    # --- 설정 영역 ---
    EVAL_MODE = "PARTIAL" 
    gt_path = 'sample.jpg_gt.json' 
    metrics_output_path = 'metrics.json'
    
    # 💡 [Priority 2] TATR Ablation 모델을 모두 평가 목록에 추가!
    models_to_evaluate = {
        "1. PP-Structure (Paddle 2.8.1)": "../1_PaddleOCR-PP-Structure/output/sample/res_0.txt",
        "2. TATR (Grid Only Ablation)": "../2_TATR/tatr_result_grid.json",
        "3. TATR (+ Spanning Recon)": "../2_TATR/tatr_result_spanning.json"
    }
    # ----------------

    if os.path.exists(gt_path):
        with open(gt_path, 'r', encoding='utf-8') as f:
            gt_data = json.load(f)
    elif os.path.exists('gt_sample.json'):
        with open('gt_sample.json', 'r', encoding='utf-8') as f:
            gt_data = json.load(f)
    else:
        gt_data = []
        print("❌ 정답지 파일이 없습니다. 라벨링을 먼저 진행하세요.")
        exit()

    all_results = {}

    for model_name, result_path in models_to_evaluate.items():
        pred_boxes = []
        if os.path.exists(result_path):
            with open(result_path, 'r', encoding='utf-8') as f:
                content = f.read()
                try:
                    data = json.loads(content)
                    # 1. PP-Structure 구조
                    if "res" in data and "cell_bbox" in data["res"]:
                        pred_boxes = data['res']['cell_bbox']
                    # 2. TATR Spanning 구조 (딕셔너리)
                    elif "reconstructed_cells" in data:
                        pred_boxes = [cell["bbox"] for cell in data["reconstructed_cells"]]
                    # 3. TATR Grid Only 구조 (표준 JSON 리스트)
                    elif isinstance(data, list) and len(data) > 0 and "bbox" in data[0]:
                        pred_boxes = [cell["bbox"] for cell in data]
                    # 구버전 호환용 (단순 좌표 리스트)
                    elif isinstance(data, list):
                        pred_boxes = data
                except Exception as e:
                    print(f"❌ {model_name} 파싱 에러: {e}")
                    
        if pred_boxes:
            all_results[model_name] = evaluate_model(
                model_name, gt_data, pred_boxes, 
                iou_thresholds=[0.3, 0.5, 0.7], 
                eval_mode=EVAL_MODE
            )
        else:
            print(f"❌ {model_name} 예측 결과를 찾을 수 없습니다.")

    with open(metrics_output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n✅ 평가 완료! 결과가 '{metrics_output_path}'에 저장되었습니다.")