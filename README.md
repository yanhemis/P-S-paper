# P-S-paper — issue branch

이 브랜치는 공동연구 과정에서 나온 **공통 연구 방향, 전체 진행 현황, 담당자별 피드백, 담당자별 작업 배정**을 분리해서 관리한다.

> 마지막 업데이트: 2026-09-22

## 전체 일정

- 작업 배분일: **2026-09-22**
- 선행 작업 1차 산출물: **2026-09-30**
- 담당 간 결과 전달 / 통합 시작: **2026-10-04**
- 정량 실험 및 기능 동결: **2026-10-07**
- 서버 End-to-End 확인: **2026-10-10**
- 최종 검토: **2026-10-12**
- 프로젝트 최종 완료: **2026-10-13**

> 2026-10-07 이후에는 신규 모델/기능 추가를 중단하고, 버그 수정·재현성·결과 정리만 진행한다.

---

## 공통 문서

### `00_scope_guard_prompt.md`
연구 범위 이탈 방지 기준.

### `01_research_direction_and_next_steps.md`
연구 방향, 가설 H1~H6, 공통 평가 기준, 다음 작업, 전체 연구 현황을 관리한다.

---

## 담당자별 작업 배정

| 담당 | 배정 문서 | 1차/조기 체크 | 최종 담당 결과 마감 | 핵심 역할 |
|---|---|---|---|---|
| `bang_` | `assignment_bang_opencv_cell_roi.md` | 09/30 | 10/04 | OpenCV Cell/ROI + merged reconstruction |
| `dahye_cell_DetectionSurvey` | `assignment_dahye_structure_evaluation.md` | 09/30 | 10/05 | 구조 모델 비교 + 공통 evaluator |
| `heewon` | `assignment_heewon_opencv_method_comparison.md` | 09/30 | 10/04 | Morphology vs Contour + Pipeline 현행화 |
| `taegu` | `assignment_taegu_anchor_roi_field_mapping.md` | 10/02 | 10/06 | Anchor-ROI / Field Mapping |
| `tail` | `assignment_member_A_ocr_roi_field_accuracy.md` | 09/25 | 10/07 | Full OCR vs ROI 재인식 |
| 추가 인원 B | `assignment_member_B_anchor_roi_field_mapping.md` | 09/25 | 10/10 | 서버 의존성 / End-to-End 통합 |

---

## 담당자별 피드백

### `feedback_dahye_cell_detection_survey.md`
- 구조 모델 비교
- TATR reconstruction
- PP-Structure 계열
- Ground Truth / evaluator
- IoU / 1:1 matching / Precision-Recall-F1

### `feedback_bang_opencv_roi.md`
- OpenCV grid / Cell / ROI
- merged cell reconstruction
- over-merge / under-merge
- irregular component 검증

### `feedback_heewon_opencv_method_comparison.md`
- Morphological Opening vs Contour
- kernel / filter sensitivity
- 동일 GT 비교

---

## 역할 간 전달 관계

```text
bang_ ───────────────┐
                     ├─> Cell/ROI 결과 ──> 추가 인원 A (ROI OCR)
heewon ──────────────┘

Dahye ──> 공통 evaluator / 구조 모델 결과

전체 OCR ──> taegu ──> Anchor-ROI / Field Mapping

각 담당 결과 ──> 추가 인원 B ──> 서버 / End-to-End 통합
```

---

## 현재 역할 분담 원칙

1. 기존에 진행한 작업의 연장선에서 마무리한다.
2. 다른 담당자의 영역을 다시 구현하지 않고 결과 파일을 받아 연결한다.
3. 새로운 Cell Detection 딥러닝 모델은 추가하지 않는다.
4. 동일 데이터와 가능한 한 동일 Ground Truth를 사용한다.
5. 단순 bbox 개수를 성능으로 해석하지 않는다.
6. 실행하지 못한 모델은 성능 열세가 아니라 `현재 환경에서 평가하지 못함`으로 기록한다.
7. 성공 사례뿐 아니라 실패 사례와 실행 조건도 함께 남긴다.
8. 10월 7일 이후에는 기능 확장보다 통합과 결과 확정이 우선이다.

---

## 최종적으로 맞춰야 할 비교축

1. Full OCR baseline
2. 구조 모델 기반 Cell/ROI
3. OpenCV 기반 Cell/ROI
4. ROI 재인식
5. Anchor-ROI Field Mapping
6. 최종 Field Accuracy
7. 서버에서 재현 가능한 End-to-End 실행

---

## 관리 원칙

1. 연구 방향·가설·공통 실험 계획은 `01_research_direction_and_next_steps.md`에서 관리한다.
2. 개인 피드백은 `feedback_*.md`에 기록한다.
3. 개인 작업과 마감은 `assignment_*.md`에 기록한다.
4. 공통 아이디어를 개인 피드백 문서에 반복하지 않는다.
5. 범위를 벗어나는 아이디어는 Future Work로 남긴다.
6. 일정이 밀릴 경우 실험축을 추가하지 않고 현재 비교축 완성을 우선한다.
