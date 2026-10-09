# 표 구조 복원 성능 비교 — 좌표계 감사 반영 결과 (RQ2)

## 1. 평가 설정

본 평가는 동일한 계약서 이미지 `sample.jpg`에서 추출된 표 구조 복원 결과를 비교하였다.

- 평가 이미지: `sample.jpg`
- 공통 Exhaustive GT: 총 95개 셀
  - General GT: 50개
  - Merged GT: 45개
- 평가 범위: GT가 구축된 상단 및 하단 표 영역 2개
- IoU 임계값: 0.3, 0.5, 0.7
- 매칭 방식: IoU 기반 1:1 Greedy Matching
- 예측 선택 기준: 예측 BBox 중심점이 GT 기반 평가 영역에 포함되는 경우
- 평가 좌표계: EXIF 방향을 반영한 3000 × 4000 이미지 좌표계

## 2. F1 정량 비교 (%)

| 평가군 | IoU 0.3 | IoU 0.5 | IoU 0.7 | 검증 상태 |
|---|---:|---:|---:|---|
| PP-Structure | 5.9 | 0.0 | 0.0 | Overlay 점검 완료 |
| TATR Grid Only | 26.0 | 3.0 | 0.0 | 좌표 변환 및 Overlay 점검 완료 |
| TATR + Spanning Reconstruction | 26.0 | 3.0 | 0.0 | 좌표 변환 및 Overlay 점검 완료 |
| OpenCV Primitive Grid | 49.7 | 38.7 | 25.8 | 과거 Affine 적용 및 정량 재평가 완료 |
| OpenCV + Cell Reconstruction | 88.4 | 77.3 | 65.2 | 과거 Affine 적용, Overlay 점검 및 정량 재평가 완료 |

모든 지표는 동일한 95개 GT와 지정된 두 표 영역에 대해 계산하였다.

## 3. 주요 감사 결과

1. PP-Structure, TATR Grid, TATR Spanning, OpenCV Primitive 및 OpenCV Restored의 다섯 평가 입력을 정상적으로 처리하였다.
2. TATR Grid와 Spanning Reconstruction은 지정된 평가 영역에서 동일한 Precision, Recall 및 F1을 보였다. 이 결과만으로 모든 예측 BBox와 셀 유형이 동일하다고 단정하지 않는다.
3. 과거 OpenCV 예측 파일에는 회전각 -1.061°가 기록되어 있으며, Git 커밋 `f352da0`에서 과거 실행 보고서와 정렬 이미지의 존재를 확인하였다.
4. 과거 실행 보고서에서 캔버스 확장 및 이동 보정이 포함된 Affine Matrix를 확보하였다.
5. 해당 Affine Matrix의 역변환을 이용하여 OpenCV Primitive 231개와 Restored 86개의 예측 BBox를 공통 GT 좌표계로 변환하였다.
6. 수정된 정식 OpenCV 입력 파일로 정량 평가를 재실행하였으며, 별도의 Affine 감사 평가와 동일한 결과를 확인하였다.
7. 다섯 평가군과 세 IoU 임계값의 총 15개 평가 조합에서 `TP + FN = 95`가 성립하였다.
8. 현재 OpenCV 파이프라인의 재실행은 Grid extraction 단계에서 실패했으며, 과거 예측의 생성 과정은 완전히 재현되지 않았다.
9. General 및 Merged GT Localization Recall은 위치 매칭 지표이며, 예측 셀 유형의 분류 정확도가 아니다.

## 4. 결과 해석 및 제한 사항

과거 Affine Matrix를 적용한 좌표 보정 후 OpenCV 평가 지표가 크게 변경되었다. 따라서 수정 전의 회전각 기반 좌표 변환으로 계산된 OpenCV 결과는 최종 정량 비교의 근거로 사용하지 않는다.

IoU 0.5에서 OpenCV Primitive의 F1은 38.7%, Restored의 F1은 77.3%로 관찰되었다. 이는 해당 평가 이미지에서 두 출력 방식의 위치 매칭 성능에 차이가 있었음을 의미한다. 그러나 이 차이를 병합 셀 재구성 처리만의 독립적인 인과 효과로 단정하지 않는다.

TATR Grid와 Spanning Reconstruction의 정량 지표는 동일하였으나, 이러한 관찰만으로 Spanning Reconstruction이 다른 이미지에서도 효과가 없다고 판단할 수 없다.

또한 다음 제한 사항을 적용한다.

- 평가는 단일 계약서 이미지의 두 표 영역에 한정된다.
- 예측 선택에 적용한 영역 필터링 규칙이 지표에 영향을 줄 수 있다.
- 과거 예측 파일의 좌표 변환 및 정량 평가 재현과 현재 파이프라인의 전체 실행 재현은 구분해야 한다.
- Merged GT Localization Recall을 병합 관계의 정확한 복원율이나 Merged Cell Accuracy로 표현하지 않는다.
- RQ2의 구조 복원 지표만으로 후속 ROI, OCR 또는 최종 Field Accuracy에 대한 인과적 영향을 확정하지 않는다.
- 측정된 결과를 다른 계약서나 데이터셋에서의 일반적인 모델 성능 순위로 확대 해석하지 않는다.

## 5. 최종 상태

**좌표계 감사 반영 및 정량 재평가 완료**

- 공통 GT 95개: 확인 완료
- 과거 OpenCV 예측 파일 출처: 확인 완료
- 과거 Affine Matrix: 확보 완료
- OpenCV 좌표 변환: 수정 완료
- 정식 입력 기반 정량 재평가: 완료
- 현재 OpenCV 파이프라인 전체 실행 재현: 실패
- 다른 문서에 대한 일반화: 검증되지 않음

최신 정량 지표는 `metrics_affine_audit.json`, 좌표 변환 및 재현성의 상세 근거는 `coordinate_audit.md`를 기준으로 한다.

수정 전 결과가 담긴 `metrics_audit_draft.json`은 감사 이력을 위한 과거 기록으로 구분하며, 최종 OpenCV 성능 수치의 출처로 사용하지 않는다.