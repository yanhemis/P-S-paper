# 추가 인원 B 현재 작업 — GT / Dataset Manager

> 재설정일: 2026-10-21
> 상세 기준: `03_team_execution_plan_20261021.md`, `04_data_collection_gt_protocol.md`

## 목표
수집된 이미지를 단순 모음이 아니라 **평가 가능한 Dataset v1.0**으로 만든다.

## 해야 할 일
- [ ] heewon/tail 수집분 통합
- [ ] 파일명과 `image_id` 통일
- [ ] 모든 이미지에 `document_group_id` 부여
- [ ] 핵심 5필드 text GT 작성/검수: `address`, `deposit`, `contract_amount`, `lessor_name`, `lessee_name`
- [ ] 금액은 `raw_text`와 숫자 `normalized` 값 함께 기록
- [ ] 가능하면 GT bbox 추가, 시간 부족 시 text GT 우선
- [ ] `manifest.csv` 완성
- [ ] 중복/누락/손상 이미지 확인
- [ ] development / holdout_test를 `document_group_id` 단위로 분리
- [ ] 기존 공통 10장은 holdout으로 지정하지 않음
- [ ] 신규 데이터 약 20~30% 또는 최소 1개 전체 문서 그룹을 holdout으로 보호
- [ ] Dataset v1.0 동결 후 파일 목록/버전 기록

## 목표 폴더
```text
data/eval_v1/
  images/
  manifest.csv
  field_gt.json
  README.md
```

## 중요 규칙
같은 원본 문서의 baseline을 development에 넣고 perspective 촬영본을 holdout에 넣으면 안 된다. 같은 `document_group_id`는 반드시 같은 split에 둔다.

## 완료 기준
모든 usable 이미지가 촬영 조건, document group, 핵심 5필드 GT, split 정보를 가지고 있어 bang/taegu/dahye가 별도 해석 없이 바로 사용할 수 있어야 한다.
