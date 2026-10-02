# tail — OCR / ROI 재인식 / Field Accuracy

> 담당 질문: **전체 페이지 OCR보다 핵심 필드 ROI를 잘라 다시 OCR했을 때 문자 인식과 Field Accuracy가 좋아지는가?** (H1, H5)
> 배정 문서: [`plan.md`](plan.md) · 상세 작업 기록: [`PROGRESS.md`](PROGRESS.md) · 최종 마감 2026-10-07
> 마지막 업데이트: 2026-10-03

---

## 1. 현재 상태 요약

| 단계 | 상태 |
|---|---|
| 09/25 조기 체크 (Full OCR baseline 실행·저장·시각화) | ✅ 완료 |
| 자체 계약서 데이터 10장 촬영 | ✅ 완료 |
| 실험 A — 전체 페이지 OCR | ✅ 10장 완료 |
| Ground Truth (정답 텍스트 + 정답 ROI) | ✅ 10장 × 5필드 완료 |
| 실험 B — GT ROI OCR | ✅ 10장 완료 |
| CER / Exact Match / confidence / Field Accuracy / sec/image | ✅ A vs B 비교 완료 |
| 대표 성공·실패 사례 | ✅ 8개 정리 |
| OCR 입출력 규격 문서 | ✅ 작성 완료 (전달 필요) |
| **실험 C — 실제 검출 ROI OCR** | ⏳ **팀원 ROI 결과 대기** (아래 5절) |

---

## 2. 핵심 결과 (10장, 평가 필드 49개)

| 방법 | Field Accuracy (Exact Match) | 평균 CER | 평균 confidence | sec/image |
|---|---|---|---|---|
| 실험 A: Full OCR | 29/49 (59.2%) | 0.141 | 0.886 | 29.93 |
| 실험 B: GT ROI OCR | **31/49 (63.3%)** | **0.117** | 0.874 | 0.93 (ROI당 0.15) |

| 필드 | Full OCR (EM · CER) | GT ROI OCR (EM · CER) |
|---|---|---|
| 소재지 | 0/10 · 0.316 | 0/10 · 0.270 |
| 보증금 (숫자) | 7/10 · 0.068 | 8/10 · 0.024 |
| 보증금 (한글, 보조) | 2/10 · 0.322 | 2/10 · 0.289 |
| 계약금 | 6/9 · 0.119 | 7/9 · 0.096 |
| 임대인 성명 | 7/10 · 0.167 | 8/10 · 0.133 |
| 임차인 성명 | 9/10 · 0.033 | 8/10 · 0.058 |

- **ROI 재인식 효과는 있지만 작다** (+2건 / 49). 표본이 작아서 통계적으로 확실한 차이라고 보기는 어렵다
- **ROI가 해결하는 문제 = 박스 병합**: 전체 페이지에서 한글 금액, 인쇄 글자, 숫자 금액이 한 박스로 묶여 값이 섞이는 경우
- **ROI로 해결되지 않는 문제 = 손글씨 인식 한계**: 소재지는 두 방법 모두 0/10이고, 손글씨 `오`·`천` 오인식이 반복됨 (위치가 아니라 인식 모델의 문제)
- **ROI 때문에 나빠진 경우 2건**: crop 위아래 여유 때문에 다음 행 글자 조각이 섞임
- 전체 표: [`results/eval/summary.md`](results/eval/summary.md) · 사례: [`results/cases/cases.md`](results/cases/cases.md)

---

## 3. 파일 구조

```text
tail/
├── README.md                  # 이 문서
├── plan.md                    # 담당 배정 문서 (체크박스로 진행 표시)
├── PROGRESS.md                # 날짜별 상세 작업 기록
├── question.md                # 팀에 묻고 싶은 질문 (전세/월세, 양식 차이, 여러 장 촬영, 데이터 규모, 브랜치 운영)
│
├── contractForm/              # 계약서 양식 원본과 촬영 계획
│   ├── **부동산임대차계약서_양식.pdf      # ← 실험에 쓴 양식 (1페이지)
│   ├── 주택임대차_표준계약서(...).hwp/pdf  # 법무부 표준계약서
│   ├── 계약서_양식_비교_법무부표준계약서_vs_부동산임대차계약서.md
│   └── shooting_conditions.md            # 10장 촬영 조건 조합표 (H1 검증용)
│
├── sample_data_jpg/           # 입력 이미지
│   ├── sample_1 ~ sample_10.JPG          # 자체 촬영본 (가짜 정보 손글씨 기입, 4032×3024)
│   ├── sample_empty.JPG                  # 빈 양식 촬영본
│   ├── sample.jpg                        # 팀 공통 샘플 (dahye/bang_/taegu와 동일 파일)
│   └── fake_contract_data.md             # 세트 #1~#10 가짜 기입 데이터 (= 정답 원본)
│
├── scripts/
│   ├── ocr_baseline.py        # 실험 A: 전체 페이지 OCR → results/<stem>_ocr.json, _vis.png
│   ├── make_gt_roi.py         # GT ROI 생성 보조: 양식 템플릿 → 촬영본 호모그래피 → gt/gt_roi.json
│   ├── roi_ocr.py             # 실험 B/C: ROI crop → OCR → <out_dir>/<stem>_roi_ocr.json
│   └── evaluate_fields.py     # 평가: Full vs GT ROI (vs Detected ROI) → results/eval/
│
├── gt/
│   ├── template.png           # 양식 PDF를 300dpi로 렌더링한 기준 이미지
│   ├── gt_fields.json         # 정답 텍스트 (이미지 × 필드)
│   ├── gt_roi.json            # 정답 ROI (이미지 × 필드, 4점 quad + bbox, 원본 좌표)
│   └── check/                 # GT ROI 육안 검수용 이미지 10장
│
├── results/
│   ├── sample_{1..10}_ocr.json / _vis.png   # 실험 A 결과 (+ 공통 sample.jpg 결과)
│   ├── roi_gt/                # 실험 B 결과 + crops/ (ROI 60개)
│   ├── eval/                  # summary.md, field_results.json, 팀원 ROI 좌표 확인 이미지
│   └── cases/                 # 대표 성공·실패 사례 (cases.md + crop 이미지)
│
└── docs/
    └── ocr_io_spec.md         # OCR 모듈 입출력 규격 (ROI 입력 형식, 출력 형식, 정규화 규칙)
```

