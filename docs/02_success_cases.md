# 대표 성공 사례 (OpenCV Grid + Spanning Reconstruction)

- 이미지: sample.jpg (휴대폰 촬영 임대차계약서, 3000x4000)
- 평가: dahye 공통 evaluator(evaluate.py), sample.jpg_gt.json (GT 95셀), 예측 = cells_original.json (원본 좌표)
- 전체 결과 (IoU 0.5): Precision 90.7% / Recall 82.1% / F1 86.2%

## S1. 세로 병합 셀 복원
- 상황: 하단 서명 표의 "임대인·임차인·공인중개사" 칸과 "(인)" 칸은 여러 행이 세로로 합쳐진 셀
- 결과: primitive 격자 3~5칸을 하나의 merged 셀로 정확히 복원
- 근거 (IoU): 임차인 칸 id 48 (3행 병합) 0.94 / (인) 칸 id 35 (3행) 0.94 / 공인중개사 칸 id 64 (5행) 0.86 / 임대인 칸 id 32 (3행) 0.84
- 그림: ![S1](img/S1_vertical.png)

## S2. 가로 병합 셀 복원
- 상황: 상단 표의 값 칸은 위 행의 열 구분선 때문에 격자상 여러 칸으로 쪼개져 있음
- 결과: 내부 경계가 없는 칸을 Union-Find로 묶어 실제 칸 하나로 복원
- 근거 (IoU): "4층 401호 전체" id 18 (4칸 병합) 0.91 / "철근콘크리트 7조·공동주택" id 14 (3칸) 0.85 / 임대할부분 면적 id 20 (4칸) 0.84 / 제1조 안내문 id 0 (11칸) 0.80
- 그림: ![S2](img/S2_horizontal.png)

## S3. 병합 복원의 효과 (Ablation)
| 방법 (IoU 0.5) | Precision | Recall | F1 | Merged Recall |
|---|---|---|---|---|
| Grid only (cells_primitive) | 28.1% | 68.4% | 39.9% | 40.0% |
| Grid + Spanning Recon (cells) | 90.7% | 82.1% | 86.2% | 77.8% |
- 해석: 격자만 쓰면 병합 셀이 잘게 쪼개져 FP가 166개 → 병합 복원 후 8개로 감소
- 그림: ![S3](img/S3_ablation.png)

## S4. 촬영본 자동 전처리
- 상황: 휴대폰 촬영본, 약 1° 기울어짐, 본문에 밑줄·서명선 다수
- 결과: 기울기 -1.06° 자동 보정 (보정 후 잔여 0.00°), 표 2개 자동 분리, 표에 붙지 않은 본문 밑줄은 grid에서 제외
- 근거: report.json (rotation_deg, deskew.residual_deg), 자동 검증 7개 항목 모두 0건
- 그림: ![S4](img/S4_deskew.png)