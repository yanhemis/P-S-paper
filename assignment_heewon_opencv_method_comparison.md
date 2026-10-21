# heewon 현재 작업 — 정상/통제 촬영 데이터 수집

> 재설정일: 2026-10-21
> 상세 기준: `03_team_execution_plan_20261021.md`, `04_data_collection_gt_protocol.md`

## 목표
기존 구조 실험 확장 대신, 논문 RQ1과 최종 평가에 사용할 **정상 기준 + 통제된 반복 촬영 데이터**를 만든다.

## 해야 할 일
- [ ] 연구용/가상 계약서 준비
- [ ] 가능하면 2개 이상의 서로 다른 `document_group_id` 확보
- [ ] 각 문서 그룹에 최소 1장 baseline 촬영
- [ ] 동일 문서를 perspective/distance 등 조건만 바꿔 반복 촬영
- [ ] 촬영 후 crop/filter/밝기/원근 보정 금지
- [ ] 원본 파일 유지
- [ ] 목표: 신규 usable 5~6장
- [ ] 각 이미지의 `document_group_id`, condition, notes를 manifest에 기록

## baseline 기준
- 정면에 가깝게 촬영
- 문서 전체 포함
- 초점 양호
- 조명 양호
- 큰 그림자/가장자리 누락 없음

## 파일명 예
```text
docA_baseline_01.jpg
docA_perspective_01.jpg
docA_distance_far_01.jpg
docB_baseline_01.jpg
```

## 전달물
- 원본 이미지
- 촬영 조건 기록
- `document_group_id`
- 촬영 중 문제/비고

최종 GT와 split은 추가 인원 B가 관리한다.
