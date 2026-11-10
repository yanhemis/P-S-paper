# bang_ 동결 선언 (P3 Detected ROI)

> 기준 문서: issue 브랜치 `05_current_team_tasks_20261101.md` 8절 전달 순서 3)·5), 2절
> 받는 사람: dahye (P3 평가), 팀 전체

## 1. 동결 선언

| 항목 | 값 |
|---|---|
| 동결 commit | `55c30b0` (2026-11-10 16:42) |
| 동결 기록 commit | `44bc72d` — `frozen_params.json` |
| 동결 대상 코드 | `Task_0930.py`, `field_roi.py`, `Task_10_Renewal.py`, `p3_detected_roi_coverage.py` (SHA-256 기록) |
| 구조 복원 | method `opencv_grid_merge`, `Task_0930.PARAMS` 그대로 (`8143969` 이후 변경 없음) |
| 필드 대응 | 기준 이미지 sample_1, 표 매칭 허용 0.15, 병합 판정 1.8배 |
| P3 Coverage | Covered ≥ 0.90, 후보 중 최대값, 후보 최소 겹침 0.5, 후보 최대 5개 |
| 실행 환경 | Python 3.13.9, opencv 5.0.0, numpy 2.3.5, pillow 12.0.0 (`requirements_frozen.txt`) |

- 코드·파라미터·규칙은 **development 만 보고** 확정했다.
- 동결 이후 위 코드 4개와 파라미터는 바꾸지 않는다. 바꾸면 `Task_10_Renewal.py` 가 holdout 실행·평가를 거부한다.

## 2. 순서 기록

| 시각 (11/10) | 내용 |
|---|---|
| 16:04 | 가은 학우 holdout_test 공개 (`dataset-v1` `fb069e7`) |
| 16:42 | bang_ 코드 commit `55c30b0`, `--freeze` 로 동결 기록 |
| 16:43 | holdout_test 동결 설정 1회 실행 |
| 16:44 | holdout 결과 commit `60f52cf` |

holdout 공개가 동결보다 먼저였지만, 동결 전에는 holdout 패키지를 열거나 실행하지 않았다. 실행 기록 `output/eval_v1/holdout_test/run_info.json` 의 코드 해시·파라미터·환경은 `frozen_params.json` 과 같고, `code_files_modified: false` 이다.

## 3. 데이터

| split | 데이터 | 이미지 | 문서 그룹 |
|---|---|---:|---|
| development | `dataset-v1` `ead8436` | 19 | common_doc01~10, heewon_docA·B, tail_docA |
| holdout_test | `dataset-v1` `fb069e7` | 6 | tail_docB, tail_docC (development 와 겹치지 않음) |

## 4. 결과 (P3 ROI Coverage, Covered ≥ 0.90)

| split | Covered | Covered Rate | 평균 Coverage | ROI 생성 |
|---|---:|---:|---:|---:|
| development 공통 10장 | 21/49 | 42.9% | 0.662 | 43/49 |
| development 신규 9장 | 15/45 | 33.3% | 0.511 | 28/45 |
| development 전체 | 36/94 | 38.3% | 0.590 | 71/94 |
| **holdout_test 6장** | **3/30** | **10.0%** | **0.264** | **10/30** |

holdout_test 결과는 1회 실행값 그대로이며, 결과를 본 뒤 코드·파라미터를 바꾸지 않았다.

## 5. 전달 파일 (`bang_` 브랜치)

```text
output/eval_v1/development/     development 19장
output/eval_v1/holdout_test/    holdout_test 6장 (1회 실행)
  <image_id>/cells_original.json, cells.json, report.json, fields.json
  roi_candidates.json           필드별 ROI 후보 (원본 좌표) — P3 평가 입력
  summary.json                  image_id, target_fields, detected_fields, roi_coverage, failure_reason
  roi_coverage_overall.json     Covered Rate, 평균 Coverage, 실패 유형 수, 동결 commit, 데이터 해시
  run_info.json                 실행 명령, 코드 해시, 환경, commit
```

aligned 이미지는 용량 때문에 git 에 올리지 않았다. 동결 commit 에서 같은 명령으로 실행하면 같은 파일이 다시 생성된다.
