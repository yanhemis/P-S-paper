# P-S-paper — issue branch

이 브랜치는 공동연구 과정에서 나온 **공통 연구 방향, 전체 진행 현황, 담당자별 피드백, 추가 인원 작업 배정**을 분리해서 관리한다.

> 마지막 업데이트: 2026-09-11

## 문서 구성

### `00_scope_guard_prompt.md`

팀 전체 공통 **연구 범위 이탈 방지 프롬프트**.

사용 시점:
- 새로운 기능을 만들기 전
- 새로운 모델을 조사/추가하기 전
- 새로운 담당 작업을 배정하기 전
- 기존 실험을 예상보다 크게 확장하기 전
- 논문 기여와 직접 관계가 있는지 애매할 때

이 프롬프트는 작업을 `IN_SCOPE / ADJACENT / OUT_OF_SCOPE`로 먼저 분류하고, H1~H6 가설·평가 지표·최종 Field Accuracy와 연결되는지 확인하도록 한다.

**새 작업은 가능하면 이 문서의 범위 판정을 먼저 거친다.** 범위를 벗어난 아이디어는 바로 구현하지 않고 Future Work 후보로만 남긴다.

---

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

현재 단계:
- OpenCV Grid / Cell Detection 1차 프로토타입 완료
- 병합 셀 후보 탐지까지 구현

**다음 확정 작업:**

```text
primitive grid
  -> shared boundary 판정
  -> 인접 primitive cell 연결
  -> Union-Find / connected component 기반 병합
  -> General / Merged Cell bbox 생성
  -> 표준 cells.json 출력
  -> 공통 evaluator에 prediction 전달
```

정리하는 내용:
- 병합 셀 후보 탐지와 실제 merged bbox 재구성 차이
- 경계선 기반 병합 로직
- primitive grid → merged cell 구조 복원
- 병합 전/후 bbox 시각화
- 표준 `cells.json` 출력
- 오병합 / 미병합 실패 사례

**Morphology vs Contour 방식 선택은 `heewon`, OCR/Field Accuracy는 추가 인원 A가 담당하므로 `bang_`에서는 수행하지 않는다.**

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

| 구분 | 핵심 역할 | 다음 산출물 |
|---|---|---|
| `dahye_cell_DetectionSurvey` | 구조 모델 + TATR/PP-Structure + evaluator 기초 | 신뢰 가능한 공통 evaluator / 구조모델 prediction |
| `bang_` | OpenCV grid → merged cell 구조 복원 | General/Merged bbox + `cells.json` |
| `heewon` | Morphology vs Contour 비교 | 동일 GT 기반 방식별 성능 비교 |
| 추가 인원 A | OCR / ROI 재인식 / Field Accuracy | Full vs GT ROI vs Detected ROI OCR 결과 |
| 추가 인원 B | Anchor-ROI / Field Mapping | Anchor 기반 핵심 필드 추출 결과 |

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
- [x] 연구 범위 이탈 방지 프롬프트 추가
- [x] `bang_` 다음 단계: Merged Cell Reconstruction으로 역할 확정

### 가장 먼저 수정할 것

- [ ] evaluator `iou_threshold=0.01`과 출력 `0.5` 불일치 수정
- [ ] GT-Pred 1:1 matching + Precision / Recall / F1
- [ ] GT 중복 좌표 검수 및 샘플 확대
- [ ] TATR spanning-cell 실제 reconstruction 반영
- [ ] PP-Structure 2.x / PP-StructureV3 명칭과 실험 분리
- [ ] OpenCV merged 판정 로직 검증

### `bang_` 다음 작업 완료 조건

- [ ] primitive cell 기반 실제 merged bbox 생성
- [ ] 2열 / 2행 / 다중 행·열 병합 처리
- [ ] General / Merged bbox 구분
- [ ] 병합 전 / boundary 판정 / 병합 후 시각화
- [ ] 표준 `cells.json` 출력
- [ ] 공통 GT 샘플 prediction 생성
- [ ] 오병합 / 미병합 사례 최소 3종 기록

### 그 다음 핵심 실험

- [ ] TATR / PP-Structure / Morphology / Contour / OpenCV merged reconstruction 동일 GT 비교
- [ ] Full OCR vs GT ROI OCR vs Detected ROI OCR 비교
- [ ] Anchor-ROI PoC
- [ ] 최종 Field Accuracy 비교

---

## 관리 원칙

1. **새 작업·새 모델·새 기능을 추가하기 전에 `00_scope_guard_prompt.md`로 연구/논문 범위와 연결되는지 먼저 확인한다.**
2. **연구 방향·가설·공통 실험 계획·전체 현황은 `01_research_direction_and_next_steps.md` 한 곳에서만 계속 업데이트한다.**
3. **담당자 피드백은 담당자별 `feedback_*.md` 파일에만 기록한다.**
4. **추가 인력에게 나눈 작업은 `assignment_*.md`에 역할별로 기록한다.**
5. 다른 담당자와 공통되는 연구 아이디어는 피드백 파일에 반복하지 않고 공통 문서로 이동한다.
6. 새 실험 결과가 나오면 먼저 공통 연구 문서의 `추가 실험에서 확인된 내용`과 `현재 현황`을 업데이트한다.
7. 피드백 파일에는 해당 브랜치에서 실제로 수정하거나 확인할 항목만 남긴다.
8. 역할이 겹치기 시작하면 `Cell Detection`, `Structure Reconstruction`, `OCR Re-recognition`, `Field Mapping` 중 어느 단계인지 기준으로 다시 분리한다.
9. 범위를 벗어나지만 흥미로운 아이디어는 즉시 구현하지 않고 `Future Work` 후보로만 기록한다.
