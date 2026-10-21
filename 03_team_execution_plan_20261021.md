# 2026-10-21 팀 실행 계획 — 핵심 3명 + 데이터/GT 3명

> 현재 기준 문서. 2026-10-08의 기존 `assignment_*.md`보다 이 문서의 역할 재배정을 우선한다.
> 세부 데이터 수집/GT 규칙은 [`04_data_collection_gt_protocol.md`](04_data_collection_gt_protocol.md)를 반드시 함께 따른다.

## 1. 재편 이유

현재 실제 개발/평가 진행은 `bang_`, `taegu`, `dahye_cell_DetectionSurvey` 세 축에 집중되어 있다. 반면 논문 측면에서 가장 큰 약점은 **평가 가능한 데이터의 수와 다양성이 부족한 것**이다.

따라서 새 모델이나 새 연구축을 추가하지 않고 다음과 같이 재편한다.

- 핵심 3명: 기존 파이프라인을 동결·연결·평가하여 논문 결과를 완성
- 나머지 3명: 신규 평가 데이터, 촬영 조건 메타데이터, GT, hold-out 관리 전담

최종 목표 데이터 규모는 **기존 10장 + 신규 10~15장 = 총 20~25장 수준**을 권장한다. 수량보다 GT와 조건 기록의 품질을 우선한다.

> 주의: 20~25장의 이미지는 20~25개의 완전 독립 표본을 뜻하지 않는다. 동일 원본 계약서를 다른 조건으로 촬영한 이미지는 같은 `document_group_id`로 묶어 분석하고, 논문에서도 이미지 수와 원본 문서 그룹 수를 구분해 보고한다.

---

## 2. 핵심 3명

### A. `bang_` — 자동 구조 복원 / Detected ROI 공급

#### 목표
현재 OpenCV 구조 복원 파이프라인을 더 크게 바꾸지 않고, 기존 10장과 신규 평가 데이터에서 **동일한 설정으로 구조/ROI 결과를 생성**한다.

#### 작업 지시
- [ ] 현재 파라미터와 실행 명령을 먼저 고정한다.
- [ ] 기존 공통 10장 결과를 최종 기준 결과로 보존한다.
- [ ] 데이터팀이 확정한 신규 `development` 세트에 동일 설정으로 batch 실행한다.
- [ ] 각 이미지에 `cells_original.json`, `report.json`을 우선 생성한다.
- [ ] 원본 좌표와 aligned 좌표를 절대 혼용하지 않는다.
- [ ] 핵심 5필드 기준 Detected ROI Coverage를 계산할 수 있게 결과를 전달한다.
- [ ] 실패를 최소 다음 유형으로 기록한다: `TABLE_MISSING`, `ROW_MERGE`, `COLUMN_MERGE`, `CELL_MERGE`, `WRONG_MAPPING`, `COORDINATE_ERROR`.
- [ ] 코드 동결 후 `holdout_test`에는 파라미터 수정 없이 1회 실행한다.

#### 전달 산출물
```text
image_id/
  cells_original.json
  report.json
  optional cells.json / preview

summary:
  image_id
  target_fields
  detected_fields
  roi_coverage
  failure_reason
```

#### 하지 않을 것
- hold-out 결과를 보고 이미지별 파라미터 튜닝
- 새 detector/model 추가
- 대규모 병합 알고리즘 재설계

---

### B. `taegu` — Anchor Field ROI + 최소 End-to-End

#### 목표
핵심 5필드의 Anchor ROI를 고정하고, 최종적으로 입력 이미지가 `final_fields.json`까지 연결되는 최소 End-to-End 경로를 만든다.

#### 핵심 필드
- `address` — 소재지
- `deposit` — 보증금
- `contract_amount` — 계약금
- `lessor_name` — 임대인 성명
- `lessee_name` — 임차인 성명

#### 작업 지시
- [ ] 현재 Anchor 규칙을 `development` 데이터에서만 보완하고 이후 동결한다.
- [ ] ROI마다 `field`, `bbox`, `method`, 가능하면 `confidence`를 저장한다.
- [ ] ROI boundary는 이미지 범위 안으로 clipping한다.
- [ ] 금액 후보는 단순히 첫 번째 OCR bbox만 선택하지 말고 금액 형식/위치 조건을 함께 확인한다.
- [ ] 실패 이유를 `ANCHOR_NOT_FOUND`, `WRONG_ANCHOR`, `MIXED_ROWS`, `ROI_TOO_LARGE`, `ROI_TOO_SMALL`, `OCR_FAILURE` 중 하나 이상으로 기록한다.
- [ ] 기존 OCR 코드를 연결하여 최소 다음 경로를 동작시킨다.

```text
input image
  -> Anchor/Field ROI
  -> OCR
  -> normalization
  -> final_fields.json
```

