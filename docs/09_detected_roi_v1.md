# Detected ROI 전달 문서 (bang_)

> 기준 문서: issue 브랜치 `05_current_team_tasks_20261101.md` 2절, `04_data_collection_gt_protocol.md`
> 받는 사람: dahye (P3 평가), taegu (End-to-End 비교)

## 1. 고정한 것

| 항목 | 값 |
|---|---|
| 구조 복원 코드 | `Task_0930.py` — commit `8143969` 이후 변경 없음, `PARAMS` 변경 없음, method `opencv_grid_merge` |
| 필드 대응 | `field_roi.py` — 기준 이미지 sample_1, 셀 id: address 2 / deposit 23 / contract_amount 25 / lessor_name 41 / lessee_name 58 |
| P3 Coverage | `p3_detected_roi_coverage.py` — Covered ≥ 0.90, 후보 최대값, 후보 최소 겹침 0.5, 후보 최대 5개 |
| 실행 환경 | `requirements_frozen.txt` — Python 3.13.9, opencv-python 5.0.0.93, numpy 2.3.5, pillow 12.0.0 |
| 데이터 | `dataset-v1` 브랜치 `ead8436`, `data/eval_v1_packages/development/` |
| 기록 | 실행마다 `run_info.json`·`roi_coverage_overall.json`, 동결 시 `frozen_params.json` |

```bash
python Task_10_Renewal.py --check-repro                   # 공통 10장 재현 확인
python Task_10_Renewal.py                                 # 공통 10장 5필드 요약
python Task_10_Renewal.py --dataset development           # development 실행 + P3 Coverage
python p3_detected_roi_coverage.py --dataset development  # 셀은 그대로, Coverage 만 다시 계산
python Task_10_Renewal.py --freeze                        # 코드 commit 후 동결
python Task_10_Renewal.py --dataset holdout_test --check-package  # 형식만 확인 (실행 안 함)
python Task_10_Renewal.py --dataset holdout_test          # 동결·패키지 공개 후 1회 실행 + P3 Coverage
```

- `--freeze` 는 코드(위 4개 .py)에 commit 되지 않은 변경이 있으면 거부한다.
- `holdout_test` 는 코드·파라미터·환경이 동결 기록과 다르거나, 이미 실행했거나, development 와 `document_group_id` 가 겹치면 거부한다. Coverage 계산도 동결 상태가 아니면 거부한다.
- GT 갱신(`285b05b` → `d4b32b6` → `ead8436`)은 BBox 만 바뀌었으므로 셀 결과(`cells*.json`)는 다시 실행해도 19장 모두 같다.

### 환경 주의

같은 코드와 파라미터라도 라이브러리 버전이 다르면 셀 결과가 달라진다.

| 환경 | numpy / pillow | 공통 10장 셀 파일 40개 |
|---|---|---|
| 동결 환경 | 2.3.5 / 12.0.0 | 40개 동일 |
| 비교 환경 | 2.5.3 / 12.3.0 | 20개 다름 (예: sample_3 기울기 2.585° → 3.255°, 셀 18 → 49) |

두 환경의 opencv 버전은 같다. numpy 와 pillow 중 어느 쪽이 원인인지는 분리하지 않았다.

## 2. 출력

```text
output/common10/                   공통 10장
output/eval_v1/development/        development
output/eval_v1/holdout_test/       holdout_test (동결 commit 55c30b0 으로 1회 실행, 6장)
  <image_id>/cells_original.json   셀, 원본 좌표 — 원본 GT 와 비교할 때 사용
  <image_id>/report.json           구조 복원 status, 실패 사례, 파라미터
  <image_id>/cells.json            셀, aligned 좌표
  <image_id>/<image_id>_aligned.png  aligned 이미지 (git 제외, 위 명령으로 재생성)
  <image_id>/fields.json           5필드 ROI + 필드별 실패 유형
  summary.json                     전달용 요약 (아래 5개 열)
  summary.csv                      summary.json + Covered Rate, ROI 생성 수, 문서 그룹, 조건, status
  roi_coverage_overall.json        전체·공통·heewon·tail·조건별 Covered Rate, 평균 Coverage, 실패 수, sec/image
  roi_coverage_fields.csv          필드별 GT BBox, Coverage, Covered, 실패 유형, roi_flag
  roi_candidates.json              필드별 ROI 후보 (원본 좌표) 와 후보별 Coverage — P3 평가 입력
  field_summary.csv                ROI 생성 기준 요약 + 문서 그룹, 조건, status, 표 수, GT bbox 수
  field_results.csv                필드 단위 상세
  detected_roi.json                5필드 ROI 모음, 원본 좌표 quad
  run_info.json                    명령, 파라미터, 코드 해시, 환경, commit, 데이터셋 해시
```

`summary.json` 열: `image_id`, `target_fields`, `detected_fields`, `roi_coverage`, `failure_reason`

