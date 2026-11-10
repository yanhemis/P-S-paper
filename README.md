# OpenCV 구조 복원 / Detected ROI (bang_)

임대차계약서 사진에서 표선을 찾아 셀 격자를 만들고, 병합 셀을 복원한 뒤, 핵심 5필드의 ROI를 평가 입력으로 전달합니다.

| 항목 | 내용 |
|---|---|
| 담당 범위 | OpenCV 구조 복원, Detected ROI 공급 (P3 평가 입력) |
| 평가 필드 | `address`, `deposit`, `contract_amount`, `lessor_name`, `lessee_name` |
| 현재 상태 | development 실행 완료, 코드 동결 완료, holdout_test 공개 대기 |
| 동결 기준 | `frozen_params.json` (commit SHA, 코드 해시, 환경). 구조 복원 코드 `Task_0930.py`는 `8143969` 이후 변경 없음 |
| 코드별 진행·결과 | [`docs/10_code_progress_results.md`](docs/10_code_progress_results.md) |
| 전달 문서 | [`docs/09_detected_roi_v1.md`](docs/09_detected_roi_v1.md) |

## 수행한 과제

| 시기 | 과제 | 결과물 |
|---|---|---|
| 09/14 | 기울기 보정, 해상도 비례 파라미터, Union-Find 병합 셀 복원 구현 | `TestResult.py` (보관용) |
| 09/28 | 셀 검출·병합 복원 파이프라인 재구성, sample.jpg 결과 생성 | `Task_0930.py` |
| 10/04 | 추가 인원 A에게 ROI OCR용 셀 결과 전달 | `1004_A에게_줄파일/`, `docs/05_handoff_A_roi.md` |
| 10/05 | 추가 인원 B에게 입출력 명세 전달, 원본 좌표 출력 추가, 성공·실패 사례 정리 | `1005_B에게_줄파일/`, `docs/02`, `docs/03`, `docs/06` |
| 10/13 | 공통 10장 일괄 실행, tail 실험 C 입력 전달 | `Task_10_Renewal.py`, `tail_roi.py`, `output/common10/`, `docs/07`, `docs/08` |
| 11/06 | 5필드 ROI·실패 유형 분류, 공통 10장 재현 확인, development 19장 실행, 코드·환경 동결 | `field_roi.py`, `output/eval_v1/development/`, `frozen_params.json`, `docs/09` |
| 11/09 | GT BBox 기준 P3 ROI Coverage (0.90, 후보 최대값), tail GT BBox 반영, Coverage 계산까지 동결 대상에 포함 | `p3_detected_roi_coverage.py`, `roi_coverage_*.json/csv` |

## 결과

### sample.jpg 셀 검출 (공통 평가, GT 95셀)

| 방법 | F1 @ IoU 0.3 | F1 @ IoU 0.5 | F1 @ IoU 0.7 |
|---|---:|---:|---:|
| Primitive Grid | 49.7% | 38.7% | 25.8% |
| Grid + Cell Reconstruction | 88.4% | 77.3% | 65.2% |

수치는 `dahye_cell_DetectionSurvey` 브랜치의 공통 평가(`5_Evaluation/metrics_affine_audit.json`) 기준입니다. 이전 README의 F1 86.2%는 셀 중심만 역변환한 좌표로 잰 자체 측정값입니다. 차이는 [코드별 진행·결과](docs/10_code_progress_results.md)에 정리했습니다. 단일 이미지 결과이므로 일반화할 수 없습니다.

사례 분석은 [성공 사례](docs/02_success_cases.md)와 [실패 사례](docs/03_failure_cases.md)에 있습니다.

### Dataset v1.0 development: 핵심 5필드 P3 ROI Coverage

GT: `dataset-v1` `ead8436` (19장 모든 평가 필드에 GT BBox). 기준: `Coverage = Area(GT ∩ ROI) / Area(GT)`, 0.90 이상이면 Covered, ROI 후보가 여럿이면 최대값.

| 묶음 | 이미지 | Covered | Covered Rate | 평균 Coverage | ROI 생성 |
|---|---:|---:|---:|---:|---:|
| 공통 10장 (common_001~010) | 10 | 21/49 | 42.9% | 0.662 | 43/49 |
| 신규 heewon | 6 | 8/30 | 26.7% | 0.457 | 18/30 |
| 신규 tail | 3 | 7/15 | 46.7% | 0.620 | 10/15 |
| **전체** | **19** | **36/94** | **38.3%** | **0.590** | **71/94** |

신규 9장의 조건별 결과입니다. 문서 그룹은 3개이므로 이미지 수를 독립 문서 수로 해석하면 안 됩니다.

