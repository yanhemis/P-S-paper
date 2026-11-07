# Detected ROI 전달 문서 (bang_)

> 기준 문서: issue 브랜치 `05_current_team_tasks_20261101.md` 2절, `04_data_collection_gt_protocol.md`
> 받는 사람: dahye (P3 평가), taegu (End-to-End 비교)

## 1. 고정한 것

| 항목 | 값 |
|---|---|
| 구조 복원 코드 | `Task_0930.py` — commit `8143969` 이후 변경 없음, `PARAMS` 변경 없음, method `opencv_grid_merge` |
| 필드 대응 | `field_roi.py` — 기준 이미지 sample_1, 셀 id: address 2 / deposit 23 / contract_amount 25 / lessor_name 41 / lessee_name 58 |
| 실행 환경 | `requirements_frozen.txt` — Python 3.13.9, opencv-python 5.0.0.93, numpy 2.3.5, pillow 12.0.0 |
| 데이터 | `dataset-v1` 브랜치 `285b05b`, `data/eval_v1_packages/development/` |
| 기록 | 실행마다 `run_info.json`, 동결 시 `frozen_params.json` |

```bash
python Task_10_Renewal.py --check-repro            # 공통 10장 재현 확인
python Task_10_Renewal.py                          # 공통 10장 5필드 요약
python Task_10_Renewal.py --dataset development    # development 실행
python Task_10_Renewal.py --freeze                 # 코드 commit 후 동결
python Task_10_Renewal.py --dataset holdout_test   # 동결·패키지 공개 후 1회 실행
```

- `--freeze` 는 코드에 commit 되지 않은 변경이 있으면 거부한다.
- `holdout_test` 는 코드·파라미터·환경이 동결 기록과 다르거나, 이미 실행했거나, development 와 `document_group_id` 가 겹치면 거부한다.

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
output/eval_v1/holdout_test/       holdout_test (미실행)
  <image_id>/cells_original.json   셀, 원본 좌표 — 원본 GT 와 비교할 때 사용
  <image_id>/report.json           구조 복원 status, 실패 사례, 파라미터
  <image_id>/cells.json            셀, aligned 좌표
  <image_id>/<image_id>_aligned.png  aligned 이미지 (git 제외, 위 명령으로 재생성)
  <image_id>/fields.json           5필드 ROI + 필드별 실패 유형
  summary.json                     전달용 요약 (아래 5개 열)
  field_summary.csv                summary.json + 문서 그룹, 조건, status, 표 수, GT bbox 수
  field_results.csv                필드 단위 상세
  detected_roi.json                5필드 ROI 모음, 원본 좌표 quad
  run_info.json                    명령, 파라미터, 코드 해시, 환경, commit, 데이터셋 해시