- 공통 10장 폴더의 `summary.csv` 는 `run_batch()` 가 만드는 구조 복원 요약이다. 5필드 요약은 `summary.json` 을 쓴다.
- `detected_roi.json` 의 key 는 development 에서 `image_id`, 공통 10장에서 파일명이다.

## 3. 판정 규칙 (04 문서 7절, dahye `final_evaluation_protocol.md`)

- Coverage = `Area(GT ∩ ROI) / Area(GT)`, 원본 좌표. 반올림 전 값이 0.90 이상이면 Covered.
- P3 는 필드마다 ROI 후보를 여럿 낼 수 있고, 후보 중 최대 Coverage 를 쓴다. ROI 가 없으면 Coverage 0.
- ROI 후보는 GT 를 보지 않는다: 기준 양식 위치의 중심을 포함하는 셀(primary) + 그 영역과 50% 이상 겹치는 같은 표의 셀, 최대 5개.
- `not_present` / `unreadable` / `bbox: null` 필드는 분모에서 뺀다 (현재 common_007 의 contract_amount 1개).

`summary.json` 열:

- `target_fields`: Coverage 평가 필드 수
- `detected_fields`: Covered 필드 수
- `roi_coverage`: 그 이미지의 평균 Coverage
- `failure_reason`: Covered 가 아닌 필드의 유형

| 유형 | 판정 |
|---|---|
| `TABLE_MISSING` | 필드가 있어야 할 표를 못 찾음, 또는 그 위치에 셀이 없음 (ROI 없음) |
| `ROW_MERGE` | primary 셀 높이 > 기준 셀 높이 × 1.8 |
| `COLUMN_MERGE` | primary 셀 폭 > 기준 셀 폭 × 1.8 |
| `CELL_MERGE` | 높이·폭 모두 초과 |
| `WRONG_MAPPING` | 후보는 GT 를 0.90 이상 못 덮는데 이미지의 다른 셀이 덮음 |
| `COORDINATE_ERROR` | GT 를 0.90 이상 덮는 셀이 이미지 어디에도 없음 (경계 어긋남·분할) |
| `RUN_ERROR` | 파이프라인 실행 실패 (성능 실패와 구분) |

Covered 인데 primary 셀이 병합 크기면 실패로 세지 않고 `roi_flag` 에 남긴다 (ROI 가 너무 큰 경우 확인용).

## 4. 결과 (GT `ead8436`, Covered ≥ 0.90)

| 묶음 | 이미지 | Covered | Covered Rate | 평균 Coverage | ROI 생성 | sec/image |
|---|---:|---:|---:|---:|---:|---:|
| 공통 10장 (common_001~010) | 10 | 21/49 | 42.9% | 0.662 | 43/49 | 1.33 |
| 신규 heewon | 6 | 8/30 | 26.7% | 0.457 | 18/30 | 1.05 |
| 신규 tail | 3 | 7/15 | 46.7% | 0.620 | 10/15 | 0.92 |
| 신규 합계 | 9 | 15/45 | 33.3% | 0.511 | 28/45 | 1.01 |
| development 전체 | 19 | 36/94 | 38.3% | 0.590 | 71/94 | 1.18 |

- Covered 아님 58필드: `TABLE_MISSING` 23, `COORDINATE_ERROR` 23, `ROW_MERGE` 12, `WRONG_MAPPING` 0, `RUN_ERROR` 0.
- Covered 36필드 중 18필드는 병합 크기 셀로 덮었다 (`roi_flag`).
- sec/image 는 `report.json` 의 `process_sec` 평균 (구조 복원만, 필드 선택·OCR 제외).
- 이전 GT `d4b32b6` 에서는 tail 15필드가 `bbox: null` 이라 29/79 였다 (dahye 독립 재계산과 일치). 공통·heewon 값은 GT 갱신 후에도 같다.

### 신규 9장

| image_id | 문서 그룹 | 조건 | Covered | 평균 Coverage | Covered 아님 |
|---|---|---|---:|---:|---|
| heewon_001 | heewon_docA | baseline | 1/5 | 0.876 | address, deposit, contract_amount, lessee_name `COORDINATE_ERROR` |
| heewon_002 | heewon_docA | distance | 3/5 | 0.905 | deposit, contract_amount `COORDINATE_ERROR` |
| heewon_003 | heewon_docA | perspective | 0/5 | 0.000 | 5필드 `TABLE_MISSING` |
| heewon_004 | heewon_docB | baseline | 4/5 | 0.961 | lessee_name `COORDINATE_ERROR` |
| heewon_005 | heewon_docB | perspective | 0/5 | 0.000 | 5필드 `TABLE_MISSING` |
| heewon_006 | heewon_docB | perspective | 0/5 | 0.000 | 상단 3필드 `ROW_MERGE`, 성명 2필드 `TABLE_MISSING` |
| tail_001 | tail_docA | perspective | 0/5 | 0.000 | 5필드 `TABLE_MISSING` |
| tail_002 | tail_docA | distance | 2/5 | 0.870 | address, deposit, contract_amount `COORDINATE_ERROR` |
| tail_007 | tail_docA | baseline | 5/5 | 0.990 | - |

