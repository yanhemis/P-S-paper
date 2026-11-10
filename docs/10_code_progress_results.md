# bang_ 코드별 진행과 결과

> 담당: OpenCV 구조 복원 / Detected ROI (논문 파이프라인의 P3 입력)
> 기준: issue 브랜치 `05_current_team_tasks_20261101.md` 2절
> 동결 commit: `55c30b0` (11/10 16:42), 기록 파일 `frozen_params.json` (첫 동결 `11af316`). 동결 선언: [11_freeze_declaration.md](11_freeze_declaration.md)

## 1. 한눈에 보기

| 코드 | 줄 수 | 역할 | 시기 | 대표 결과 | 상태 |
|---|---:|---|---|---|---|
| `TestResult.py` | 459 | 초기 구조 복원 | 09/14 | sample.jpg 표선 검출 실패 | 보관용 |
| `Task_0930.py` | 1,046 | 구조 복원 메인 | 09/28 ~ 10/05 | sample.jpg F1 77.3% (IoU 0.5, 공통 평가) | 동결 |
| `tail_roi.py` | 116 | tail OCR 입력 변환 | 10/13 | 필드 25/60 전달, OCR Field Accuracy 13/49 | 이전 전달본 |
| `Task_10_Renewal.py` | 550 | 일괄 실행·재현 확인·동결 | 10/13 ~ 11/06 | 공통 10장 셀 파일 40/40 재현, development 19장 실행 | 동결 |
| `field_roi.py` | 228 | 5필드 ROI·실패 유형 | 11/06 | ROI 생성 41/94 (43.6%) | 동결 |
| `p3_detected_roi_coverage.py` | 431 | GT BBox 기준 P3 ROI Coverage | 11/09 | Covered 36/94 (38.3%), 평균 Coverage 0.590 | 동결 |

```text
이미지 → Task_0930.py → 셀 → field_roi.py → 5필드 ROI·실패 유형
           (구조 복원)             (필드 대응)
                              → p3_detected_roi_coverage.py → ROI 후보 + GT BBox Coverage → P3 평가 입력
                    Task_10_Renewal.py 가 전체 실행과 재현·동결을 관리
```

## 2. 코드별 내용

### 2.1 `TestResult.py` — 초기 구조 복원 (보관용)

**구현:** HoughLinesP 기울기 보정, 해상도 비례 파라미터, 경계 판정, Union-Find 병합 셀 복원, `cells.json` 저장

**결과:** 선 추출 커널이 이미지 높이의 40%라서, 촬영본 sample.jpg에서 표선이 지워져 셀을 만들지 못했습니다(행 경계 0개, 열 경계 0개). 11/07에 다시 실행해도 같은 결과입니다. 이 한계 때문에 `Task_0930.py`로 넘어갔습니다.

### 2.2 `Task_0930.py` — 구조 복원 메인

**구현**

| 단계 | 내용 |
|---|---|
| 입력 보정 | EXIF 회전 반영, 기울기 보정, 회전 시 캔버스 확장 |
| 이진화 | CLAHE + adaptive threshold, 해상도 비례 파라미터 |
| 선·표 검출 | 해상도 비례 고정 길이 커널, 끊어진 선 연결, 한 페이지 여러 표 분리 |
| 셀 복원 | 경계 판정, Union-Find 병합, 비직사각형 병합 복구 |
| 자동 검증 | 선 검출 실패, 과다·미병합 의심 등 7종 기록 |
| 출력 | 보정본·원본 좌표 셀, 병합 전 격자, 시각화, `report.json` |

**결과: sample.jpg 단일 이미지, GT 95셀**

평가는 다혜 학우의 공통 평가 기준을 따릅니다. **논문 비교에는 이 표를 사용합니다.**

| 방법 | F1 @ IoU 0.3 | F1 @ IoU 0.5 | F1 @ IoU 0.7 |
|---|---:|---:|---:|
| Primitive Grid | 49.7% | 38.7% | 25.8% |
| Grid + Cell Reconstruction | **88.4%** | **77.3%** | **65.2%** |

IoU 0.5 세부: Restored TP 70, FP 16, FN 25, Precision 81.4%, Recall 73.7%

**자체 측정값과의 차이**

같은 GT와 같은 1:1 매칭으로 두 입력 파일을 다시 계산한 결과입니다.

