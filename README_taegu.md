# P4 — Anchor 기반 Field ROI 및 2차 OCR

## 목적

부동산 임대차계약서 이미지에서 Anchor(항목명)를 찾아 필드별 ROI를 생성하고, 해당 영역에 2차 OCR을 수행해 주요 계약 정보를 추출하는 실험용 파이프라인입니다.

## 처리 흐름

```text
계약서 이미지
  → 1차 전체 OCR (또는 동일 이미지의 저장된 OCR 결과 재사용)
  → Anchor 탐색 및 Field ROI 생성
  → ROI 이미지 Crop
  → ROI별 2차 PaddleOCR
  → 필드값 선택 및 결과 저장
```

대상 필드 5개:

| 필드 키 | 의미 |
|---|---|
| `address` | 소재지 |
| `deposit` | 보증금 |
| `contract_amount` | 계약금 |
| `lessor_name` | 임대인 성명 |
| `lessee_name` | 임차인 성명 |

## 실행 방법

프로젝트 가상환경에서 실행합니다.

```cmd
.venv\Scripts\activate
python run_p4_pipeline.py sample.jpg --first-pass-cache full_ocr_result.json
```

`--first-pass-cache`는 **해당 이미지에서 생성한 1차 OCR 결과**가 있을 때만 사용합니다. 다른 이미지에 `sample.jpg`의 OCR 캐시를 재사용하면 안 됩니다.

캐시 없이 실행할 때:

```cmd
python run_p4_pipeline.py sample.jpg
```

> 주의: 캐시 없이 전체 이미지 OCR을 실행한 시도에서는 약 10분 동안 완료되지 않아 사용자가 중단했습니다. 원인은 아직 확인되지 않았습니다. 위의 캐시 없는 실행 명령은 성공이 검증된 실행 경로가 아닙니다.

## 출력 파일

`results/p4_e2e/sample/`:

- `field_rois.json`: 필드별 ROI 좌표 및 관련 정보
- `final_fields.json`: 필드별 추출 결과
- `summary.csv`: 필드별 추출/평가 요약
- `first_pass_ocr.json`: 1차 OCR 결과
- `*_crop.png`: 필드별 ROI Crop 이미지

전체 요약: `results/p4_e2e/summary.csv`

Git에는 핵심 JSON/CSV 결과를 포함했습니다. `first_pass_ocr.json`과 Crop 이미지는 로컬에서 생성되며 현재 커밋에는 포함되지 않았습니다.

## 초기 실행 결과 (2026-11-04)

대상: `sample.jpg` **1장**, 5개 필드.

| 필드 | 추출값 | 비교 결과 |
|---|---|---|
| `address` | `서울특별시 강남구 테헤란로 123,4 401` | 불일치 (`4층` 인식 실패) |
| `deposit` | `일억` | 일치 |
| `contract_amount` | `일천만` | 일치 |
| `lessor_name` | `고결` | 일치 |
| `lessee_name` | `김영수` | 일치 |

- ROI 생성: **5/5**
- Field Exact Match (raw): **4/5 (80%)**
- 주소 필드 실패 기록: `OCR_FAILURE`

**해석상 주의:** 위 80%는 단일 이미지에서의 원문 일치율이며, 전체 데이터셋 정확도나 일반화 성능을 의미하지 않습니다. 공통 평가 기준이 확정되면 해당 기준으로 재평가해야 합니다.

## 확인된 한계 및 다음 작업

1. 주소의 `4층`이 `4`로 인식되는 오류 발생. 정답값을 하드코딩하지 않고 ROI 범위/인식 결과를 분석해야 합니다.
2. 1차 전체 OCR의 장시간 지연 원인은 미확인. 캐시 재사용 경로만 이번 실행에서 정상 완료됐습니다.
3. 추가 개발용 계약서 이미지 확보 후 문서별 ROI 검출률, 필드 일치율, 실패 유형을 비교해야 합니다.
4. 개발용 데이터와 최종 평가용 holdout 데이터를 분리하고, 최종 평가 전에 코드 버전을 고정해야 합니다.

## 코드 및 버전

- 실행 코드: `run_p4_pipeline.py`
- ROI 2차 OCR 실험 코드: `run_p4_roi_reocr_v2.py`
- 최초 결과 커밋: [`ef6d140`](https://github.com/yanhemis/P-S-paper/commit/ef6d140)
- 브랜치: `taegu`