조건별 신규 9장: baseline 10/15 (평균 0.942), distance 5/10 (0.888), perspective 0/20 (0.000). 이미지 수이며 독립 문서 수가 아니다 (문서 그룹 3개).

`COORDINATE_ERROR` 23필드의 Coverage 는 0.709~0.898 (중앙값 0.835) 이다. 모두 GT 의 70% 이상은 덮었지만 0.90 에 못 미쳤고, 이미지의 어떤 셀도 0.90 이상 덮지 못했다. 원인(값 글자가 표 선에 걸침, 셀 경계 오차 등)은 필드별로 확인하지 않았다.

### 공통 10장

| image_id | 파일 | Covered | 평균 Coverage | Covered 아님 |
|---|---|---:|---:|---|
| common_001 | sample_1 | 1/5 | 0.848 | address, contract_amount, lessor_name, lessee_name `COORDINATE_ERROR` |
| common_002 | sample_2 | 4/5 | 0.919 | address `COORDINATE_ERROR` |
| common_003 | sample_3 | 4/5 | 0.946 | lessor_name `COORDINATE_ERROR` |
| common_004 | sample_4 | 2/5 | 0.874 | address, lessor_name, lessee_name `COORDINATE_ERROR` |
| common_005 | sample_5 | 2/5 | 0.400 | address `ROW_MERGE`, 성명 2필드 `TABLE_MISSING` |
| common_006 | sample_6 | 0/5 | 0.445 | 상단 3필드 `ROW_MERGE`, 성명 2필드 `COORDINATE_ERROR` |
| common_007 | sample_7 | 1/4 | 0.458 | address `ROW_MERGE`, 성명 2필드 `TABLE_MISSING` |
| common_008 | sample_8 | 2/5 | 0.544 | deposit, contract_amount `ROW_MERGE`, lessor_name `COORDINATE_ERROR` |
| common_009 | sample_9 | 4/5 | 0.944 | lessor_name `COORDINATE_ERROR` |
| common_010 | sample_10 | 1/5 | 0.200 | deposit, contract_amount `ROW_MERGE`, 성명 2필드 `TABLE_MISSING` |

development 의 common_001~010 `cells_original.json` 은 공통 10장 결과와 10장 모두 같다.

이전 P3 감사의 22/49 는 tail GT 위치로 셀을 고른 이전 전달본(`handoff_tail/`)의 ROI 기록 존재율이다. 이번 21/49 는 GT 없이 고른 후보의 기하 Coverage 이므로 두 값을 같은 지표로 비교하지 않는다.

### holdout_test (동결 후 1회 실행)

GT `dataset-v1` `fb069e7`, 동결 commit `55c30b0`. 결과를 본 뒤 코드·파라미터를 바꾸지 않았다. 동결 선언과 순서 기록은 [동결 선언](11_freeze_declaration.md).

| image_id | 문서 그룹 | 조건 | 표 | Covered | 평균 Coverage | Covered 아님 |
|---|---|---|---:|---:|---:|---|
| tail_003 | tail_docB | lighting | 2 | 0/5 | 0.000 | 5필드 `TABLE_MISSING` |
| tail_004 | tail_docB | fold | 2 | 0/5 | 0.000 | 5필드 `TABLE_MISSING` |
| tail_005 | tail_docC | perspective | 0 | 0/5 | 0.000 | 5필드 `TABLE_MISSING` |
| tail_006 | tail_docC | lighting | 2 | 0/5 | 0.000 | 5필드 `TABLE_MISSING` |
| tail_008 | tail_docB | baseline | 2 | 3/5 | 0.845 | address `COORDINATE_ERROR`, deposit `ROW_MERGE` |
| tail_009 | tail_docC | baseline | 2 | 0/5 | 0.740 | 5필드 `COORDINATE_ERROR` |

전체 3/30 (10.0%), 평균 Coverage 0.264, ROI 생성 10/30. tail_003·004·006 은 표 2개를 찾았지만 기준 양식 위치에 맞는 표 또는 셀이 없어 `TABLE_MISSING` 으로 판정됐다.

## 5. 전달 시 확인이 필요한 사항

- 평가 쪽에서 쓸 P3 입력은 `roi_candidates.json` (필드별 후보 bbox, 원본 좌표) 이다.
- GT BBox 의 육안 정확도와 Dataset v1.0 최종 동결은 bang_ 이 검증하지 않았다.

## 6. 하지 않은 것

- 이미지별 파라미터 조정, 새 detector / model 추가, 구조 복원 알고리즘 재설계
- 동결 전 holdout_test 접근·실행, holdout 결과를 본 뒤 재튜닝·재실행