| 원본 좌표 변환 방식 | 사용처 | 셀 | TP @ 0.5 | F1 @ 0.3 | F1 @ 0.5 | F1 @ 0.7 |
|---|---|---:|---:|---:|---:|---:|
| 네 꼭짓점을 역변환한 외접 사각형 | 공통 평가 | 86 | 70 | 88.4% | 77.3% | 65.2% |
| 셀 중심만 역변환하고 크기 유지 (`to_original`) | 자체 측정 | 86 | 78 | 92.8% | 86.2% | 75.1% |

검출된 셀 수는 같고 좌표 변환 방식이 다릅니다. 자체 측정값 86.2%는 코드 개발 기록으로만 남기고, 다른 방법과 비교할 때는 77.3%를 사용합니다.

**재현 확인 (sample.jpg, 11/07)**

| 코드 | 환경 (numpy / pillow) | 결과 | 기존 파일과 비교 |
|---|---|---|---|
| `Task_0930.py` | 2.5.3 / 12.3.0 | 표 2개, 셀 86개, -1.06°, `ok` | 공통 평가에 쓰인 `cells.json`과 셀 전체 동일 |
| `Task_0930.py` | 2.3.5 / 12.0.0 (동결 환경) | 표 2개, 셀 86개, -1.06°, `ok` | 10/05 전달본 `cells_original.json`과 셀 전체 동일 |
| `TestReult.py` (이전 코드) | 2.3.5 / 12.0.0 | 행 경계 0개, 열 경계 0개 | 셀 생성 실패 |

공통 평가 감사 문서(`coordinate_audit.md`)의 "현재 파이프라인 재현 실패, 행·열 0개"는 이전 코드의 증상과 같습니다. 해당 브랜치에는 `TestReult.py`만 있고 `Task_0930.py`가 없습니다. 이 항목은 `Task_0930.py`로 다시 확인하도록 다혜 학우에게 요청합니다.

**해석 시 주의:** 단일 이미지의 두 표 영역 결과이므로 다른 계약서로 일반화할 수 없습니다. Primitive와 Restored의 차이도 병합 복원만의 인과 효과로 단정하지 않습니다.

**전달:** 10/04 추가 인원 A에게 ROI OCR용 셀 86개와 크롭 이미지, 10/05 추가 인원 B에게 입출력 명세와 원본 좌표 파일을 전달했습니다.

**사례 문서:** [성공 사례](02_success_cases.md), [실패 사례](03_failure_cases.md)

### 2.3 `tail_roi.py` — tail OCR 입력 변환

**구현:** 공통 10장의 검출 셀 중 tail GT ROI를 가장 많이 덮는 셀을 골라 OCR 입력 형식으로 변환합니다. 표를 못 찾았거나 과다 병합된 필드는 뺐습니다.

**결과**

| 항목 | 값 |
|---|---:|
| 전달 필드 (보조 필드 포함) | 25/60 |
| 5필드 기준 ROI 기록 | 22/49 (44.9%) |
| 이 입력으로 수행한 OCR Field Accuracy (tail·다혜 집계) | 13/49 (26.5%) |
| ROI가 있는 경우의 조건부 정확도 | 13/22 (59.1%) |

GT 위치로 셀을 골랐기 때문에 "필드 위치를 알 때 검출 셀 경계로 자른 성능"입니다. 자동 필드 탐색 성능은 포함되지 않습니다. 정확도 저하의 주원인은 ROI 누락 27개입니다.

### 2.4 `Task_10_Renewal.py` — 일괄 실행·재현 확인·동결

**구현**

| 기능 | 내용 |
|---|---|
| 일괄 실행 | 공통 10장, development, holdout_test를 같은 설정으로 실행 |
| 재현 확인 | `--check-repro`: 임시 폴더에 다시 실행해 기존 결과와 비교 |
| 실행 기록 | 명령, 파라미터, 코드 해시, 환경, commit, 데이터셋 해시 저장 |
| 동결 | `--freeze`: 코드에 미커밋 변경이 있으면 거부 |
| 패키지 사전 확인 | `--check-package`: 필수 열, 파일, GT 키, 그룹 중복, 동결 일치를 실행 없이 확인 (11/10) |
| holdout 보호 | 동결 불일치, 재실행, 문서 그룹 중복이면 실행 거부 |
| 전달 형식 | `summary.json`, `<image_id>_aligned.png` |
| P3 Coverage 연결 | Dataset v1 실행 끝에 `p3_detected_roi_coverage.py` 를 자동 실행 (11/09) |

**결과: 공통 10장 구조 복원 (육안 판정 포함)**

