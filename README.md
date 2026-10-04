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
| H1 — 이미지 품질 영향 (인쇄 글자 비교 + 원본/전처리 비교) | ✅ 1차 분석 완료 (2-4절) |
| 개인정보 — 사진 GPS 위치정보 제거 | ✅ 현재 파일은 제거 완료 (이전 커밋에는 남아 있음, 2-6절) |
| **실험 C — 실제 검출 ROI OCR** | 🔶 파이프라인은 연결 완료 (공통 `sample.jpg` 1장, taegu ROI). **10장은 팀원 ROI 결과 대기** (아래 5절) |

---

## 2. 핵심 결과 (10장, 평가 필드 49개)

| 방법 | Field Accuracy (Exact Match) | 평균 CER | 평균 confidence | sec/image |
|---|---|---|---|---|
| 실험 A: Full OCR | 29/49 (59.2%) | 0.141 | 0.886 | 29.32 |
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

### 2-1. 현재 결론 (plan.md 최종 질문에 대한 중간 답)

> **"ROI를 정확히 특정하는 것이 실제 OCR 및 핵심 필드 추출 정확도 개선으로 이어지는가?"**
>
> → **부분적으로 그렇다.** 정답 ROI로 잘라 재인식하면, 전체 페이지에서 여러 칸이 한 박스로 합쳐지는 오류는 해결된다(Field Accuracy 59.2% → 63.3%, CER 0.141 → 0.117).
> 하지만 손글씨 글자 자체의 오인식(소재지 0/10, 한글 금액 2/10)은 ROI로 해결되지 않는다. 남은 오류의 대부분은 **위치가 아니라 인식 모델의 문제**다.
> 이 결과는 정답 ROI 기준의 상한선이다. 자동 검출 ROI에서도 개선이 유지되는지는 실험 C로 확인할 예정이다.
>
> **추가로 확인된 점 (H1 분석)**: ROI를 자르지 않고 페이지 전체를 **원근 보정만 해서** 전체 OCR을 돌려도 Field Accuracy가 31/49로, GT ROI OCR과 같았다.
> ROI 재인식의 이득 중 일부는 "칸을 특정한 효과"가 아니라 **문서를 크게(고해상도로) 보는 효과**일 수 있다. 논문에서 H5를 주장할 때 이 대조군을 같이 보고해야 한다.

### 2-2. 평가 방법과 용어

| 용어 | 정의 |
|---|---|
| 평가 단위 | 이미지 × 필드. 5개 우선 필드 × 10장 = 50개 중 #7 계약금(미기입) 1개를 빼서 **49개** |
| 정규화 | 비교 전에 예측과 정답 모두 공백, 인쇄 글자(`원정`, `금`, `(인)`, `₩` 등), 쉼표를 제거한다. 보증금 숫자는 숫자만 남긴다. 규칙 전체는 [`docs/ocr_io_spec.md`](docs/ocr_io_spec.md) 4절 |
| **Exact Match (EM)** | 정규화한 예측과 정답이 완전히 같으면 1, 아니면 0 |
| **Field Accuracy** | EM이 1인 필드 수 / 평가 필드 수. 이 문서의 필드 정확도는 모두 EM 기준 |
| **CER** | 정규화한 문자열 사이의 레벤슈타인 편집 거리 / 정답 글자 수. 0이면 완벽하고, 1을 넘을 수도 있다 |
| confidence | OCR rec score 평균. 필드에 쓰인 박스들의 평균이다 |
| sec/image | Full OCR은 한 장 전체의 OCR 시간이고, ROI 방법은 한 장의 ROI 6개 OCR 시간 합이다 |
| 보증금 | **숫자 금액(`deposit_num`)을 대표값**으로 평가한다. 한글 금액(`deposit_kor`)은 보조 지표로 따로 보고하며 전체 합계에는 넣지 않는다 |

**Full OCR 결과를 필드에 배정하는 방법** (A와 B를 공정하게 비교하기 위한 규칙)

전체 페이지 OCR은 박스 하나에 여러 칸의 글자가 섞이는 경우가 많다(예: `일천팔백만 원정은 계약시에 지급하고 영수함.`).
그래서 박스를 통째로 배정하지 않고 **글자 단위로** 배정한다.

