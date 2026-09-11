# P-S-paper — issue branch

이 브랜치는 공동연구 과정에서 나온 **공통 연구 방향, 전체 진행 현황, 담당자별 피드백, 추가 인원 작업 배정**을 분리해서 관리한다.

> 마지막 업데이트: 2026-09-11

## 문서 구성

### `01_research_direction_and_next_steps.md`

팀 전체 공통 문서.

정리하는 내용:
- 현재 연구 방향
- 연구 가설 H1~H6
- Text Detection / Structure / Field Extraction 구분
- 최신 실험에서 확인된 핵심 사항
- 우선 비교 파이프라인
- Ground Truth 기준
- 공통 평가 지표
- 다음 작업 우선순위
- 전체 역할 분담
- 현재 연구 진행 현황

**공통 연구 방향과 해볼 것들은 이 파일 한 곳에 계속 이어서 업데이트한다.**

담당자 개인 피드백은 넣지 않는다.

---

## 담당자별 피드백

### `feedback_dahye_cell_detection_survey.md`

대상: `dahye_cell_DetectionSurvey`

정리하는 내용:
- 구조 모델 조사 및 비교 피드백
- TATR reconstruction
- PP-Structure / PP-StructureV3 구분
- GT 및 evaluator 코드 피드백
- IoU threshold / 1:1 matching / Precision-Recall 보완 사항

OpenCV 구현 세부 내용은 넣지 않는다.

---

### `feedback_bang_opencv_roi.md`

대상: `bang_`

정리하는 내용:
- OpenCV Grid / Cell / ROI 프로토타입 피드백
- 병합 셀 후보 탐지와 실제 merged bbox 재구성 차이
- 경계선 기반 병합 로직
- morphology kernel 및 고정 파라미터 점검
- 최종 ROI 생성 관련 확인 사항

범용 구조 모델 조사나 OCR 성능 비교는 넣지 않는다.

---

### `feedback_heewon_opencv_method_comparison.md`

대상: `heewon`

정리하는 내용:
- Morphological Opening vs Contour 방식 비교
- kernel / filter parameter sensitivity
- bbox 수가 아닌 GT 기반 Precision / Recall / F1 비교
- 모든 셀이 merged 후보로 판정되는 현상 원인 확인
- 두 OpenCV 방식의 실패 유형 분류

`bang_`의 최종 병합 셀 재구성 알고리즘과 겹치지 않게 관리한다.

---

## 추가 인원 작업 배정

담당자 이름이 정해지면 파일명은 변경해도 되지만, 역할 경계는 유지한다.

### `assignment_member_A_ocr_roi_field_accuracy.md`

추가 인원 A.

담당:
- PaddleOCR 전체 페이지 baseline
- GT ROI OCR
- 실제 검출 ROI OCR
- CER / Exact Match / confidence
- Field Accuracy
- 전체 OCR vs ROI OCR 비교

**셀 검출 알고리즘 자체는 수정하지 않는다.**

---

### `assignment_member_B_anchor_roi_field_mapping.md`

추가 인원 B.

담당:
- 핵심 라벨 Anchor 탐색
- 상대 위치 기반 ROI 생성
- label-to-value mapping
- ROI Coverage Rate
- Field Exact Match / Accuracy
- Cell 기반 방식과 Anchor 기반 방식 비교

**Table Structure / Cell Detection 모델 개발은 하지 않는다.**

---

## 현재 역할 분담

| 구분 | 핵심 역할 |
|---|---|
| `dahye_cell_DetectionSurvey` | 구조 모델 + TATR/PP-Structure + evaluator 기초 |
| `bang_` | OpenCV grid + merged cell bbox 재구성 |
| `heewon` | Morphology vs Contour 비교 |
| 추가 인원 A | OCR / ROI 재인식 / Field Accuracy |
| 추가 인원 B | Anchor-ROI / Field Mapping |

---

## 현재 연구 현황 — 2026-09-11

### 완료/진행

- [x] 범용 Table Structure 모델 예비 조사
- [x] OpenCV line/cell detection 1차 프로토타입
- [x] Morphological / Contour 비교 실험 시작
- [x] GT 라벨링 도구 초안
- [x] IoU evaluator 초안
- [x] TATR cell bbox 재구성 1차 구현
- [x] 연구 가설 H1~H6 정리
- [x] 추가 인원 2명 역할 분배

### 가장 먼저 수정할 것

- [ ] evaluator `iou_threshold=0.01`과 출력 `0.5` 불일치 수정
- [ ] GT-Pred 1:1 matching + Precision / Recall / F1
- [ ] GT 중복 좌표 검수 및 샘플 확대
- [ ] TATR spanning-cell 실제 reconstruction 반영
- [ ] PP-Structure 2.x / PP-StructureV3 명칭과 실험 분리
- [ ] OpenCV merged 판정 로직 검증

### 그 다음 핵심 실험

- [ ] TATR / PP-Structure / Morphology / Contour 동일 GT 비교
- [ ] Full OCR vs GT ROI OCR vs Detected ROI OCR 비교
- [ ] Anchor-ROI PoC
- [ ] 최종 Field Accuracy 비교

---

## 관리 원칙

1. **연구 방향·가설·공통 실험 계획·전체 현황은 `01_research_direction_and_next_steps.md` 한 곳에서만 계속 업데이트한다.**
2. **담당자 피드백은 담당자별 `feedback_*.md` 파일에만 기록한다.**
3. **추가 인력에게 나눈 작업은 `assignment_*.md`에 역할별로 기록한다.**
4. 다른 담당자와 공통되는 연구 아이디어는 피드백 파일에 반복하지 않고 공통 문서로 이동한다.
5. 새 실험 결과가 나오면 먼저 공통 연구 문서의 `추가 실험에서 확인된 내용`과 `현재 현황`을 업데이트한다.
6. 피드백 파일에는 해당 브랜치에서 실제로 수정하거나 확인할 항목만 남긴다.
7. 역할이 겹치기 시작하면 `Cell Detection`, `Structure Reconstruction`, `OCR Re-recognition`, `Field Mapping` 중 어느 단계인지 기준으로 다시 분리한다.
