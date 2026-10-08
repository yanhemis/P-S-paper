# tail 최종 작업 — 이미지 품질 / OCR / 최종 Field Accuracy

> 재설정일: 2026-10-08
> 내부 마감: 2026-10-11

## 담당 목표

논문의 핵심 정량 담당. 기존 Full OCR / GT ROI OCR 결과를 기반으로 **각 단계가 최종 Field Accuracy에 미치는 영향을 같은 기준으로 비교**한다.

## 유지할 기존 결과

- Full OCR baseline 10장
- GT ROI OCR 10장
- CER / Exact Match / confidence
- Field Accuracy
- sec/image
- H1 이미지 품질 분석

## 추가로 해야 할 일

### E0 — Raw Full OCR
- [ ] 기존 결과 최종값 확정

### E1 — Image-corrected Full OCR
- [ ] 원근 보정/기존 전처리 Full OCR 결과 확정
- [ ] E0 대비 Field Accuracy/CER 변화 정리

### E3 — GT ROI OCR
- [ ] 기존 oracle ROI 결과 최종값 확정

### E4 — Detected ROI OCR
- [ ] `bang_` 또는 최종 자동 ROI 결과 수신
- [ ] 같은 OCR 조건으로 실행
- [ ] Field Accuracy / CER / confidence 계산

### E5 — Anchor ROI OCR
- [ ] `taegu` 10장 ROI가 오면 실행
- [ ] 미완료 시 공통 sample PoC만 유지

## 최종 핵심 표

| Pipeline | Image correction | ROI source | Field Accuracy | CER | sec/image |
|---|---|---|---:|---:|---:|
| P0 | X | Full page | 값 | 값 | 값 |
| P1 | O | Full page | 값 | 값 | 값 |
| P2 | 조건 고정 | GT ROI | 값 | 값 | 값 |
| P3 | 조건 고정 | Detected ROI | 값 | 값 | 값 |
| P4 | 조건 고정 | Anchor ROI | 가능 시 | 가능 시 | 가능 시 |

## 오류 분석

- 이미지 품질로 설명되는 오류
- 구조/ROI localization 오류
- ROI crop 혼입/잘림 오류
- 구조/ROI가 맞아도 남는 Recognition 오류

특히 GT ROI에서도 실패한 필드는 문자 인식 병목 후보로 분류한다.

## 하지 않을 것

- Cell Detection 알고리즘 수정
- Anchor 규칙 재설계
- 새 OCR 모델 학습

## 완료 기준

논문에서 다음 질문에 숫자로 답할 수 있어야 한다.

> 이미지 보정, 구조/ROI localization, 문자 인식 단계 중 어떤 단계를 통제했을 때 Field Accuracy가 얼마나 변하는가?
