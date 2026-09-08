# P-S-paper — issue branch

이 브랜치는 공동연구 과정에서 나온 **연구 방향 정리, 공통 다음 작업, 담당자별 피드백**을 분리해서 관리한다.

## 문서 구성

### `01_research_direction_and_next_steps.md`

팀 전체 공통 문서.

정리하는 내용:
- 현재 연구 방향
- 연구 가설 H1~H6
- Text Detection / Table Structure / Field Mapping 구분
- 우선 비교 파이프라인
- Ground Truth 기준
- 공통 평가 지표
- 다음 작업 우선순위
- 현재 연구 진행 현황

**담당자 개인 피드백은 이 파일에 적지 않는다.**

---

### `feedback_dahye_cell_detection_survey.md`

대상: `dahye_cell_DetectionSurvey` 브랜치

정리하는 내용:
- 범용 Table Structure 모델 조사에 대한 피드백
- 실행 실패와 성능 실패 구분
- TATR cell reconstruction 해석 수정
- 최신 PP-StructureV3 재검증 필요 항목
- 모델 비교 README 개선 사항

OpenCV 구현 세부 피드백은 이 파일에 적지 않는다.

---

### `feedback_bang_opencv_roi.md`

대상: `bang_` 브랜치

정리하는 내용:
- OpenCV Cell/ROI Detection 프로토타입 피드백
- 병합 셀 후보 탐지와 실제 merged bbox 재구성 차이
- morphology kernel 및 고정 파라미터 점검
- `close_gaps()` 수평/수직 길이 기준 점검
- Ground Truth 기반 정량 평가 필요 사항

범용 구조 모델 조사 피드백은 이 파일에 적지 않는다.

---

## 현재 연구 현황 — 2026-09-08

### 완료/진행

- [x] 범용 Table Structure 모델 예비 조사
- [x] TATR / PP-Structure 계열의 재검증 필요 지점 정리
- [x] OpenCV line/cell detection 1차 프로토타입 구현
- [x] 연구 가설 H1~H6 정리
- [x] 공통 비교 파이프라인 후보 선정

### 다음 핵심 작업

- [ ] 공통 Ground Truth 데이터셋 구성
- [ ] PaddleOCR Text bbox baseline 측정
- [ ] PP-StructureV3 최신 조합 재실험
- [ ] TATR cell reconstruction 정량 평가
- [ ] OpenCV merged cell bbox 재구성
- [ ] 동일 문서에서 Cell IoU 비교
- [ ] ROI OCR 전/후 Field Accuracy 비교
- [ ] 필요 시 Anchor-ROI PoC

## 관리 원칙

1. **연구 방향·가설·공통 실험 계획은 `01_research_direction_and_next_steps.md` 한 곳에서만 관리한다.**
2. **담당자 피드백은 담당자별 `feedback_*.md` 파일에만 기록한다.**
3. 다른 담당자와 공통되는 연구 아이디어는 피드백 파일에 반복하지 않고 공통 문서로 이동한다.
4. 새로운 실험 결과가 나오면 먼저 공통 연구 문서의 `현재 현황`과 관련 가설을 업데이트한다.
5. 피드백 파일에는 해당 브랜치에서 실제로 수정하거나 확인할 항목만 남긴다.