- [ ] 코드 동결 이후 `holdout_test`에는 예외 규칙을 추가하지 않고 실행한다.

#### 완료 판단
10장/신규 데이터 전체에서 성공하지 못해도 된다. 실패율과 실패 유형 자체를 결과로 남긴다. Anchor-ROI가 충분히 완성되지 않으면 P4는 PoC/보조 비교로 유지한다.

---

### C. `dahye_cell_DetectionSurvey` — 최종 평가 총괄 / Evaluation Gatekeeper

#### 목표
기존 `tail`의 OCR 결과와 코드, `bang_`의 Detected ROI, `taegu`의 Anchor ROI를 같은 GT와 같은 평가 규칙으로 묶어 **최종 논문 숫자를 확정**한다.

#### 작업 지시
- [ ] 기존 RQ2 Affine 좌표계 감사 결과를 유지한다.
- [ ] 기존 `tail` E0/E1/E3/E4 결과를 평가 기준의 출발점으로 인수한다.
- [ ] P0~P4에서 분모, field key, normalization 규칙이 동일한지 확인한다.
- [ ] ROI가 생성되지 않은 필드는 평가에서 제외하지 말고 end-to-end Field Accuracy에서는 실패로 계산한다.
- [ ] `ROI Coverage`와 `ROI가 존재하는 경우의 OCR 정확도`를 분리해서 보고한다.
- [ ] 신규 데이터에서도 기존 10장과 별도 표를 먼저 만들고, 필요 시 통합 표를 추가한다.
- [ ] 같은 `document_group_id`의 반복 촬영을 독립 문서 표본처럼 과장하지 않는다.
- [ ] hold-out 결과는 코드/규칙 동결 후 최종 1회 평가하고, 이후 튜닝 시 해당 결과를 더 이상 최종 hold-out으로 부르지 않는다.

#### 최종 비교표
| Pipeline | Image correction | ROI source | ROI Coverage | Field Accuracy | CER | sec/image |
|---|---|---|---:|---:|---:|---:|
| P0 | X | Full page | - | 값 | 값 | 값 |
| P1 | O | Full page | - | 값 | 값 | 값 |
| P2 | 조건 고정 | GT ROI | 100% | 값 | 값 | 값 |
| P3 | 조건 고정 | bang Detected ROI | 값 | 값 | 값 | 값 |
| P4 | 조건 고정 | taegu Anchor ROI | 값 | 가능 시 | 가능 시 | 가능 시 |

#### 평가 원칙
- 좌표계가 다른 prediction과 GT를 섞지 않는다.
- 실행 실패와 낮은 성능을 구분한다.
- 이미지 수와 field instance 수를 둘 다 보고한다.
- 같은 이미지에서 나온 5개 field를 5개의 완전 독립 문서 표본처럼 해석하지 않는다.

---

## 3. 데이터/GT 3명

### D. `heewon` — 정상/통제 촬영 데이터 담당

#### 목표
OCR/구조 복원이 정상적으로 동작해야 하는 **깨끗한 기준 데이터와 통제된 반복 촬영 데이터**를 만든다.

#### 작업 지시
- [ ] 개인정보가 없는 연구용/가상 계약서만 사용한다.
- [ ] 가능하면 2개 이상의 서로 다른 `document_group_id`를 준비한다.
- [ ] 각 원본 문서에 최소 1장의 `baseline` 정면 촬영을 만든다.
- [ ] 동일 문서를 조건만 바꿔 반복 촬영하여 RQ1 통제 비교가 가능하게 한다.
- [ ] 정면, 초점 양호, 문서 전체 포함, 그림자 최소 상태를 기준으로 한다.
- [ ] 원본 촬영 이미지에 crop/filter/밝기/원근 보정을 적용하지 않는다.
- [ ] 목표: **신규 usable 이미지 5~6장**.
- [ ] 촬영 즉시 `manifest`에 `document_group_id`, 조건, 비고를 기록한다.

#### 권장 구성 예
```text
docA_baseline_01.jpg
docA_perspective_01.jpg
docA_distance_far_01.jpg

docB_baseline_01.jpg
docB_lighting_01.jpg
docB_perspective_01.jpg
```

세부 규칙은 `04_data_collection_gt_protocol.md` 참고.

---

### E. `tail` — 난이도 촬영 / 이미지 품질 메타데이터 담당

#### 목표
기존 H1 이미지 품질 분석 경험을 활용하여 **실제 실패를 유발할 수 있는 촬영 조건을 의도적으로 수집하고 조건을 정확히 기록**한다. OCR 모델 개발은 이번 재배정의 주업무가 아니다.

