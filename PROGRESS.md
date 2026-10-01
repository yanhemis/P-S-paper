# tail 작업 진행 기록

> 관련 배정 문서: [plan.md](plan.md) (= `issue/assignment_member_A_ocr_roi_field_accuracy.md`)

---

## 2026-09-23 — 09/25 조기 체크 준비

### 목표

`plan.md` 2절의 09/25 조기 체크 4개 항목 대응:

- [x] 전체 페이지 Korean OCR baseline 실행 성공
- [x] OCR 결과 JSON 저장
- [x] text bbox / text / confidence / runtime 저장
- [x] 최소 1장 이상 결과 시각화 또는 확인 가능한 출력 생성

### 1. 환경 구성

- `tail` 전용 conda 환경 신설 (Python 3.11)
- 설치 패키지: `paddlepaddle 3.3.1`, `paddleocr 3.7.0`, `opencv-python 4.10.0`
- 참고: `dahye_cell_DetectionSurvey` 팀원이 이미 `paddlepaddle==2.6.2` + `paddleocr==2.8.1` (CPU, PaddleOCR 2.x API)로 한국어 OCR을 검증한 이력이 있었음. 이번엔 최신 `paddleocr 3.x`로 설치됨 — API가 달라졌음 (`PaddleOCR.predict()` 기반, `rec_texts` / `rec_scores` / `rec_polys` 반환 구조).

### 2. 실험 A 스크립트

`tail/scripts/ocr_baseline.py`

- 입력: 이미지 경로(들)
- 처리: `PaddleOCR(lang="korean", ...)` 로 전체 페이지 OCR 실행
- 출력 (각 이미지당):
  - `results/<image_stem>_ocr.json` — `image_id`, `runtime_sec`, `num_text_boxes`, `items[].{text, confidence, bbox}`
  - `results/<image_stem>_vis.png` — bbox를 원본 이미지 위에 시각화

### 3. 트러블슈팅 — OOM (exit 137)

- 최초 실행 시 스마트폰 원본 해상도(4000×3000) 이미지에 대해 `lang="korean"` 기본값이 무거운 서버 검출 모델(`PP-OCRv5_server_det`)을 선택 → `peak memory footprint 54GB`까지 치솟으며 16GB RAM 환경에서 OOM으로 프로세스가 죽음 (`exit code 137`).
- 조치: 검출/인식 모델을 명시적으로 가벼운 모델로 고정
  - `text_detection_model_name="PP-OCRv5_mobile_det"`
  - `text_recognition_model_name="korean_PP-OCRv5_mobile_rec"`
  - `text_det_limit_side_len=1536`, `text_det_limit_type="max"`
- 주의: 검출/인식 모델명을 명시하면 `lang` 파라미터가 완전히 무시되므로, 인식 모델도 반드시 한국어 모델로 같이 지정해야 함 (처음엔 인식 모델만 기본값으로 남아 한자/깨진 문자가 나오는 문제가 있었음 — 반드시 두 모델 다 지정할 것).
- 결과: peak memory ~1.5GB, 런타임 약 30초/장으로 안정화.

### 4. 스모크 테스트 결과

- 테스트 이미지: `dahye_cell_DetectionSurvey/sample.jpg` (실제 임대차계약서 사진, tail 자체 데이터는 아직 없어 임시로 사용)
- 결과: 156개 text box 검출, runtime 30.8초
- 육안 확인: "부동산임대차계약서", "소재지", 주소, 보증금·계약금·성명 등 우선 평가 5개 필드 영역이 모두 정확히 bbox로 잡히고 한글 인식도 정상 (예: `서울특별시 강남구 테헤란로 123,4층 401`)

### 5. 남은 작업 (다음 단계)

- [ ] tail 자체 계약서 이미지 확보 (최종 마감 기준 최소 10장, 동일/유사 양식)
- [ ] 5개 우선 필드(소재지/보증금/계약금/임대인 성명/임차인 성명)에 대한 GT(정답 crop + 정답 텍스트) 준비 → 실험 B용
- [ ] 실험 B: GT ROI OCR
- [ ] 실험 C: `bang_`/`heewon`의 Cell/ROI 결과 수신 후 적용
- [ ] CER / Exact Match / confidence / Field Accuracy 비교표 작성
- [ ] git commit (현재 `tail` 브랜치에 미커밋 상태 — conda 환경/스크립트/결과물 정리 후 커밋 예정)

---

## 2026-10-02 — 자체 계약서 데이터 3장 추가

### 1. 데이터 준비 문서

- `contractForm/shooting_conditions.md` — 10장 촬영 조건 조합표 (조명/각도/그림자/블러/문서 상태/거리), H1 검증용으로 조건을 의도적으로 분산
- `sample_data_jpg/fake_contract_data.md` — 세트 #1~#10 가짜 기입 데이터 (= GT 원본). 대상 양식: `contractForm/**부동산임대차계약서_양식.pdf`
- `contractForm/` — 법무부 주택임대차 표준계약서(hwp/pdf), 부동산 양식, 두 양식 비교 문서 추가
- `question.md` — 전세/월세 차이, 양식 간 일반화, 여러 장 촬영 대응, 데이터 규모 관련 질문 정리

### 2. 추가된 이미지 (`sample_data_jpg/`, 2026-09-30 촬영, 4032×3024)

