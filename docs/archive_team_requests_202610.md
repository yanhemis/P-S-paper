# (보관) 팀원 요청사항 — 2026-10 초 기준

> 10/21·11/01 재배정 이전의 협업 요청 기록이다. 기한과 담당이 현재와 다르다. 현재 역할은 `../plan.md`, 팀 기준은 `issue/05_current_team_tasks_20261101.md`.


### 담당 정리 (`issue/README.md` 기준)

| 담당 | 역할 | 최종 마감 |
|---|---|---|
| `bang_` | OpenCV Cell/ROI + merged reconstruction | 10/04 |
| `dahye_cell_DetectionSurvey` | 구조 모델 비교 + **공통 evaluator** | 10/05 |
| `heewon` | Morphology vs Contour + Pipeline 현행화 | 10/04 |
| `taegu` | Anchor-ROI / Field Mapping | 10/06 |
| `tail` (= 추가 인원 A) | Full OCR vs ROI 재인식 | 10/07 |
| 추가 인원 B | **서버 의존성 / End-to-End 통합** | 10/10 |

※ `taegu`와 추가 인원 B는 다른 사람이다. 추가 인원 B의 배정 파일명(`assignment_member_B_anchor_roi_field_mapping.md`)과 일부 이전 문서(`01_research_direction…`, `feedback_bang…`)에는 예전 역할(Anchor-ROI)이 남아 있지만, 9/22에 서버 통합으로 역할이 바뀌었다.

### 기한

tail 최종 마감 **2026-10-07**에서 거꾸로 잡았다. 실험 C 실행 자체는 몇 분이면 되지만, 결과 해석과 비교표 작성에 하루가 필요하다.

| 요청 | 대상 | 기한 |
|---|---|---|
| 우리 10장 셀 검출 결과 (`cells.json` + 필요하면 `report.json`) | `bang_` | **2026-10-05** |
| 우리 10장 필드 ROI (`docs/ocr_io_spec.md` 1절 형식) | `taegu` | **2026-10-06 오전** (taegu 마감과 같은 날) |
| 보증금 대표값(숫자/한글) 결정 | `taegu` + `tail` (+ 팀) | **2026-10-05** |
| 공통 evaluator 정규화 규칙 맞추기 | `dahye` (evaluator 담당) + `taegu` + `tail` | **2026-10-05** |
| 셀 bbox (비교군, 선택) | `heewon` | 2026-10-06 |
| OCR 모듈 규격·의존성·실행 순서 확인 | 추가 인원 B | 2026-10-07 (B 마감 10/10) |

기한까지 ROI를 받지 못하면, 실험 C는 공통 `sample.jpg` 1장 결과만으로 보고하고 10장 결과는 "미완료"로 남긴다.

### `bang_` (OpenCV Cell/ROI 검출)

1. **우리 10장에 셀 검출 실행 요청**: `tail/sample_data_jpg/sample_data_v1/sample_1.JPG ~ sample_10.JPG`
   - 현재 `bang_/output/`에는 공통 `sample.jpg` 결과만 있어서 실험 C를 돌릴 수 없다
2. **좌표계**: 원본 좌표(EXIF 회전 적용 후)로 주면 가장 좋다. 정렬(deskew) 이미지 좌표로 줄 경우 이미지별 `report.json`(affine 포함)을 함께 달라
   - `sample.jpg` 결과를 affine 역변환해 원본에 겹쳐 본 결과, 표 선에는 정확히 맞았다 → [`results/eval/teammate_roi_check_sample_top.jpg`](results/eval/teammate_roi_check_sample_top.jpg)
3. **확인 필요 — 성명 칸 상단 경계**: `sample.jpg`의 임대인·임차인 성명 셀 위쪽 경계가 손글씨 이름 중간을 지나간다. 그래서 정답 글자의 76~82%만 셀 안에 들어온다 → [`results/eval/teammate_roi_check_sample_bottom.jpg`](results/eval/teammate_roi_check_sample_bottom.jpg). 손글씨 획을 표 선으로 오검출했는지 확인 부탁
4. **참고 — 보증금/계약금 행**: 행 전체(가로 약 2,170px)가 병합 셀 하나로 나온다. 한글 금액, `원정 (₩`, 숫자 금액이 한 셀에 들어 있다. 셀 구조상으로는 맞지만, 필드 값을 뽑으려면 셀 내부를 나누는 단계(taegu 담당)가 필요하다

### `taegu` (Anchor-ROI / Field Mapping)