| 구분 | 이미지 |
|---|---|
| 성공 (2장) | sample_1, sample_2 |
| 부분 (3장) | sample_4, sample_6, sample_8 |
| 실패 (5장) | sample_3, sample_5, sample_7, sample_9, sample_10 |

주요 실패 원인은 촬영 원근과 종이 휨으로 가로선 투영이 겹쳐 여러 행이 합쳐지는 것입니다. 상세는 [공통 10장 결과](07_common10_results.md)에 있습니다.

**결과: 재현성**

| 환경 | numpy / pillow | 공통 10장 셀 파일 40개 |
|---|---|---:|
| 동결 환경 (`requirements_frozen.txt`) | 2.3.5 / 12.0.0 | **40개 동일** |
| 비교 환경 | 2.5.3 / 12.3.0 | 20개 다름 |

OpenCV 버전은 같습니다(5.0.0). numpy와 pillow 중 어느 쪽이 원인인지는 분리하지 않았습니다. 라이브러리 버전만 달라도 결과가 크게 바뀔 수 있어(sample_3 셀 18개 → 49개), 환경을 동결 항목에 포함했습니다.

### 2.5 `field_roi.py` — 5필드 ROI·실패 유형

**구현**

- 기준 이미지 sample_1에서 필드 셀의 표 안 상대 위치를 기록하고, 새 이미지에서 같은 위치의 셀을 고릅니다. GT와 글자 인식은 쓰지 않습니다.
- 기준 셀 크기와 비교해 병합 오류를 판정합니다.
- GT bbox가 있으면 `WRONG_MAPPING`과 `COORDINATE_ERROR`도 판정합니다.
- GT가 `not_present`인 필드는 분모에서 뺍니다.

**결과: Dataset v1.0 development 19장**

| 묶음 | 이미지 | 5필드 | ROI Coverage | 위치 검증 |
|---|---:|---:|---:|---|
| 공통 10장 | 10 | 21/49 | 42.9% | GT bbox 있음, GT 평균 87.7% 덮음 |
| 신규 | 9 | 20/45 | 44.4% | GT bbox 없음, 육안 확인만 수행 |
| **전체** | **19** | **41/94** | **43.6%** | |

**필드별**

| 필드 | 생성 / 대상 | 비율 |
|---|---:|---:|
| `address` | 7/19 | 36.8% |
| `deposit` | 7/19 | 36.8% |
| `contract_amount` | 7/18 | 38.9% |
| `lessor_name` | 10/19 | 52.6% |
| `lessee_name` | 10/19 | 52.6% |

**신규 9장 촬영 조건별** (문서 그룹 3개이므로 독립 문서 수가 아닙니다)

| 조건 | 이미지 | 5필드 | 비율 |
|---|---:|---:|---:|
| baseline | 3 | 12/15 | 80.0% |
| distance | 2 | 8/10 | 80.0% |
| perspective | 4 | 0/20 | 0.0% |

**실패 유형 (53건)**

| 유형 | 건수 |
|---|---:|
| `ROW_MERGE` | 28 |
| `TABLE_MISSING` | 23 |
| `COLUMN_MERGE` | 1 |
| `CELL_MERGE` | 1 |
| `WRONG_MAPPING` | 0 (공통 10장 기준, 신규 9장은 판정 불가) |
| `COORDINATE_ERROR` | 0 (공통 10장 기준, 신규 9장은 판정 불가) |
| `RUN_ERROR` | 0 |

위 값은 GT 없이 **ROI를 만든 비율**(11/06 기준)이며 위치 정합을 보증하지 않습니다. 평가 기준 수치는 아래 2.6의 GT BBox Coverage입니다.

### 2.6 `p3_detected_roi_coverage.py` — GT BBox 기준 P3 ROI Coverage

**구현**

- 기준 양식 위치의 중심을 포함하는 셀(primary)과 그 영역에 50% 이상 겹치는 같은 표의 셀을 필드별 ROI 후보로 냅니다 (최대 5개, GT 미사용).
- `Coverage = Area(GT ∩ ROI) / Area(GT)`를 후보마다 계산해 최대값을 쓰고, 0.90 이상이면 Covered입니다.
- Covered가 아닌 필드에 실패 유형을 남깁니다. GT를 0.90 이상 덮는 셀이 이미지에 있으면 `WRONG_MAPPING`, 없으면 `COORDINATE_ERROR`입니다.
- 셀 결과를 다시 만들지 않고 읽기만 하므로 구조 복원 결과와 파라미터는 바뀌지 않습니다.
- 11/09에 동결 대상(`CODE_FILES`)에 넣고, `Task_10_Renewal.py --dataset <split>` 끝에서 자동 실행되게 했습니다.