| 파일 | 세트 | 유형 | 촬영 조건 (계획) | 비고 |
|---|---|---|---|---|
| `sample_empty.JPG` | — | 빈 양식 | — | 기입 전 양식 (템플릿 / ROI 기준용) |
| `sample_1.JPG` | #1 | 전세 | 베이스라인 (정면·선명·평평) | 손글씨 |
| `sample_2.JPG` | #2 | 월세 | 실내 형광등 | 손글씨, 추가 특약 "반려동물 사육 금지" |
| `sample_3.JPG` | #3 | 전세 | 저조도 | 손글씨, 임대인 대리인 기입, 약간 기울어짐 |

- 진행률: 계획한 10장 중 3장 (#1~#3)
- 육안 확인 결과 3장 모두 우선 평가 5개 필드(소재지/보증금/계약금/임대인 성명/임차인 성명)가 프레임 안에 들어와 있고 가려진 부분 없음

### 3. GT와 실제 기입값 차이 (GT 작성 시 반영 필요)

- **#3 중도금 / 잔금 지급일**: GT는 `2026년 11월 10일` / `2026년 12월 15일`인데 실제로는 `2026년 12월 10일` / `2027년 1월 15일`로 기입됨 → 우선 5개 필드는 아니지만, GT는 **이미지에 실제로 쓰인 값** 기준으로 맞춰야 함
- **빈 칸 표기 방식이 기입 규칙과 다름** (규칙: 빗금 `/`)
  - #1: 중도금·차임 칸에 `없음`이라고 씀
  - #2: 중도금 칸을 검게 지움
  - #3: 차임 칸을 비워 둠
  - → 빈 필드 GT를 어떻게 정의할지(빈 문자열 / `없음`) 정해야 함

### 4. 남은 작업

- [x] tail 자체 계약서 이미지 확보 — 3/10장 완료
- [ ] 나머지 7장 촬영 (#4~#10, `shooting_conditions.md` 기준)
- [x] 3장에 대해 실험 A(`scripts/ocr_baseline.py`) 실행 → `results/`에 저장 (아래 5절)
- [ ] 5개 우선 필드 GT(정답 crop + 정답 텍스트) 작성 — 위 3절 차이 반영
- [ ] 실험 B: GT ROI OCR
- [ ] 실험 C: `bang_`/`heewon`의 Cell/ROI 결과 수신 후 적용
- [ ] CER / Exact Match / confidence / Field Accuracy 비교표 작성
- [ ] 공유 전 이미지 EXIF(GPS) 제거

### 5. 실험 A (Full OCR) — 3장 결과

`scripts/ocr_baseline.py` 그대로 실행 (mobile det/rec, `text_det_limit_side_len=1536`). EXIF 회전이 적용되어 bbox는 세로(3024×4032) 좌표 기준.

| 이미지 | 세트 | text box 수 | 평균 confidence | conf < 0.8 박스 | runtime |
|---|---|---|---|---|---|
| `sample_1` | #1 베이스라인 | 169 | 0.922 | 22 | 31.9s |
| `sample_2` | #2 형광등 | 157 | 0.944 | 10 | 30.9s |
| `sample_3` | #3 저조도 | 165 | 0.937 | 16 | 30.8s |

산출물: `results/sample_{1,2,3}_ocr.json`, `results/sample_{1,2,3}_vis.png`

**우선 평가 5개 필드 — 육안 대조 (CER 계산 전, 1차 확인)**

| 필드 | #1 | #2 | #3 |
|---|---|---|---|
| 소재지 | △ `시을특별시 마구 월드컵로 45길 12. 3013` | △ `서열 독별시 관악구 관악로 210 지하102` | △ `경기도 성남시 분당? 핀교3 256번 33 1204통 803` (박스 여러 개로 쪼개짐) |
| 보증금 (한글 / 숫자) | ○ `일억팔천만` / △ `180,000.` + `OㅇO` (박스 분리) | ○ `일천만` / ○ `10,000,000` | ✕ `이억 3천만` / ○ `250,000,000` |
| 계약금 | ○ `일천팔백만` | ○ `일백만` | ✕ `이전소백만` (정답 이천오백만) |
| 임대인 성명 | ○ `박정훈` | ○ `정미경` | ○ `강태식` |
| 임차인 성명 | ○ `이서연` | ○ `오준혁` | ○ `신유진` |

(○ 정확 / △ 일부 오인식 / ✕ 핵심 값 틀림)

**관찰**

- 성명 필드는 3장 모두 정확. 소재지는 3장 모두 일부 글자 오인식(`서울`→`시을`/`서열`, `구`→`?`/`3`, `호`→`3`) → 주소처럼 긴 손글씨 필드가 가장 약함
- 손글씨 `오`가 반복적으로 틀림: `오천`→`3천`, `오백`→`소백`/`9백`, `구백만`→`2백만` → 금액 필드 오류의 주원인
- 숫자/영문 혼동: `5`↔`S`, `1`↔`l`, `0`↔`o`/`O` (전화번호·주민번호에서 다수)
- 같은 줄의 값이 여러 박스로 쪼개지거나 행 경계를 넘어 합쳐짐 (예: #1 숫자 금액, #3 당사자 칸 `주 소 경기도 성남시…`) → 필드 단위 매칭에는 ROI가 필요하다는 근거 (실험 B/C)
- 저조도(#3)의 평균 confidence는 베이스라인(#1)보다 낮지 않음. 다만 표본이 1장씩이라 H1 판단은 10장을 모두 확보한 뒤에 할 것