1. 박스 polygon의 왼쪽 변과 오른쪽 변의 중점을 잇는 선을 글자 수만큼 등분해서 각 글자의 중심을 추정한다
2. 중심이 정답 ROI 안에 들어온 글자만 모은다. 이때 정답 ROI는 실험 B와 똑같이 위아래로 25% 늘린다
3. 박스 글자의 **50% 이상이 ROI 안이면 박스 전체를** 그 필드에 넣는다. 글자 폭이 일정하다는 가정 때문에 경계 글자가 잘리는 것을 막기 위해서다
4. 모은 글자를 ROI의 가로 방향 순서로 이어 붙인다

### 2-3. 실험 C 중간 결과 — 공통 `sample.jpg` 1장, taegu anchor ROI

팀원 결과가 아직 공통 `sample.jpg` 1장뿐이라, 파이프라인 연결 확인용으로만 돌렸다. **1장이라 수치 자체는 의미가 거의 없다.**
(정답은 `taegu/field_gt.json`을 변환해 썼다. 보증금은 한글 금액만 있어서 전체 합계는 4필드다.)

| 방법 | EM (4필드) | 평균 CER | sec/image |
|---|---|---|---|
| Full OCR | 3/4 | 0.012 | 30.94 |
| GT ROI OCR | 3/4 | 0.012 | 0.60 |
| Detected ROI OCR (taegu `value_roi`, 여유 0) | 2/4 | 1.024 | 3.23 |

- 성명 2개는 taegu ROI로도 맞았다 (`(인)`이 함께 읽히지만 정규화에서 제거됨)
- **보증금·계약금은 실패했다**: taegu ROI가 2~3행에 걸쳐 있어서 `금 금 금 일천만 사천만 원정은…`처럼 다른 행 값이 섞였다 → ROI를 해당 행 높이로 줄여야 실험 C에서 의미 있는 비교가 가능하다
- 소재지는 세 방법 모두 `호`를 놓쳤다(`401`). taegu ROI는 아래 행 인쇄 글자 `(대지권의 목적인`도 섞였다
- 결과: `results/eval/common_sample/summary.md`

### 2-4. H1 — 이미지 품질의 영향 (`results/h1/summary.md`)

> H1: "Text bbox는 한국어 자체보다 이미지 품질의 영향을 더 크게 받는다"

**방법**: 양식에 **인쇄된 한글**(53줄, 1,325자)은 10장 모두 내용이 같다. 그래서 인쇄 글자의 인식률을 장별로 비교하면 글자 내용(한국어)은 고정되고 이미지 품질만 달라진다. 정답은 양식 PDF의 텍스트 레이어에서 가져왔다(`gt/template_words.json`).
- **인쇄 재현율**: 줄 단위로, 정답 한글 중 순서대로 맞게 읽힌 비율(LCS). 같은 줄에 쓴 손글씨는 감점하지 않는다
- **위치 무관 재현율**: 페이지 전체 한글 2글자 묶음 중 OCR 결과에 나온 비율. 정렬 오차의 영향을 받지 않으며, 두 지표가 같은 결론을 내는지 교차 확인하는 용도다
- **품질 지표**: 원근 보정한 문서에서 밝기, 대비, 선명도, 조명 불균일, 유효 해상도, 기울기, 원근비를 측정했다
- **검출 입력 해상도**: 검출 모델이 실제로 보는 해상도. 사진 긴 변을 1536px로 줄이므로, 유효 해상도 × 1536 / 사진 긴 변으로 계산한다

**결과 1 — 품질이 좋으면 인쇄 한글은 거의 다 읽힌다**

