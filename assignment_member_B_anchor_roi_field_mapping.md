# 가은 학우 (추가 인원 B) 현재 작업 — GT / Dataset Manager

> 담당자 확정: 2026-11-01
> **최신 상세 작업 지시:** `05_current_team_tasks_20261101.md`
> 데이터/GT 세부 규칙: `04_data_collection_gt_protocol.md`

> 파일명에는 과거 역할명 `anchor_roi_field_mapping`이 남아 있지만, **현재 추가 인원 B의 역할은 Anchor ROI가 아니다. Anchor ROI는 `taegu` 담당이며, 가은 학우는 Dataset Manager를 맡는다.**

## 목표

희원·tail이 수집한 이미지를 단순한 사진 모음이 아니라 **평가 가능한 Dataset v1.0**으로 완성한다.

## 바로 해야 할 일

- [ ] `heewon`, `tail` 수집분을 받는다.
- [ ] 개인정보와 GPS EXIF 등 공개 위험을 확인한다.
- [ ] 파일명과 `image_id`를 통일한다.
- [ ] 모든 이미지에 `document_group_id`를 부여한다.
- [ ] `manifest.csv`에 촬영 조건을 정리한다.
- [ ] 모든 usable 이미지의 핵심 5필드 text GT를 작성·검수한다.
  - `address`
  - `deposit`
  - `contract_amount`
  - `lessor_name`
  - `lessee_name`
- [ ] 금액은 `raw_text`와 숫자 `normalized` 값을 함께 기록한다.
- [ ] bbox는 가능하면 추가하되, 시간이 부족하면 text GT를 먼저 끝낸다.
- [ ] 중복/누락/손상 이미지를 검사한다.
- [ ] development / holdout_test를 **`document_group_id` 단위**로 분리한다.
- [ ] 기존 공통 10장은 holdout으로 지정하지 않는다.
- [ ] 신규 데이터의 약 20~30% 또는 최소 1개 전체 문서 그룹을 holdout으로 보호한다.
- [ ] bang/taegu 코드·규칙 동결 전까지 holdout을 공개하지 않는다.
- [ ] Dataset v1.0을 동결하고 파일 목록/버전을 기록한다.

## 목표 폴더

```text
data/eval_v1/
  images/
  manifest.csv
  field_gt.json
  README.md
```

## `manifest.csv` 필수 컬럼

```text
image_id
document_group_id
filename
condition
perspective_direction
perspective_level
distance_level
lighting
fold
crop
usable
split
notes
```

## 중요 규칙

같은 원본 문서의 baseline을 development에 넣고 perspective 촬영본을 holdout에 넣으면 안 된다.

```text
X docA_baseline -> development
X docA_perspective -> holdout_test
```

반드시 같은 `document_group_id` 전체를 하나의 split에 둔다.

```text
O docA 전체 -> development
O docB 전체 -> development
O docC 전체 -> holdout_test
```

`split`은 가은 학우가 최종 확정한다.

## 완료 기준

다음이 모두 끝나면 완료다.

- 신규 usable 이미지 약 10~15장
- 최소 2~3개 `document_group_id`
- 각 이미지 촬영 조건 기록
- 핵심 5필드 GT 완료
- manifest / GT `image_id` 일치
- 개인정보/GPS 확인
- 중복/손상 확인
- group 단위 development/holdout 분리
- Dataset v1.0 동결

이후 가은 학우는 development를 bang/taegu에 전달하고, 두 담당자가 코드/규칙을 동결한 뒤에만 holdout_test를 공개한다.
