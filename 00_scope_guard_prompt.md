# 연구 범위 이탈 방지 기준 — 2026-10-08 개정

## 현재 논문 중심 주제

**정형 임대차계약서 핵심정보 추출 파이프라인의 단계별 오류 전파 분석: 이미지 품질, 구조 복원, ROI 설정, 문자 인식을 중심으로**

본 연구의 목적은 새로운 OCR 모델을 만드는 것이 아니라, 동일 데이터와 Ground Truth에서 다음 단계의 오류가 최종 Field Accuracy에 어떤 영향을 주는지 분리하여 정량적으로 비교하는 것이다.

```text
이미지 품질
  -> 문서 구조 복원
  -> 핵심 필드 ROI 설정
  -> OCR 문자 인식
  -> 정규화/검증
  -> 최종 Field Accuracy
```

## 새 작업을 시작하기 전 확인

새 기능, 모델, 실험을 추가하려면 아래 질문에 모두 답한다.

1. 이 작업이 이미지 품질 / 구조 복원 / ROI / 문자 인식 중 한 단계의 영향을 분리하는가?
2. 동일한 공통 데이터와 GT에서 비교 가능한가?
3. 최종적으로 Field Accuracy 또는 그 원인을 설명하는 지표와 연결되는가?
4. 2026-10-13 최종 마감 전 기존 비교표를 완성하는 데 필요한가?

하나라도 아니면 새 구현보다 기존 결과 정리와 통합을 우선한다.

## IN_SCOPE

- 원본 Full OCR baseline
- 원근 보정/기존 전처리 후 Full OCR
- PP-Structure / TATR / OpenCV 구조 복원 결과의 공통 GT 평가
- Ground Truth ROI OCR
- 실제 검출 ROI OCR
- Anchor-ROI 기반 필드 ROI 비교
- CER / Exact Match / confidence / Field Accuracy
- Cell IoU / Precision / Recall / F1
- ROI Coverage / ROI IoU / 필드 위치 성공률
- 실패 유형 분류
- 입력 이미지부터 최종 field JSON까지 End-to-End 재현
- 이미 구현된 경량 Guardrail의 보조적 검증

## OUT_OF_SCOPE / Future Work

- 새로운 YOLO / DETR / Faster R-CNN Cell Detector 학습
- Mask R-CNN 등 Instance Segmentation 추가
- 새 OCR 모델 학습/파인튜닝
- 대규모 신규 데이터셋 구축
- LLM 기반 새 추출 파이프라인 추가
- Guardrail을 별도 핵심 연구 주제로 확장
- 10월 8일 이후 새로운 실험축 추가

## 해석 원칙

- ROI가 항상 정확도를 높인다고 전제하지 않는다.
- OpenCV가 항상 구조 모델보다 우수하다고 전제하지 않는다.
- 실행 실패와 성능 실패를 구분한다.
- 좌표계가 다른 결과를 같은 evaluator에 넣지 않는다.
- Partial GT의 FP/Precision을 최종 성능으로 사용하지 않는다.
- 자동 ROI가 GT ROI보다 나쁘게 나오더라도 실패 자체를 연구 결과로 기록한다.
- 기대와 다른 결과를 숨기지 않고 어느 단계가 실제 병목인지 해석한다.

## 최종 논문에서 답해야 할 질문

> 이미지 품질, 구조 복원, ROI 설정, 문자 인식 중 어떤 단계가 임대차계약서 핵심정보 추출의 최종 Field Accuracy에 가장 큰 영향을 주며, 각 단계의 오류를 제거하거나 통제했을 때 성능이 어떻게 변하는가?
