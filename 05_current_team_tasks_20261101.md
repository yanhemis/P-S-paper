# 2026-11-01 현재 팀 작업 지시 — 이 문서부터 확인

> **현재 최우선 작업 지시 문서.** 2026-10-21의 `03_team_execution_plan_20261021.md`와 과거 `assignment_*.md`보다 이 문서를 우선한다.
> 연구 방향 자체는 `01_research_direction_and_next_steps.md`, 데이터/GT 세부 규칙은 `04_data_collection_gt_protocol.md`를 따른다.

## 0. 지금 팀이 해야 하는 일 한 줄 요약

새 연구축을 늘리는 것이 아니라, **핵심 3명은 현재 파이프라인을 동결·연결·평가하고, 나머지 3명은 논문에 쓸 신규 데이터와 GT를 완성한다.**

최종 역할은 다음 6명으로 고정한다.

| 담당 | 현재 역할 | 지금 바로 할 일 | 최종 전달물 |
|---|---|---|---|
| `bang_` | OpenCV 구조 복원 / Detected ROI | 현재 코드·파라미터 고정 후 공통 10장 및 신규 development에 동일 설정 실행 | `cells_original.json`, `report.json`, ROI coverage용 summary |
| `taegu` | Anchor Field ROI / 최소 End-to-End | 핵심 5필드 Anchor ROI를 development에서만 보완 후 동결 | ROI 결과, `final_fields.json`, coverage/실패 사유 |
| `dahye_cell_DetectionSurvey` | 최종 평가 총괄 | P0~P4 평가 규칙·정규화·분모를 잠그고 bang/taegu 결과 통합 | 최종 비교표, failure breakdown, 논문용 수치 |
| `heewon` | 정상/통제 촬영 데이터 | 깨끗한 baseline 및 통제 조건 신규 데이터 5~6장 수집 | 원본 이미지 + 촬영 조건 기록 |
| `tail` | 난이도 촬영 / 품질 메타데이터 | perspective/distance/lighting/fold-or-crop 신규 데이터 5~8장 수집 | 원본 이미지 + 촬영 조건 기록 |
| **가은 학우 (추가 인원 B)** | **GT / Dataset Manager** | 희원·tail 수집분 통합, 5필드 GT와 manifest 작성, split/holdout 관리 | `manifest.csv`, `field_gt.json`, Dataset v1.0 |

---

# 1. 공통 원칙 — 먼저 이것부터 지킨다

1. **새 모델이나 새 연구축을 추가하지 않는다.** 현재 논문을 끝내는 것이 우선이다.
2. 기존 공통 10장은 이미 개발에 사용했으므로 **hold-out이 아니다.**
3. 신규 데이터는 약 **10~15장**, 최종 총량은 기존 10장을 포함해 약 **20~25장 수준**을 목표로 한다.
4. 동일 원본 계약서를 여러 조건으로 촬영했다면 같은 `document_group_id`로 묶는다.
5. development / holdout_test는 이미지가 아니라 **`document_group_id` 단위로 분리**한다.
6. 핵심 평가는 아래 5필드로 통일한다.
   - `address`
   - `deposit`
   - `contract_amount`
   - `lessor_name`
   - `lessee_name`
7. 실제 개인정보가 있는 계약서는 공개 저장소에 올리지 않는다. 가능하면 처음부터 가상 정보 문서를 사용한다.
8. hold-out은 bang/taegu 코드와 규칙이 동결될 때까지 보지 않는다.

---

# 2. `bang_` — OpenCV 구조 복원 / Detected ROI

## 이번 단계 목표

새 알고리즘을 더 만드는 것이 아니라, **현재 OpenCV grid + merged-cell reconstruction을 고정된 설정으로 반복 실행할 수 있게 만들고 P3 평가 입력을 전달**한다.

현재 `bang_` README 기준:

- 메인 코드: `Task_0930.py`
- 공통 10장 일괄 실행: `Task_10_Renewal.py`
- 이전 버전: `TestResult.py` — 보관용

