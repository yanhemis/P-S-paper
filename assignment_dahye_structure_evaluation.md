# dahye 현재 작업 — 최종 평가 총괄 / Evaluation Gatekeeper

> 재설정일: 2026-10-21
> 상세 기준: `03_team_execution_plan_20261021.md`

## 목표
기존 구조 평가와 `tail` OCR 결과, `bang_` Detected ROI, `taegu` Anchor ROI를 같은 GT/규칙으로 묶어 최종 논문 숫자를 확정한다.

## 해야 할 일
- [ ] 기존 RQ2 Affine 좌표계 감사 결과 유지
- [ ] 기존 tail E0/E1/E3/E4 결과 인수
- [ ] P0~P4의 field key, 분모, normalization 규칙 통일
- [ ] ROI 미생성 필드는 end-to-end Field Accuracy에서 실패 처리
- [ ] ROI Coverage와 ROI 존재 시 OCR 정확도를 분리 보고
- [ ] 신규 데이터 결과는 기존 10장과 별도 표를 먼저 작성
- [ ] 동일 `document_group_id` 반복 촬영을 독립 문서 표본처럼 해석하지 않음
- [ ] holdout은 bang/taegu 코드 동결 후 최종 평가

## 최종 표
| Pipeline | ROI source | ROI Coverage | Field Accuracy | CER | sec/image |
|---|---|---:|---:|---:|---:|
| P0 | Full page | - | 값 | 값 | 값 |
| P1 | Full page corrected | - | 값 | 값 | 값 |
| P2 | GT ROI | 100% | 값 | 값 | 값 |
| P3 | bang Detected ROI | 값 | 값 | 값 | 값 |
| P4 | taegu Anchor ROI | 가능 시 | 가능 시 | 가능 시 | 가능 시 |

## 평가 원칙
- 좌표계가 다른 prediction/GT 혼용 금지
- 실행 실패와 성능 실패 구분
- 이미지 수, 원본 문서 그룹 수, field instance 수 구분
- holdout 결과를 본 뒤 튜닝하면 더 이상 untouched final test로 부르지 않음