```

`summary.json` 열: `image_id`, `target_fields`, `detected_fields`, `roi_coverage`, `failure_reason`

- 공통 10장 폴더의 `summary.csv` 는 `run_batch()` 가 만드는 구조 복원 요약이다. 5필드 요약은 `summary.json` 을 쓴다.
- `detected_roi.json` 의 key 는 development 에서 `image_id`, 공통 10장에서 파일명이다.

## 3. 판정 규칙

- `target_fields`: 평가 대상 필드 수. GT 가 `status: not_present` 인 필드는 분모에서 뺀다 (common_007 / sample_7 의 contract_amount).
- `detected_fields`: 실패 유형 없이 ROI 를 만든 필드 수.
- `roi_coverage`: `detected_fields / target_fields`. **ROI 생성 비율이며, GT bbox 가 없는 이미지에서는 위치 정합을 보증하지 않는다.**

| 유형 | 판정 |
|---|---|
| `TABLE_MISSING` | 필드가 있어야 할 표를 못 찾음, 또는 그 위치에 셀이 없음 |
| `ROW_MERGE` | 셀 높이 > 기준 셀 높이 × 1.8 |
| `COLUMN_MERGE` | 셀 폭 > 기준 셀 폭 × 1.8 |
| `CELL_MERGE` | 높이·폭 모두 초과 |
| `WRONG_MAPPING` | GT bbox 필요: 고른 셀은 GT 를 50% 이상 못 덮는데 다른 셀이 덮음 |
| `COORDINATE_ERROR` | GT bbox 필요: GT 를 50% 이상 덮는 셀이 없음 |
| `RUN_ERROR` | 파이프라인 실행 실패 (성능 실패와 구분) |

GT bbox: Dataset v1.0 은 common_001~010 의 49개 필드에만 `bbox` 가 있다. 신규 9장은 `null` 이라 `WRONG_MAPPING` / `COORDINATE_ERROR` 를 자동 판정하지 못한다.

## 4. 결과

| 묶음 | 이미지 | 5필드 | ROI coverage |
|---|---:|---:|---:|
| 공통 10장 (common_001~010) | 10 | 21/49 | 42.9% |
| 신규 development | 9 | 20/45 | 44.4% |
| development 전체 | 19 | 41/94 | 43.6% |

실패 53건: `ROW_MERGE` 28, `TABLE_MISSING` 23, `COLUMN_MERGE` 1, `CELL_MERGE` 1, `RUN_ERROR` 0. `WRONG_MAPPING` / `COORDINATE_ERROR` 는 공통 10장에서 0건이고 신규 9장은 판정 불가다.

### 신규 9장

| image_id | 문서 그룹 | 조건 | 표 | 5필드 | 실패 |
|---|---|---|---:|---:|---|
| heewon_001 | heewon_docA | baseline | 4 | 5/5 | - |
| heewon_002 | heewon_docA | distance | 2 | 4/5 | lessor_name `CELL_MERGE` |
| heewon_003 | heewon_docA | perspective | 0 | 0/5 | 5필드 `TABLE_MISSING` |
| heewon_004 | heewon_docB | baseline | 2 | 2/5 | 상단 3필드 `ROW_MERGE` |
| heewon_005 | heewon_docB | perspective | 0 | 0/5 | 5필드 `TABLE_MISSING` |
| heewon_006 | heewon_docB | perspective | 1 | 0/5 | 상단 3필드 `ROW_MERGE`, 성명 2필드 `TABLE_MISSING` |
| tail_001 | tail_docA | perspective | 0 | 0/5 | 5필드 `TABLE_MISSING` |
| tail_002 | tail_docA | distance | 2 | 4/5 | lessor_name `COLUMN_MERGE` |
| tail_007 | tail_docA | baseline | 2 | 5/5 | - |

조건별 신규 9장: baseline 12/15, distance 8/10, perspective 0/20. 이미지 수이며 독립 문서 수가 아니다 (문서 그룹 3개).

육안 확인(GT 아님): ROI 가 생성된 신규 필드 20개를 원본 위에 그려 확인했을 때 모두 해당 필드의 행·칸에 놓였다. 이 확인은 평가 수치에 반영하지 않았다.

### 공통 10장

| image_id | 표 | 5필드 | 실패 |
|---|---:|---:|---|
| sample_1 | 2 | 5/5 | - |
| sample_2 | 2 | 5/5 | - |
| sample_4 | 2 | 5/5 | - |
| sample_6 | 2 | 2/5 | 상단 3필드 `ROW_MERGE` |
| sample_8 | 2 | 2/5 | 상단 3필드 `ROW_MERGE` |
| sample_3 | 2 | 1/5 | 상단 3필드, lessee_name `ROW_MERGE` |
| sample_9 | 2 | 1/5 | 상단 3필드, lessee_name `ROW_MERGE` |
| sample_5 | 1 | 0/5 | 상단 3필드 `ROW_MERGE`, 성명 2필드 `TABLE_MISSING` |
| sample_7 | 1 | 0/4 | address, deposit `ROW_MERGE`, 성명 2필드 `TABLE_MISSING` |
| sample_10 | 1 | 0/5 | 상단 3필드 `ROW_MERGE`, 성명 2필드 `TABLE_MISSING` |

development 의 common_001~010 `cells_original.json` 은 공통 10장 결과와 10장 모두 같다.

이전 P3 감사의 22/49 는 tail GT 위치로 셀을 고른 이전 전달본(`handoff_tail/`) 기준이다. 이번 21/49 는 GT 없이 기준 구조로 고른 값이며, sample_6 address 판정이 다르다 (기준 셀 높이의 2.03배로 `ROW_MERGE`).

## 5. 전달 시 확인이 필요한 사항

- 신규 9장 GT `bbox` 가 없으면 기하 ROI Coverage 와 `WRONG_MAPPING` / `COORDINATE_ERROR` 를 계산할 수 없다.

## 6. 하지 않은 것

- 이미지별 파라미터 조정, 새 detector / model 추가, 구조 복원 알고리즘 재설계
- holdout_test 접근·실행