공통 10장 일괄 실행은 다음 명령을 기준으로 한다.

```bash
python Task_10_Renewal.py
```

일반 폴더 batch가 필요하면 현재 구현된 `run_batch()` 경로를 사용하되, **이미지별로 파라미터를 다르게 튜닝하지 않는다.**

## 해야 할 일

- [ ] 현재 사용할 commit/파라미터를 먼저 기록한다.
- [ ] 공통 10장 결과가 현재 기준과 동일하게 재현되는지 확인한다.
- [ ] 가은 학우가 전달한 **development 데이터만 먼저** 같은 설정으로 실행한다.
- [ ] 각 이미지에서 최소 `cells_original.json`, `report.json`을 남긴다.
- [ ] OCR/평가가 aligned 좌표를 쓸 경우 `cells.json`과 aligned image도 함께 전달한다.
- [ ] 원본 GT와 비교할 때는 반드시 `cells_original.json`을 사용한다.
- [ ] 이미지별로 다음 실패 유형을 기록한다.
  - `TABLE_MISSING`
  - `ROW_MERGE`
  - `COLUMN_MERGE`
  - `CELL_MERGE`
  - `WRONG_MAPPING`
  - `COORDINATE_ERROR`
- [ ] 핵심 5필드 기준 Detected ROI Coverage를 계산할 수 있는 summary를 만든다.
- [ ] 코드 동결 후 holdout_test에는 설정 변경 없이 1회 실행한다.

## 전달 형식

```text
<image_id>/
  cells_original.json
  report.json
  cells.json              # aligned OCR 사용 시
  <image_id>_aligned.png  # aligned OCR 사용 시

summary.csv 또는 summary.json
  image_id
  target_fields
  detected_fields
  roi_coverage
  failure_reason
```

## 이번 단계에서 하지 않을 것

- hold-out을 본 뒤 이미지별 파라미터 튜닝
- 새 detector/model 추가
- 구조 복원 알고리즘 대규모 재설계
- `TestResult.py`를 다시 메인으로 사용

## 완료 기준

**development 전부에 대해 동일 설정으로 결과 파일 + 실패 사유가 남아 있고, 다혜가 P3 평가에 바로 넣을 수 있으면 완료.**

---

# 3. `taegu` — Anchor Field ROI / 최소 End-to-End

## 이번 단계 목표

핵심 5필드에 대해 Anchor 기반 ROI를 만들고, 최소한 다음 경로를 끝까지 연결한다.

```text
input image
  -> Anchor/Field ROI
  -> OCR
  -> normalization
  -> final_fields.json
```

현재 브랜치에 있는 `anchor_field_mapper.py`, `evaluate_roi_coverage.py`, `evaluate_fields.py`를 중심으로 정리한다.

## 해야 할 일

- [ ] 핵심 5필드를 정확히 위 공통 key로 맞춘다.
- [ ] Anchor 규칙 수정은 **development 데이터에서만** 한다.
- [ ] 각 ROI에 `field`, `bbox`, `method`, 가능하면 `confidence`를 저장한다.
- [ ] bbox는 이미지 범위 밖으로 나가지 않게 clipping한다.
- [ ] 금액은 첫 OCR bbox를 무조건 고르지 말고 금액 형식과 상대 위치를 함께 본다.
- [ ] ROI가 아예 생성되지 않은 필드도 누락시키지 말고 실패로 남긴다.
- [ ] 아래 실패 사유 중 하나 이상을 기록한다.
  - `ANCHOR_NOT_FOUND`
  - `WRONG_ANCHOR`
  - `MIXED_ROWS`
  - `ROI_TOO_LARGE`
  - `ROI_TOO_SMALL`
  - `OCR_FAILURE`
- [ ] development에서 규칙을 확정하면 commit SHA를 기록하고 동결한다.
- [ ] holdout_test에는 예외 규칙을 추가하지 않고 1회 실행한다.