| 이미지 (세트) | 검출 입력 dpi | 인쇄 재현율 | 위치 무관 재현율 | 원인 |
|---|---|---|---|---|
| 7장 (#1, #2, #3, #5, #6, #8, #9) | 106~120 | **0.971~0.995** | 0.943~0.944 | — |
| sample_4 (#4) | 110 | 0.903 | 0.904 | 클립보드 가장자리에 걸린 맨 아래 안내문 줄 전체 누락 |
| sample_7 (#7 접힘) | 113 | 0.888 | 0.913 | 접힌 자국 부근(제1조 줄 끝) 누락 |
| sample_10 (#10 멀리서) | **79** | **0.871** | **0.836** | 문서가 작게 찍혀 검출 입력 해상도가 가장 낮음 |

- 같은 한국어 인쇄 글자인데 장에 따라 재현율이 0.87~0.99로 달라진다. 떨어지는 3장은 모두 촬영 상태(거리, 접힘, 가장자리)로 설명된다 → **H1을 지지한다**
- 품질 지표 중 인쇄 재현율과 순위 상관이 뚜렷한 것은 **유효 해상도(ρ=+0.73)**뿐이다. 조명 불균일도 ρ=+0.78로 나왔지만, "불균일할수록 잘 읽힌다"는 방향이라 설명이 안 된다. #4와 #10의 값이 우연히 낮아서 생긴 상관으로 보고 해석하지 않는다(n=10)
- 손글씨 CER과 인쇄 재현율의 상관은 ρ=−0.71이다. 인쇄 글자가 잘 안 읽히는 장은 손글씨도 잘 안 읽힌다. 다만 깨끗한 #1에서도 손글씨 CER이 0.105라서, **손글씨 인식은 이미지 품질과 별개인 병목**이다

**결과 2 — 원본 vs 전처리** (전체 OCR, 10장 평균)

| 입력 | 인쇄 재현율 | 손글씨 Field Accuracy | 손글씨 CER |
|---|---|---|---|
| 원본 | 0.957 | 29/49 | 0.142 |
| CLAHE 대비 보정 | 0.960 | **24/49** ↓ | 0.205 |
| **원근 보정** (문서만 잘라 정면으로 펴기) | **0.975** | **31/49** | **0.119** |

- **원근 보정이 가장 효과가 크다**. #10은 인쇄 재현율이 0.871에서 0.990으로 회복됐다. 문서만 잘라 펴면 같은 1536px 제한 안에서 문서가 더 크게 들어가기 때문이다(검출 입력 79dpi → 131dpi)
- **대비 보정(CLAHE)은 효과가 없거나 오히려 해롭다**. 인쇄 글자는 거의 같고, 손글씨 Field Accuracy는 29에서 24로 떨어졌다
- #4와 #7은 원근 보정으로도 회복되지 않았다(0.907, 0.891). 평면 변환으로 고칠 수 없는 국소 문제(가장자리, 접힘)다
- 주의: 원근 보정에는 GT ROI 생성과 같은 양식 템플릿 정합(호모그래피)을 썼다. 실제 파이프라인에서는 문서 경계 검출 같은 자동 방법이 필요하다. #7은 정합이 부정확해서 원근 보정본의 필드 칸이 일부 어긋난다

### 2-5. 결과 해석 시 주의할 점 (한계)

- **표본이 작다**: 49필드, 10장이다. A와 B의 차이(+2건)는 통계적으로 확실한 차이가 아니라 경향으로 봐야 한다
- **필체가 하나다**: 10장 모두 한 사람이 썼고 인쇄체 기입이 없다(#7도 손글씨). 다른 필체로 일반화할 수 있는지는 확인하지 않았다
- **정답은 tail이 직접 만들었다**:
  - 정답 텍스트는 의도한 값(`fake_contract_data.md`) 기준이다. 필체가 모호한 경우(`권나연`이 `권4연`처럼 보임)도 의도한 값을 정답으로 했다
  - 정답 ROI는 양식 템플릿을 호모그래피로 옮긴 뒤 60개 crop을 전부 육안 검수했다. #7 상단 4칸은 직접 좌표를 지정했다
- **Full OCR 필드 배정은 근사다**: 글자 폭이 일정하다고 가정한다. 인쇄 글자와 손글씨가 섞인 긴 박스에서는 경계 글자가 한두 개 어긋날 수 있다
- **ROI 처리 시간에는 칸 검출 시간이 빠져 있다**: 0.93초/장은 OCR만의 시간이다. 실제 파이프라인 시간은 실험 C에서 검출 시간을 더해야 한다
- **인식 모델은 하나만 썼다**: `korean_PP-OCRv5_mobile_rec` 하나다. 서버 모델은 메모리 문제로 쓰지 못했다. 손글씨 오인식 결론은 이 모델에 한정된다
- **ROI 여유 비율(25%)은 고정값이지만, 결과는 이 값에 거의 영향을 받지 않는다**: 0 / 0.10 / 0.25 / 0.40으로 바꿔 돌려 봐도 EM은 30~31/49였다(아래 표). 같은 10장으로 최적값을 고르면 과적합이 되므로 0.25를 유지한다

  | 여유 비율 | EM | 평균 CER | sec/image |
  |---|---|---|---|
  | 0 | 30/49 | 0.151 | 0.86 |
  | 0.10 | 31/49 | 0.114 | 0.80 |
  | **0.25 (사용)** | **31/49** | **0.117** | 0.93 |
  | 0.40 | 30/49 | 0.150 | 1.04 |

  여유가 0이면 선을 넘은 획이 잘리고, 0.40이면 다음 행 글자가 섞여서 CER이 양쪽 끝에서 나빠진다 (`results/eval/pad_sweep/`)

- **H1 분석도 표본이 작다**: 10장, 양식 1종, 촬영자 1명이다. 상관계수는 방향을 보는 참고 자료이고, 장별 원인은 이미지를 직접 확인해서 붙였다

### 2-6. 개인정보 — 사진 GPS 위치정보

- 촬영 사진 11장과 공통 `sample.jpg`에 **GPS 위치정보(촬영 장소 좌표)가 들어 있었다**. 2026-10-05에 `exiftool -gps:all=`로 **GPS 항목만** 지웠다
  - EXIF 전체를 지우면 회전 정보(Orientation)까지 사라져 사진이 가로로 돌아가고, 정답 좌표가 전부 틀어진다. 그래서 GPS만 지웠다
  - 지우기 전과 후에 디코딩한 픽셀의 해시를 비교해, 12장 모두 **픽셀과 회전이 완전히 같음**을 확인했다 → 정답 좌표와 OCR 결과는 그대로 유효하다
- **이전 커밋(`eaee964`, `1e9bbe2` 등)에는 GPS가 남은 원본이 여전히 있고, GitHub에 push된 상태다.** 완전히 지우려면 git 히스토리를 다시 써서 강제 push해야 하므로 팀 합의가 필요하다
- 이후 사진을 추가할 때는 커밋 전에 `exiftool -gps:all= -overwrite_original <파일>`을 실행할 것

---

## 3. 파일 구조

```text
tail/
├── README.md                  # 이 문서
├── plan.md                    # 담당 배정 문서 (체크박스로 진행 표시)
├── PROGRESS.md                # 작업 진행 요약 (상세 이력은 git 히스토리)
├── requirements.txt           # 실행 의존성 (추가 인원 B 전달용)
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
│   ├── evaluate_fields.py     # 평가: Full vs GT ROI (vs Detected ROI) → results/eval/
│   ├── h1_quality.py          # H1: 품질 지표, 인쇄 글자 평가, 원본/전처리 비교 → results/h1/
│   └── convert_teammate.py    # 팀원(taegu) 결과 → tail 형식 변환 (팀원 폴더는 읽기만)
│
├── gt/
│   ├── template.png           # 양식 PDF를 300dpi로 렌더링한 기준 이미지
│   ├── gt_fields.json         # 정답 텍스트 (이미지 × 필드)
│   ├── gt_roi.json            # 정답 ROI (이미지 × 필드, 4점 quad + bbox, 원본 좌표)
│   ├── template_words.json    # 양식 PDF의 인쇄 단어와 좌표 (H1 인쇄 글자 정답)
│   ├── check/                 # GT ROI 육안 검수용 이미지 10장
│   └── common_sample/         # 공통 sample.jpg 정답 (taegu field_gt.json 변환본)
│
├── results/
│   ├── sample_{1..10}_ocr.json / _vis.png   # 실험 A 결과 (+ 공통 sample.jpg 결과)
│   ├── roi_gt/                # 실험 B 결과 + crops/ (ROI 60개)
│   ├── roi_gt_pad/            # 실험 B 여유 비율 민감도 (0 / 0.1 / 0.4)
│   ├── detected_roi/          # 실험 C 입력 (팀원 ROI 변환본)
│   ├── common_sample/         # 공통 sample.jpg의 실험 B/C 결과
│   ├── h1/                    # H1: quality_metrics.json, printed_*.json, ocr/(전처리 OCR), eval_*/, summary.md
│   │                          #     (images/, homography/ 는 재생성 가능해서 .gitignore)
│   ├── eval/                  # summary.md, field_results.json, 팀원 ROI 좌표 확인 이미지
│   └── cases/                 # 대표 성공·실패 사례 (cases.md + crop 이미지)
│
└── docs/
    └── ocr_io_spec.md         # OCR 모듈 입출력 규격 (ROI 입력 형식, 출력 형식, 정규화 규칙)
```

---

## 4. 실행 방법

환경: conda `tail` (Python 3.11). 패키지 버전은 [`requirements.txt`](requirements.txt)

```bash
conda activate tail

# 실험 A — 전체 페이지 OCR (장당 약 30초)
python scripts/ocr_baseline.py sample_data_jpg/sample_{1..10}.JPG

# GT ROI 생성 (이미 gt/gt_roi.json 있음. 새 이미지를 추가할 때만 실행하고 gt/check/로 반드시 육안 검수)
python scripts/make_gt_roi.py sample_data_jpg/sample_{1..10}.JPG

# 실험 B — GT ROI OCR
python scripts/roi_ocr.py gt/gt_roi.json results/roi_gt

# 실험 C — 검출 ROI OCR (팀원 ROI를 docs/ocr_io_spec.md 1절 형식으로 받은 뒤)
python scripts/roi_ocr.py <detected_roi.json> results/roi_detected --pad 0   # 검출 ROI는 이미 여유가 있으면 --pad 0
# taegu field_mapping_result.json 형식으로 받은 경우 먼저 변환 (팀원 폴더는 읽기만 함)
python scripts/convert_teammate.py taegu-roi ../taegu/<result>.json results/detected_roi/taegu.json

# 평가
python scripts/evaluate_fields.py                                  # A vs B
python scripts/evaluate_fields.py --detected results/roi_detected  # A vs B vs C

# H1 (순서대로, 자세한 옵션은 scripts/h1_quality.py 상단 주석)
python scripts/h1_quality.py prepare sample_data_jpg/sample_{1..10}.JPG
python scripts/ocr_baseline.py results/h1/images/clahe/*.jpg --out-dir results/h1/ocr/clahe --no-vis
python scripts/ocr_baseline.py results/h1/images/rectified/*.jpg --out-dir results/h1/ocr/rectified --no-vis
python scripts/h1_quality.py printed results original photo
python scripts/h1_quality.py printed results/h1/ocr/clahe clahe photo
python scripts/h1_quality.py printed results/h1/ocr/rectified rectified template
python scripts/evaluate_fields.py --full-dir results/h1/ocr/clahe --roi-gt-dir results/h1/none --out-dir results/h1/eval_clahe
python scripts/evaluate_fields.py --full-dir results/h1/ocr/rectified --gt-roi results/h1/gt_roi_rectified.json --roi-gt-dir results/h1/none --out-dir results/h1/eval_rectified
python scripts/h1_quality.py report
```

결과 json의 `meta`에 모델명, 버전, 실행 환경(CPU/GPU), 최대 메모리가 기록된다. 이 환경에서는 CPU이고 최대 메모리는 약 1.9GB다.

주의:
- OCR 모델은 `PP-OCRv5_mobile_det` + `korean_PP-OCRv5_mobile_rec`로 고정했다. 기본값(서버 모델)은 16GB RAM에서 OOM이 난다. 자세한 내용은 PROGRESS.md 09-23 참고
- 모든 좌표는 **EXIF 회전을 적용한 원본 이미지 기준**이다 (3024×4032 세로)

---

## 5. 팀원 요청사항

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

---

## 6. 남은 작업 (tail)

- [x] 실험 C 파이프라인 연결 확인 (sample.jpg 1장, taegu ROI)
- [ ] 실험 C 10장 실행 및 A/B/C 비교표 (팀원 ROI 수신 후 바로 가능)
- [x] H1 1차 분석 (인쇄 글자 비교, 원본/전처리 비교)
- [ ] 촬영 조건 매핑 확인 → H1 표에 계획 조건 열 추가
- [ ] 이전 커밋에 남은 GPS 원본 사진 처리 결정 (2-6절)
- [x] ROI 여유 비율 민감도 확인 (결과에 거의 영향 없음)
- [ ] (선택) ROI 후처리: crop 가장자리에 걸친 작은 박스 제거
- [ ] (선택) 잔금 / 계약기간 필드 추가
- [ ] 결과 시각화 PNG 용량 정리 (장당 약 18MB) 후 커밋