| 조건 | 이미지 | Covered | 평균 Coverage |
|---|---:|---:|---:|
| baseline | 3 | 10/15 | 0.942 |
| distance | 2 | 5/10 | 0.888 |
| perspective | 4 | 0/20 | 0.000 |

Covered 가 아닌 58필드의 유형: `TABLE_MISSING` 23, `COORDINATE_ERROR` 23, `ROW_MERGE` 12 (`WRONG_MAPPING` 0).

- 분모 94는 GT가 `not_present`인 common_007의 `contract_amount`를 제외한 값입니다.
- ROI 후보는 GT를 보지 않고 기준 양식의 상대 위치로 고릅니다. GT는 Coverage 계산에만 씁니다.
- 구조 복원 시간은 이미지당 평균 1.18초입니다 (`report.json`의 `process_sec`, 필드 선택·OCR 제외).
- 이전 기준(ROI 생성 비율 41/94)과 이전 GT(`d4b32b6`, 79필드 29/79)의 값은 [코드별 진행·결과](docs/10_code_progress_results.md)에 남겨 두었습니다.
- 이미지별 결과는 `output/eval_v1/development/summary.json`, 필드별 결과는 `roi_coverage_fields.csv`에 있습니다.

## 처리 흐름

1. 이미지 로드(EXIF 회전 반영) 후 기울기 보정 (HoughLinesP)
2. 이진화 (CLAHE + adaptive threshold, 해상도 비례 파라미터)
3. 수평·수직선 추출, 끊어진 선 연결, 표 영역 분리
4. 셀 경계 판정, Union-Find 병합, 비직사각형 병합 복구
5. 자동 검증과 결과 저장 (`cells.json`, 시각화, 리포트)
6. 기준 양식의 상대 위치로 5필드 셀 선택, 실패 유형 기록
7. 필드별 ROI 후보와 GT BBox로 P3 ROI Coverage 계산 (Dataset v1)

## 폴더 구조

```text
P-S-paper/
├─ Task_0930.py             구조 복원 메인 코드
├─ Task_10_Renewal.py       일괄 실행, 재현 확인, 동결, 결과 요약
├─ field_roi.py             5필드 → 셀 대응, 실패 유형 분류
├─ p3_detected_roi_coverage.py  GT BBox 기준 P3 ROI Coverage
├─ tail_roi.py              공통 10장 셀 → tail 실험 C 입력 변환
├─ TestResult.py            이전 버전 (보관용)
├─ frozen_params.json       동결한 파라미터, 코드 해시, 환경, commit
├─ requirements_frozen.txt  결과가 재현되는 라이브러리 버전
├─ data/common10/           공통 10장 + tail GT ROI 사본
├─ data/eval_v1_packages/   Dataset v1.0 패키지 (git 제외)
├─ output/common10/         공통 10장 결과
├─ output/eval_v1/          Dataset v1.0 결과
├─ 1004_A에게_줄파일/        10/04 전달물
├─ 1005_B에게_줄파일/        10/05 전달물
└─ docs/                    사례 분석, 전달 문서
```

## 설치

```bash
python -m pip install -r requirements_frozen.txt
```

라이브러리 버전이 다르면 셀 결과도 달라지므로 Python 3.13.9와 위 파일의 버전을 그대로 사용합니다.

Dataset v1.0 development 패키지는 `dataset-v1` 브랜치에서 받습니다.

```bash
git archive origin/dataset-v1 data/eval_v1_packages/development | tar -x
```

## 실행

프로젝트 폴더에서 실행합니다.

| 목적 | 명령 |
|---|---|
| 공통 10장 재현 확인 (기존 결과 유지) | `python Task_10_Renewal.py --check-repro` |
| 공통 10장 5필드 요약 | `python Task_10_Renewal.py` |
| 공통 10장 다시 실행 (기존 결과 덮어씀) | `python Task_10_Renewal.py --rerun` |
| development 일괄 실행 + P3 Coverage | `python Task_10_Renewal.py --dataset development` |
| 셀은 그대로 두고 Coverage만 다시 계산 | `python p3_detected_roi_coverage.py --dataset development` |
| 코드 commit 후 동결 기록 | `python Task_10_Renewal.py --freeze` |
| holdout_test 패키지 형식 확인 (실행 안 함) | `python Task_10_Renewal.py --dataset holdout_test --check-package` |
| holdout_test 1회 실행 + P3 Coverage | `python Task_10_Renewal.py --dataset holdout_test` |

`holdout_test`는 코드(`p3_detected_roi_coverage.py` 포함)·파라미터·환경이 동결 기록과 다르거나, 이미 실행했거나, development와 `document_group_id`가 겹치면 실행되지 않습니다.

## 출력

`output/common10/`과 `output/eval_v1/<split>/`의 구조는 같습니다.

