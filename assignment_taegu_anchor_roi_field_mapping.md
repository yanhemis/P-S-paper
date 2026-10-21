# taegu 현재 작업 — Anchor Field ROI + 최소 End-to-End

> 재설정일: 2026-10-21
> 상세 기준: `03_team_execution_plan_20261021.md`

## 목표
핵심 5필드 Anchor ROI 규칙을 development 데이터에서 고정하고, 입력 이미지가 `final_fields.json`까지 이어지는 최소 실행 경로를 만든다.

## 핵심 필드
- `address`
- `deposit`
- `contract_amount`
- `lessor_name`
- `lessee_name`

## 해야 할 일
- [ ] Anchor 규칙은 development 데이터에서만 보완
- [ ] ROI별 `field`, `bbox`, `method`, 가능하면 `confidence` 저장
- [ ] ROI bbox를 이미지 경계 안으로 clipping
- [ ] 금액 후보는 위치와 금액 형식을 함께 확인
- [ ] 실패 이유 기록: `ANCHOR_NOT_FOUND`, `WRONG_ANCHOR`, `MIXED_ROWS`, `ROI_TOO_LARGE`, `ROI_TOO_SMALL`, `OCR_FAILURE`
- [ ] 기존 OCR과 연결해 `input -> ROI -> OCR -> normalization -> final_fields.json` 최소 경로 완성
- [ ] 코드 동결 후 holdout_test에는 새 예외 규칙 추가 금지

## 완료 기준
모든 이미지 성공이 목표가 아니다. 필드별 성공/실패와 Coverage를 남기고, 충분한 정량 결과가 없으면 P4는 PoC로 유지한다.
