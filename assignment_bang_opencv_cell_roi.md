# bang_ 현재 작업 — 자동 구조 복원 / Detected ROI

> 재설정일: 2026-10-21
> 상세 기준: `03_team_execution_plan_20261021.md`

## 목표
현재 OpenCV 구조 복원 파이프라인을 더 크게 수정하지 않고, 기존 10장과 Dataset v1.0에 **동일 설정으로 batch 실행**하여 Detected ROI 평가 입력을 공급한다.

## 해야 할 일
- [ ] 현재 파라미터와 실행 명령 고정
- [ ] 기존 공통 10장 결과 보존
- [ ] 신규 development 세트에 동일 설정으로 실행
- [ ] 이미지별 `cells_original.json`, `report.json` 생성
- [ ] 원본/보정 좌표 혼용 금지
- [ ] 핵심 5필드 기준 ROI Coverage 계산 가능하게 전달
- [ ] 실패 이유 기록: `TABLE_MISSING`, `ROW_MERGE`, `COLUMN_MERGE`, `CELL_MERGE`, `WRONG_MAPPING`, `COORDINATE_ERROR`
- [ ] 코드 동결 후 holdout_test에는 파라미터 변경 없이 실행

## 최종 산출물
```text
image_id/
  cells_original.json
  report.json
summary: image_id / target_fields / detected_fields / roi_coverage / failure_reason
```

## 하지 않을 것
- holdout 결과별 파라미터 튜닝
- 새 detector/model 추가
- 대규모 알고리즘 재설계
