# P-S-paper

# OpenCV Cell Detection Test

임대차계약서 이미지에서 표의 셀을 검출하기 위해
Morphology Grid 방식과 Contour 방식을 비교·평가하는 OpenCV 기반 실험입니다.

## 처리 흐름
1. 임대차계약서 이미지 전처리 및 표 영역 분석
2. Morphological Opening을 이용한 수평/수직 표선 검출 → 셀 Bounding Box 생성
3. Contour 기반 셀 Bounding Box 검출
4. 동일한 GT(`gt_sample.json`)를 기준으로 IoU 기반 정량 평가
5. Precision, Recall, F1 및 Bounding Box 개수 비교
6. 주요 파라미터 변화에 따른 검출 성능 및 실패 유형 분석

## 실험 내용
- Morphology Grid
  - h/v ratio: 0.03, 0.05, 0.08
- Contour
  - min width/height: 30/15, 50/20, 70/30
- IoU Threshold: 0.3, 0.5, 0.7

## 평가
동일한 GT를 기준으로 각 방법의 셀 검출 결과를 비교하며,
IoU Threshold에 따른 Precision, Recall, F1-Score를 측정합니다.

또한 다음과 같은 실패 유형을 분석합니다.
- 짧은 내부 선 누락
- 끊어진 선
- 희미한 선
- 텍스트 획 오검출
- 중복 contour
- 셀 내부 사각 요소 오검출
- 병합 셀 경계 미검출

## 출력
각 방법에서 검출된 Bounding Box 개수와
Precision, Recall, F1-Score 및 처리 시간을 비교하여
표 셀 검출 방식의 특성과 파라미터 민감도를 확인합니다.