## 전달물

```text
<image_id>/
  field_rois.json
  final_fields.json

summary.csv 또는 summary.json
  image_id
  field
  roi_found
  prediction
  normalized_prediction
  failure_reason
```

## 완료 기준

모든 이미지에서 성공할 필요는 없다. **ROI Coverage와 Field Accuracy를 계산할 수 있고, 실패가 어떤 유형인지 남아 있으면 완료.**

P4 성능이 낮아도 괜찮다. 그 경우 논문에서는 PoC/보조 비교로 둔다.

---

# 4. `dahye_cell_DetectionSurvey` — 최종 평가 총괄 / Evaluation Gatekeeper

## 이번 단계 목표

최근 추가한 P3/P4 및 common10 감사 결과를 기반으로, **평가 기준을 더 이상 흔들리지 않게 고정하고 P0~P4의 최종 논문 숫자를 한 기준으로 확정**한다.

최근 진행된 문서 흐름:

- P3 Detected ROI evaluation audit
- common10 field evaluation consistency audit
- common10 normalization reproducibility audit
- P4 anchor ROI PoC audit

따라서 지금부터는 새 evaluator를 넓히기보다 위 감사를 **최종 평가 규칙으로 정리하고 결과를 합치는 것**이 우선이다.

## 해야 할 일

- [ ] P0~P4에서 field key가 완전히 같은지 확인한다.
- [ ] normalization 규칙을 하나로 고정한다.
- [ ] 이미지 수, field instance 수, 분모 정의를 문서로 고정한다.
- [ ] ROI 생성 실패를 end-to-end Field Accuracy에서 제외하지 않는다.
- [ ] 다음 두 수치를 반드시 분리해 보고한다.
  1. `ROI Coverage`
  2. ROI가 존재하는 경우의 OCR 정확도
- [ ] 기존 공통 10장과 신규 데이터 결과를 먼저 별도 표로 만든다.
- [ ] 필요할 때만 통합 표를 추가한다.
- [ ] 같은 `document_group_id` 반복 촬영을 독립 문서 표본처럼 해석하지 않는다.
- [ ] bang P3와 taegu P4의 failure reason을 공통 failure breakdown으로 묶는다.
- [ ] bang/taegu 동결 후 가은 학우가 공개한 holdout을 최종 1회 평가한다.

## 최종 표

| Pipeline | Image correction | ROI source | ROI Coverage | Field Accuracy | CER | sec/image |
|---|---|---|---:|---:|---:|---:|
| P0 | X | Full page | - | 값 | 값 | 값 |
| P1 | O | Full page | - | 값 | 값 | 값 |
| P2 | 조건 고정 | GT ROI | 100% | 값 | 값 | 값 |
| P3 | 조건 고정 | bang Detected ROI | 값 | 값 | 값 | 값 |
| P4 | 조건 고정 | taegu Anchor ROI | 값 | 가능 시 | 가능 시 | 가능 시 |

## 완료 기준

**논문 본문/표에 그대로 복사할 수 있는 최종 수치, 분모, 평가 규칙, 실패 유형이 한 세트로 정리되면 완료.**

---

# 5. `heewon` — 정상/통제 촬영 데이터

## 현재 우선 업무

예전 Morphology vs Contour 비교가 아니라, **논문 평가용 정상/통제 신규 데이터 수집이 현재 최우선 업무**다.

## 해야 할 일

- [ ] 개인정보가 없는 가상/연구용 계약서를 사용한다.
- [ ] 가능하면 서로 다른 원본 문서 `document_group_id`를 2개 이상 준비한다.
- [ ] 각 원본 문서마다 최소 1장의 `baseline`을 만든다.
- [ ] 같은 문서를 조건만 바꿔 반복 촬영해 비교쌍을 만든다.
- [ ] 정면, 초점 양호, 문서 전체 포함, 그림자 최소 상태를 기본으로 한다.
- [ ] 촬영 후 crop/filter/밝기/원근 보정을 하지 않는다.
- [ ] 목표: **usable 5~6장**.
- [ ] 촬영 즉시 가은 학우에게 다음 정보를 함께 전달한다.
  - 원본 파일
  - 어떤 원본 문서인지
  - 촬영 조건
  - 특이사항

