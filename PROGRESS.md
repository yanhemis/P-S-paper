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