---

## 4. 실행 방법

환경: conda `tail` (Python 3.11, `paddlepaddle 3.3.1`, `paddleocr 3.7.0`, `opencv-python 4.10.0`)

```bash
conda activate tail

# 실험 A — 전체 페이지 OCR (장당 약 30초)
python scripts/ocr_baseline.py sample_data_jpg/sample_{1..10}.JPG

# GT ROI 생성 (이미 gt/gt_roi.json 있음. 새 이미지를 추가할 때만 실행하고 gt/check/로 반드시 육안 검수)
python scripts/make_gt_roi.py sample_data_jpg/sample_{1..10}.JPG

# 실험 B — GT ROI OCR
python scripts/roi_ocr.py gt/gt_roi.json results/roi_gt

# 실험 C — 검출 ROI OCR (팀원 ROI를 docs/ocr_io_spec.md 1절 형식으로 받은 뒤)
python scripts/roi_ocr.py <detected_roi.json> results/roi_detected

# 평가
python scripts/evaluate_fields.py                                  # A vs B
python scripts/evaluate_fields.py --detected results/roi_detected  # A vs B vs C
```

주의:
- OCR 모델은 `PP-OCRv5_mobile_det` + `korean_PP-OCRv5_mobile_rec`로 고정했다. 기본값(서버 모델)은 16GB RAM에서 OOM이 난다. 자세한 내용은 PROGRESS.md 09-23 참고
- 모든 좌표는 **EXIF 회전을 적용한 원본 이미지 기준**이다 (3024×4032 세로)

---

## 5. 팀원 요청사항

### `bang_` (OpenCV Cell/ROI 검출)

1. **우리 10장에 셀 검출 실행 요청**: `tail/sample_data_jpg/sample_1.JPG ~ sample_10.JPG`
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
3. **ROI 크기**: 현재 `value_roi`는 라벨 폭의 6배, 라벨 높이의 ±50%로 잡은 고정 비율 영역이다. 정답 대비 면적이 13~18배이고, 보증금 ROI가 계약금 행까지, 계약금 ROI가 중도금 행까지 내려간다. ROI를 다시 OCR하는 실험 C에서는 다른 행 글자가 섞여 결과가 나빠질 수 있다
4. **평가 중복 정리**: `taegu/evaluate_fields.py`는 원문을 그대로 비교하고, `tail/scripts/evaluate_fields.py`는 정규화한 뒤 비교한다(공백·인쇄 글자·쉼표 제거, `docs/ocr_io_spec.md` 4절). 같은 예측이라도 점수가 달라지므로 공통 evaluator를 하나로 정하자

### 추가 인원 B (OCR 결과 통합)

- 통합용 입출력 규격: [`docs/ocr_io_spec.md`](docs/ocr_io_spec.md) — ROI 입력 형식, ROI OCR 출력 형식, 전체 페이지 OCR 출력 형식, 필드 값 정규화 규칙

### `heewon`

- 현재 폴더에는 노트북과 비교표만 있고 bbox 결과 파일이 없다. 실험 C의 비교군으로 쓸 수 있도록, 가장 좋은 설정(Contour 50/20, F1 26.7%)으로 우리 10장의 셀 bbox를 뽑아 주면 `bang_` 결과와 같이 비교하겠다

### 전원 — 데이터 관련 공유

- 우리 10장과 정답 데이터는 자유롭게 써도 된다: `sample_data_jpg/`, `gt/gt_fields.json`, `gt/gt_roi.json`
- **파일 번호와 데이터 세트 번호가 다른 장이 있다**: `sample_5`=#6, `sample_6`=#5, `sample_8`=#9, `sample_9`=#8. 정답은 `gt/gt_fields.json`(이미지 파일명 기준)을 쓰면 된다
- #7(`sample_7`)은 접힌 문서이고, 종이에 인쇄 글자와 표 선이 한 줄 가까이 어긋나 인쇄돼 있다. 계약금은 미기입이라 평가에서 제외했다
- 팀에 묻고 싶은 질문은 [`question.md`](question.md)에 정리했다

---

## 6. 남은 작업 (tail)

- [ ] 실험 C 실행 및 A/B/C 비교표 (팀원 ROI 수신 후 바로 가능)
- [ ] 촬영 조건 매핑 확인 → 조건별 비교 (H1)
- [ ] (선택) ROI 후처리: crop 가장자리에 걸친 작은 박스 제거, 위아래 여유 비율 조정
- [ ] (선택) 잔금 / 계약기간 필드 추가
- [ ] 결과 시각화 PNG 용량 정리 (장당 약 18MB) 후 커밋