## 권장 예

```text
docA_baseline_01.jpg
docA_perspective_01.jpg
docA_distance_far_01.jpg

docB_baseline_01.jpg
docB_lighting_01.jpg
docB_perspective_01.jpg
```

## 완료 기준

**원본 이미지 5~6장과 각 이미지의 조건 설명이 가은 학우에게 전달되면 완료.**

---

# 6. `tail` — 난이도 촬영 / 이미지 품질 메타데이터

## 현재 우선 업무

기존 OCR 실험을 새로 확장하는 것이 아니라, **실제 실패를 유발할 수 있는 현실적인 촬영 조건 데이터를 수집하고 조건을 정확히 기록하는 것**이 현재 주업무다.

## 해야 할 일

- [ ] 가능하면 희원이 쓰는 원본 문서 그룹 일부를 공유한다.
- [ ] 다음 조건을 우선한다.
  - `perspective`
  - `distance`
  - `lighting`
  - `fold_or_crop`
- [ ] 사람이 실제 스마트폰으로 찍을 만한 수준으로 만든다.
- [ ] 사람이 읽을 수 없을 정도의 극단적 실패 이미지는 피한다.
- [ ] 촬영 후 이미지를 보정하지 않는다.
- [ ] 실패할 것 같은 이미지도 버리지 말고 `usable` 여부와 이유를 기록한다.
- [ ] 목표: **usable 5~8장**.
- [ ] 가은 학우에게 원본과 조건 설명을 같이 전달한다.

## 완료 기준

**난이도 조건 원본 5~8장과 조건 메타데이터가 가은 학우에게 전달되면 완료.**

---

# 7. 가은 학우 (추가 인원 B) — GT / Dataset Manager

## 역할

가은 학우는 사진을 많이 찍는 담당이 아니라, 희원·tail이 모은 데이터를 **논문 평가가 가능한 Dataset v1.0으로 바꾸는 최종 관리자**다.

세부 규칙은 반드시 `04_data_collection_gt_protocol.md`를 따른다.

## 1단계 — 수집분 받기

희원·tail에게 다음을 받는다.

```text
원본 이미지
원본 문서 그룹 정보
촬영 조건
특이사항
```

받자마자:

- [ ] 개인정보가 남아 있지 않은지 확인
- [ ] 스마트폰 GPS EXIF 등 공개하면 안 되는 메타데이터 확인
- [ ] 손상/중복 이미지 확인
- [ ] `usable` 여부 기록

## 2단계 — 파일명과 manifest 통일

파일명 규칙:

```text
<document_group_id>_<condition>_<index>.jpg
```

`manifest.csv` 필수 컬럼:

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

**`split`은 가은 학우만 최종 확정한다.**

## 3단계 — 핵심 5필드 GT 작성

모든 usable 이미지에 최소 다음 5필드 text GT를 작성한다.

```text
address
deposit
contract_amount
lessor_name
lessee_name
```

각 필드는 가능하면 다음 구조로 기록한다.

```json
{
  "raw_text": "문서에 적힌 원문",
  "normalized": "평가용 정규화 값",
  "bbox": null
}
```

우선순위는 다음과 같다.

1. text GT 정확성
2. normalized 값 정확성
3. 가능하면 bbox

시간이 부족하면 bbox보다 text GT를 먼저 끝낸다.

## 4단계 — 2차 검수

- [ ] GT 초안을 원본 이미지와 다시 비교한다.
- [ ] 애매한 값은 추정하지 않고 `notes`에 기록한다.
- [ ] 금액은 원문과 숫자 정규화 값을 둘 다 남긴다.
- [ ] `manifest.csv`와 `field_gt.json`의 `image_id`가 정확히 일치하는지 확인한다.