| 파일 | 내용 | 좌표 기준 |
|---|---|---|
| `<image_id>/cells_original.json` | 최종 셀. 원본 GT와 비교할 때 사용 | 원본 |
| `<image_id>/cells.json` | 최종 셀. aligned OCR에 사용 | 보정본 |
| `<image_id>/<image_id>_aligned.png` | 보정본 이미지 (git 제외, 다시 실행하면 생성) | - |
| `<image_id>/report.json` | status, 실패 사례, 파라미터, 처리 시간 | - |
| `<image_id>/fields.json` | 5필드 ROI, 필드별 실패 유형 | 원본 |
| `summary.json` | 전달용 요약: `image_id`, `target_fields`, `detected_fields`, `roi_coverage`, `failure_reason` | - |
| `summary.csv` | `summary.json` + Covered Rate, ROI 생성 수, 문서 그룹, 조건, status (Dataset v1) | - |
| `roi_coverage_overall.json` | 전체·공통·신규·조건별 Covered Rate, 평균 Coverage, 실패 수, sec/image, 동결 commit, 데이터 해시 (Dataset v1) | - |
| `roi_coverage_fields.csv` | 필드별 GT BBox, Coverage, Covered, 실패 유형 (Dataset v1) | 원본 |
| `roi_candidates.json` | 필드별 ROI 후보와 후보별 Coverage (Dataset v1) | 원본 |
| `field_summary.csv` | ROI 생성 기준 요약 + 문서 그룹, 조건, status, 표 수, GT bbox 수 | - |
| `field_results.csv` | 필드 단위 상세 | 원본 |
| `detected_roi.json` | 5필드 ROI 모음 (quad) | 원본 |
| `run_info.json` | 명령, 파라미터, 코드 해시, 환경, commit (`--dataset`, `--rerun` 실행 시 생성) | - |

`summary.json`의 의미는 폴더마다 다릅니다. Dataset v1(`output/eval_v1/`)은 GT BBox 기준 Coverage(`detected_fields` = Covered 필드 수, `roi_coverage` = 평균 Coverage)이고, 공통 10장(`output/common10/`)은 ROI 생성 비율입니다. `output/common10/summary.csv`는 `run_batch()`가 만드는 구조 복원 요약입니다.

### cells.json 형식

```json
{
  "image": "sample_aligned.png",
  "source_image": "sample.jpg",
  "method": "opencv_grid_merge",
  "rotation_deg": -1.061,
  "cells": [
    {"id": 0, "table": 0, "bbox": [0, 0, 100, 50], "type": "merged", "primitive_cells": [[0, 0], [0, 1]]}
  ]
}
```

- `bbox`: 정수 픽셀 `[왼쪽, 위, 오른쪽, 아래]`
- `type`: `general`(격자 1칸) 또는 `merged`(격자 2칸 이상)
- `table`: 페이지 안의 표 번호 (위에서 아래 순)
- `primitive_cells`: 그 표 안의 `[행, 열]`

## 실패 유형

| 유형 | 판정 |
|---|---|
| `TABLE_MISSING` | 필드가 있어야 할 표를 못 찾음, 또는 그 위치에 셀이 없음 |
| `ROW_MERGE` | 셀 높이 > 기준 셀 높이 × 1.8 |
| `COLUMN_MERGE` | 셀 폭 > 기준 셀 폭 × 1.8 |
| `CELL_MERGE` | 높이와 폭 모두 초과 |
| `WRONG_MAPPING` | 후보는 GT BBox를 0.90 이상 못 덮는데 이미지의 다른 셀이 덮음 |
| `COORDINATE_ERROR` | GT BBox를 0.90 이상 덮는 셀이 이미지 어디에도 없음 (경계 어긋남·분할) |
| `RUN_ERROR` | 파이프라인 실행 실패 |

P3 Coverage에서는 Covered가 아닌 필드에만 실패 유형을 기록합니다. Covered이지만 고른 셀이 병합 크기인 18필드는 실패로 세지 않고 `roi_flag`에 `ROW_MERGE` 등을 남겼습니다 (ROI가 커서 OCR에 다른 글자가 섞일 수 있음).

## 알려진 한계

- 원근 왜곡은 보정하지 않습니다. perspective 조건 4장은 모두 5필드 ROI를 만들지 못했습니다.
- 촬영 원근이나 종이 휨이 있으면 가로선 투영이 겹쳐 여러 행이 하나로 합쳐질 수 있습니다.
- 한 행 높이보다 짧은 세로 경계는 선 추출에서 지워져 라벨 칸과 값 칸이 합쳐질 수 있습니다.
- 선이 없는 표는 지원하지 않습니다.
- 필드 위치는 기준 양식의 상대 위치로 고르므로, 같은 양식의 계약서를 전제로 합니다.