1. **우리 10장에 대해 필드 ROI 출력 요청**: `docs/ocr_io_spec.md` 1절 형식으로 받으면 바로 실험 C에 넣을 수 있다 (`bang_` 셀 기반이든 anchor 기반이든 무관, 어떤 방식인지만 명시)
2. **필드 키·정의 맞추기**:

   | taegu | tail | 비고 |
   |---|---|---|
   | `소재지` | `address` | |
   | `보증금` | `deposit_kor` (+ `deposit_num`) | taegu `보증금`은 한글 금액(`일억`). tail은 숫자 금액을 대표값으로 쓰고 한글 금액은 보조 |
   | `계약금` | `down_payment` | |
   | `임대인_성명` | `lessor_name` | |
   | `임차인_성명` | `lessee_name` | |

   → **보증금 대표값을 숫자로 할지 한글로 할지 팀 차원에서 정하자** (tail 결과: 숫자 칸이 한글 칸보다 훨씬 정확함, EM 7~8/10 vs 2/10)
3. **정답 확인**: `field_gt.json`의 sample.jpg 소재지가 `…4층 401`인데, 이미지에는 `401호`로 적혀 있다 (tail 변환본에서는 `401호`로 고쳐서 사용, 원본 파일은 건드리지 않음)
4. **ROI 크기**: 현재 `value_roi`는 라벨 폭의 6배, 라벨 높이의 ±50%로 잡은 고정 비율 영역이다. 정답 대비 면적이 13~18배이고, 보증금 ROI가 계약금 행까지, 계약금 ROI가 중도금 행까지 내려간다. ROI를 다시 OCR하는 실험 C에서는 다른 행 글자가 섞여 결과가 나빠질 수 있다 → sample.jpg로 실제로 돌려 보니 **보증금·계약금이 다른 행 값과 섞여 실패**했다 (2-3절). ROI 높이를 해당 행으로 줄여 달라
5. **평가 중복 정리**: `taegu/evaluate_fields.py`는 원문을 그대로 비교하고, `tail/scripts/evaluate_fields.py`는 정규화한 뒤 비교한다(공백·인쇄 글자·쉼표 제거, `docs/ocr_io_spec.md` 4절). 같은 예측이라도 점수가 달라지므로, 공통 evaluator 담당인 `dahye`와 함께 정규화 규칙을 하나로 정하자

### `dahye_cell_DetectionSurvey` (공통 evaluator)

- 필드 단위 평가(Field Accuracy / CER / Exact Match)에 쓸 **정규화 규칙을 공통 evaluator에 맞추자**. tail 규칙은 `docs/ocr_io_spec.md` 4절에 있다
- 현재 공통 GT(`5_Evaluation/gt_sample.json`)는 sample.jpg의 셀 bbox뿐이다. 필드 단위 정답이 필요하면 tail의 `gt/gt_fields.json`, `gt/gt_roi.json`(10장)을 써도 된다

### 추가 인원 B (서버 의존성 / End-to-End 통합)

B가 tail에게서 받기로 한 것은 "OCR/ROI 재인식 모듈과 결과 포맷"이다. 아래 세 가지를 전달한다.

1. **의존성**: [`requirements.txt`](requirements.txt). Python 3.11, CPU 실행만 확인했다. 같은 환경에 OpenCV 패키지가 두 개 깔려 있어서 서버에서는 하나만 설치하기를 권장한다. 모델은 `~/.paddlex/`에 자동으로 다운로드된다
2. **입출력 규격**: [`docs/ocr_io_spec.md`](docs/ocr_io_spec.md). ROI 입력 형식, ROI OCR 출력, 전체 페이지 OCR 출력, 정규화 규칙
3. **실행 순서와 entry point**: 4절 "실행 방법". End-to-End에서 tail 모듈이 들어가는 위치는 아래와 같다

   ```text
   이미지 → (bang_ Cell/ROI) → (taegu Field Mapping: 필드별 ROI) → [tail] roi_ocr.py → 필드 값 JSON
                 └────────────── [tail] ocr_baseline.py (전체 페이지 OCR = 비교 기준선. taegu는 자체 full_ocr.py로 anchor를 찾음)
   ```

- 서버 메모리 주의: 서버 검출 모델은 4000×3000 이미지에서 54GB까지 올라간다. mobile 모델 설정을 바꾸지 말 것

### `heewon`

- 현재 폴더에는 노트북과 비교표만 있고 bbox 결과 파일이 없다. 실험 C의 비교군으로 쓸 수 있도록, 가장 좋은 설정(Contour 50/20, F1 26.7%)으로 우리 10장의 셀 bbox를 뽑아 주면 `bang_` 결과와 같이 비교하겠다

### 전원 — 데이터 관련 공유

- 우리 10장과 정답 데이터는 자유롭게 써도 된다: `sample_data_jpg/`, `gt/gt_fields.json`, `gt/gt_roi.json`
- **파일 번호와 데이터 세트 번호가 다른 장이 있다**: `sample_5`=#6, `sample_6`=#5, `sample_8`=#9, `sample_9`=#8. 정답은 `gt/gt_fields.json`(이미지 파일명 기준)을 쓰면 된다
- #7(`sample_7`)은 접힌 문서이고, 종이에 인쇄 글자와 표 선이 한 줄 가까이 어긋나 인쇄돼 있다. 계약금은 미기입이라 평가에서 제외했다
- 팀에 묻고 싶은 질문은 [`question.md`](question.md)에 정리했다