## 5단계 — development / holdout 분리

가장 중요한 규칙:

```text
X  docA_baseline -> development
X  docA_perspective -> holdout_test
```

위처럼 같은 문서를 나누면 안 된다.

반드시:

```text
O  docA 전체 -> development
O  docB 전체 -> development
O  docC 전체 -> holdout_test
```

처럼 `document_group_id` 단위로 나눈다.

권장:

- 신규 데이터 약 20~30%
- 또는 최소 1개 전체 문서 그룹

을 `holdout_test`로 둔다.

**holdout 이미지는 bang/taegu가 development 규칙과 코드를 동결하기 전까지 공개하지 않는다.**

## 6단계 — Dataset v1.0 동결

최종 구조:

```text
data/eval_v1/
  images/
  manifest.csv
  field_gt.json
  README.md
```

- [ ] 파일 목록 또는 해시 기록
- [ ] Dataset v1.0 버전 명시
- [ ] 이후 수정 시 v1.1처럼 버전을 올림
- [ ] 실제 개인정보가 포함된 이미지는 public GitHub에 올리지 않음

## 완료 기준

다음이 모두 만족되면 완료다.

- [ ] 신규 usable 이미지 약 10~15장
- [ ] 최소 2~3개 `document_group_id`
- [ ] 모든 이미지 조건 기록
- [ ] 핵심 5필드 GT 완료
- [ ] manifest / GT image_id 일치
- [ ] 개인정보/GPS 확인
- [ ] 중복/손상 확인
- [ ] group 단위 development/holdout 분리
- [ ] Dataset v1.0 동결

---

# 8. 전체 전달 순서 — 이 순서를 바꾸지 않는다

```text
1) heewon / tail
   -> 신규 원본 이미지 + 촬영 조건 수집

2) 가은
   -> 파일명 통일
   -> manifest 작성
   -> 5필드 GT 작성/검수
   -> development / holdout_test 그룹 분리

3) bang / taegu
   -> development만 보고 코드·규칙 확정
   -> commit SHA 기록
   -> 동결 선언

4) 가은
   -> holdout_test 공개

5) bang / taegu
   -> holdout에 동일 설정으로 1회 실행
   -> 결과만 전달, 결과를 보고 재튜닝하지 않음

6) dahye
   -> P0~P4 최종 평가
   -> ROI Coverage / Field Accuracy / CER / 실패 유형 정리
   -> 논문용 표와 수치 확정
```

---

# 9. 각자 진행 상황을 올릴 때 형식

작업자가 무엇을 했는지 서로 다시 물어보지 않도록, 진행 보고는 아래 5줄만 맞춘다.

```text
[담당자/브랜치]
1. 현재 작업:
2. 완료한 것:
3. 생성/수정 파일:
4. 막힌 점:
5. 다음 작업:
```

예:

```text
[bang_]
1. 현재 작업: 신규 development 6장 batch 실행
2. 완료한 것: 4/6장 cells_original.json 생성
3. 생성/수정 파일: output/<image_id>/..., summary.csv
4. 막힌 점: 2장 TABLE_MISSING
5. 다음 작업: 파라미터 변경 없이 실패 사유 정리 후 다혜에게 전달
```

---

# 10. 최종적으로 팀이 끝내야 하는 것

이번 단계의 완료 조건은 새 기능 수가 아니다.

- 데이터: Dataset v1.0 완성
- P3: bang Detected ROI 결과 완성
- P4: taegu Anchor ROI PoC 결과 완성
- 평가: dahye가 동일 기준으로 P0~P4 수치 확정
- 논문: 성공 사례뿐 아니라 실패율과 실패 유형까지 설명 가능

**각자 위 산출물이 끝나면 자신의 역할은 완료된 것으로 본다.**