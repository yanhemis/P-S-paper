# tail 현재 작업 — 난이도 촬영 / 이미지 품질 메타데이터

> 재설정일: 2026-10-21
> 상세 기준: `03_team_execution_plan_20261021.md`, `04_data_collection_gt_protocol.md`

## 목표
기존 OCR/H1 분석 경험을 활용해 실제 실패를 유발할 수 있는 촬영 조건을 의도적으로 수집하고, 조건을 정확히 기록한다. 이번 재배정의 주업무는 OCR 모델 개발이 아니다.

## 해야 할 일
- [ ] 가능하면 heewon과 같은 원본 문서 그룹 일부를 공유해 조건 비교쌍 만들기
- [ ] 우선 조건: `perspective`, `distance`, `lighting`, `fold_or_crop`
- [ ] 사람이 실제 스마트폰으로 촬영할 법한 현실적인 수준 유지
- [ ] 촬영 후 보정 없이 원본 제출
- [ ] 목표: 신규 usable 5~8장
- [ ] 실패 가능성이 높은 이미지도 삭제하지 말고 `usable`과 이유 기록
- [ ] 기존 H1의 거리/접힘/가장자리 해석과 연결되도록 메타데이터 작성

## 권장 조건
```text
perspective: 좌/우/상단 사선, mild/moderate
distance: 글자는 읽히지만 유효 해상도가 떨어지는 거리
lighting: 낮은 조도 또는 한쪽 조명/약한 그림자
fold_or_crop: 약한 접힘/휨 또는 가장자리 소량 누락
```

## 전달물
- 원본 이미지
- condition / level / notes
- `document_group_id`
- unusable이면 그 이유

GT 작성과 최종 development/holdout 분리는 추가 인원 B가 관리한다.