#### 작업 지시
- [ ] 가능하면 `heewon`이 사용하는 것과 같은 원본 문서 그룹 일부를 공유해 조건만 다른 비교쌍을 만든다.
- [ ] 다음 조건을 우선한다: `perspective`, `distance`, `lighting`, `fold_or_crop`.
- [ ] 지나치게 극단적이어서 사람이 읽을 수 없는 이미지는 만들지 않는다.
- [ ] 각 조건은 현실적인 스마트폰 촬영 수준으로 만든다.
- [ ] 원본 이미지를 보정하지 않고 그대로 제출한다.
- [ ] 목표: **신규 usable 이미지 5~8장**.
- [ ] 실패할 것 같은 이미지도 버리지 말고 `usable` 여부와 이유를 기록한다.
- [ ] 기존 H1에서 사용한 거리/접힘/가장자리 해석과 연결될 수 있도록 메타데이터를 구체적으로 작성한다.

#### 권장 조건
```text
perspective: 좌/우/상단 사선, 대략 10~20도 수준
distance: 글자는 읽히지만 유효 해상도가 떨어지는 거리
lighting: 어두움 또는 한쪽 조명/약한 그림자
fold_or_crop: 약한 접힘/휨 또는 가장자리 소량 누락
```

세부 규칙은 `04_data_collection_gt_protocol.md` 참고.

---

### F. 추가 인원 B — GT / Dataset Manager

#### 목표
사진을 많이 모으는 것이 아니라, 수집된 이미지를 **평가 가능한 Dataset v1.0으로 만드는 최종 관리자** 역할을 맡는다.

#### 작업 지시
- [ ] `heewon`, `tail` 수집분을 한 폴더 구조로 통합한다.
- [ ] 공개 GitHub에 올릴 수 없는 개인정보가 남아 있는지 먼저 검사한다.
- [ ] 파일명과 `image_id`를 통일한다.
- [ ] 모든 이미지에 `document_group_id`를 부여한다.
- [ ] 모든 이미지의 핵심 5필드 text GT를 작성/검수한다.
- [ ] 금액은 원문(`raw_text`)과 비교용 정규화 값(`normalized`)을 함께 기록한다.
- [ ] 가능하면 핵심 필드 GT ROI bbox를 추가하되, 시간이 부족하면 text GT를 우선한다.
- [ ] `manifest.csv`를 완성하고 중복/누락/손상 이미지를 검사한다.
- [ ] `development`와 `holdout_test`를 **이미지가 아니라 `document_group_id` 단위로 분리**한다.
- [ ] 기존 공통 10장은 이미 개발/분석에 사용됐으므로 hold-out으로 지정하지 않는다.
- [ ] 신규 데이터의 약 20~30% 또는 최소 1개 전체 문서 그룹을 `holdout_test`로 남긴다.
- [ ] Dataset v1.0을 동결한 뒤 파일 목록/해시 또는 변경 방지 기록을 남긴다.

#### 핵심 산출물
```text
data/eval_v1/
  images/
  manifest.csv
  field_gt.json
  README.md
```

실제 이미지가 개인정보를 포함한다면 공개 저장소에 커밋하지 않고, 비식별/가상 데이터만 repository에 포함한다.

---

## 4. 데이터 전달 순서

```text
heewon / tail
  -> 원본 이미지 + 촬영조건 기록
        ↓
추가 인원 B
  -> 개인정보 확인
  -> 파일명/manifest 정리
  -> field GT 작성/검수
  -> document_group_id 기준 split
  -> Dataset v1.0 동결
        ↓
  development 공개
        ↓
bang / taegu 개발·규칙 확정
        ↓
  코드/파라미터 동결
        ↓
  holdout_test 공개
        ↓
bang / taegu 최종 실행
        ↓
dahye 최종 평가
```

---

## 5. 전체 팀 공통 금지사항

- 신규 OCR/구조 모델을 추가해 연구축을 다시 넓히지 않는다.
- hold-out 결과를 본 뒤 규칙을 수정하고 같은 결과를 최종 test라고 부르지 않는다.
- 동일 문서의 반복 촬영 이미지를 서로 다른 문서처럼 train/development와 test에 나누지 않는다.
- 데이터 수를 늘리기 위해 같은 이미지를 resize/compress 복제하여 별도 표본으로 세지 않는다.
- 실제 개인정보가 포함된 임대차계약서 원본을 공개 저장소에 올리지 않는다.
- 데이터가 20~25장으로 늘어나더라도 전체 임대차계약서에 일반화된다고 주장하지 않는다.

## 6. 최종 완료 기준

1. Dataset v1.0에 기존 10장 + 신규 10~15장 수준의 평가 가능한 이미지가 있다.
2. 신규 데이터는 `document_group_id`, 촬영조건, GT, split을 가진다.
3. `bang_`과 `taegu`는 동결된 설정으로 hold-out에 실행한다.
4. `dahye`가 P0~P4와 구조 결과의 최종 수치를 같은 기준으로 확정한다.
5. 논문에는 이미지 수, 원본 문서 그룹 수, field instance 수를 구분해 보고한다.