**결과: Dataset v1.0 development 19장 (GT `ead8436`)**

| 묶음 | 이미지 | Covered | Covered Rate | 평균 Coverage | ROI 생성 |
|---|---:|---:|---:|---:|---:|
| 공통 10장 | 10 | 21/49 | 42.9% | 0.662 | 43/49 |
| 신규 heewon | 6 | 8/30 | 26.7% | 0.457 | 18/30 |
| 신규 tail | 3 | 7/15 | 46.7% | 0.620 | 10/15 |
| **전체** | **19** | **36/94** | **38.3%** | **0.590** | **71/94** |

**필드별**

| 필드 | Covered / 대상 | 평균 Coverage |
|---|---:|---:|
| `address` | 7/19 | 0.644 |
| `deposit` | 9/19 | 0.601 |
| `contract_amount` | 7/18 | 0.565 |
| `lessor_name` | 6/19 | 0.557 |
| `lessee_name` | 7/19 | 0.580 |

**신규 9장 촬영 조건별**

| 조건 | 이미지 | Covered | 평균 Coverage |
|---|---:|---:|---:|
| baseline | 3 | 10/15 | 0.942 |
| distance | 2 | 5/10 | 0.888 |
| perspective | 4 | 0/20 | 0.000 |

**Covered 아님 (58필드)**: `TABLE_MISSING` 23, `COORDINATE_ERROR` 23 (Coverage 0.709~0.898), `ROW_MERGE` 12, `WRONG_MAPPING` 0

**GT 버전별 기록**

| GT | 평가 필드 | Covered | 비고 |
|---|---:|---:|---|
| `d4b32b6` | 79 | 29/79 (36.7%) | tail 15필드 `bbox: null`, dahye 독립 재계산과 일치 |
| `ead8436` | 94 | 36/94 (38.3%) | tail GT BBox 추가, 공통·heewon 값은 같음 |

이미지별 결과는 [Detected ROI 전달 문서](09_detected_roi_v1.md)와 `output/eval_v1/development/summary.json`에 있습니다.

## 3. 현재 결론

1. **병합 복원 효과:** 단일 이미지 공통 평가에서 F1이 38.7%에서 77.3%로 관찰됐습니다.
2. **병목은 촬영 조건:** 신규 데이터에서 perspective 조건은 Covered가 0/20이었고, baseline 10/15, distance 5/10이었습니다.
3. **실패는 표 누락, 경계 오차, 행 병합:** Covered가 아닌 58필드가 `TABLE_MISSING` 23, `COORDINATE_ERROR` 23, `ROW_MERGE` 12입니다. `COORDINATE_ERROR`는 모두 GT의 70% 이상은 덮었습니다.
4. **재현성은 환경에 달려 있음:** 코드와 파라미터가 같아도 라이브러리 버전이 다르면 셀 결과가 달라집니다.

## 4. 진행 상태

| 지시 항목 | 상태 |
|---|---|
| commit·파라미터 기록 | ✅ `frozen_params.json` (P3 Coverage 코드 포함) |
| 공통 10장 재현 확인 | ✅ 40/40 |
| development 동일 설정 실행 | ✅ 19/19 |
| `cells_original.json`, `report.json`, `cells.json` | ✅ 19/19 |
| aligned 이미지 | 🟡 19/19 생성, 용량 때문에 git 제외 |
| 실패 유형 기록 | ✅ 94필드 모두 GT BBox로 판정 |
| ROI Coverage summary | ✅ `summary.json`, `roi_coverage_overall.json` (Covered ≥ 0.90, 후보 최대값) |
| holdout_test 1회 실행 | ✅ 6장, 3/30 (10.0%), 평균 Coverage 0.264 (`60f52cf`) |
| 동결 선언 | ✅ `docs/11_freeze_declaration.md` |

## 5. 재현 방법

```bash
python -m pip install -r requirements_frozen.txt
git archive origin/dataset-v1 data/eval_v1_packages/development | tar -x
python Task_10_Renewal.py --check-repro
python Task_10_Renewal.py --dataset development
```

PowerShell에서는 파이프 대신 `git archive -o dev.tar origin/dataset-v1 data/eval_v1_packages/development` 후 `tar -xf dev.tar`를 씁니다.
