# P-S-paper — issue branch

이 브랜치는 공동연구 과정에서 나온 **공통 연구 방향, 전체 진행 현황, 담당자별 피드백, 추가 인원 작업 배정**을 분리해서 관리한다.

> 마지막 업데이트: 2026-09-14

## 문서 구성

### `00_scope_guard_prompt.md`

팀 전체 공통 **연구 범위 이탈 방지 프롬프트**.

사용 시점:
- 새로운 기능을 만들기 전
- 새로운 모델을 조사/추가하기 전
- 새로운 담당 작업을 배정하기 전
- 기존 실험을 예상보다 크게 확장하기 전
- 논문 기여와 직접 관계가 있는지 애매할 때

작업을 `IN_SCOPE / ADJACENT / OUT_OF_SCOPE`로 분류하고, H1~H6·평가 지표·최종 Field Accuracy와 연결되는지 확인한다.

현재는 **Object Detection / Instance Segmentation 기반 Cell Detector 학습을 Future Work로 명시적으로 제외**했다.

---

### `01_research_direction_and_next_steps.md`

팀 전체 공통 문서.

정리하는 내용:
- 현재 연구 방향
- 연구 가설 H1~H6
- Text Detection / Structure / Field Extraction 구분
- 최신 실험에서 확인된 내용
- 현재 논문 범위 / Future Work 경계
- Ground Truth 기준
- 공통 평가 지표
- 다음 작업 우선순위
- 역할 분담
- 전체 연구 현황

**공통 연구 방향과 해볼 것들은 이 파일 한 곳에 계속 이어서 업데이트한다.**

---

## 담당자별 피드백

### `feedback_dahye_cell_detection_survey.md`

대상: `dahye_cell_DetectionSurvey`

담당/피드백 범위:
- 구조 모델 비교
- TATR reconstruction
- PP-Structure / PP-StructureV3 구분
- Ground Truth / evaluator
- IoU / 1:1 matching / Precision-Recall-F1

현재 주요 확인점:
- 1:1 Greedy Matching과 0.3/0.5/0.7 IoU threshold는 구현됨
- TATR spanning-cell reconstruction도 구현됨
- 다만 현재 GT가 일부 셀만 라벨된 partial GT라면 모든 unmatched prediction을 FP로 계산하는 방식은 Precision을 왜곡할 수 있음
- 대표 페이지 exhaustive GT 구축이 우선

---

### `feedback_bang_opencv_roi.md`

대상: `bang_`

현재 단계:

```text
primitive grid
  -> shared boundary 판정
  -> Union-Find 기반 병합
  -> General / Merged Cell bbox
  -> cells.json
```

까지 1차 구현되었다.

이제 해야 할 일:
- 실제 `cells.json` 결과 생성/보관
- primitive / boundary / final bbox 시각화
- h/v kernel 0.4에 의한 짧은 경계 누락 확인
- over-merge / under-merge 검증
- irregular component(rectangularity) 검사
- exhaustive GT 기반 공통 evaluator 연결

**새로운 이미지 딥러닝 Cell Detector는 구현하지 않고 Future Work로 미룬다.**

---

### `feedback_heewon_opencv_method_comparison.md`

대상: `heewon`

담당:
- Morphological Opening vs Contour 비교
- kernel / filter parameter sensitivity
- GT 기반 성능 비교
- OpenCV 방식별 실패 유형 분류

`bang_`의 최종 병합 셀 reconstruction과 역할을 분리한다.

---

## 추가 인원 작업 배정

### `assignment_member_A_ocr_roi_field_accuracy.md`

담당:
- PaddleOCR 전체 페이지 baseline
- GT ROI OCR
- 실제 검출 ROI OCR
- CER / Exact Match / confidence
- Field Accuracy

**Cell Detection 알고리즘 자체는 수정하지 않는다.**

### `assignment_member_B_anchor_roi_field_mapping.md`

담당:
- 핵심 라벨 Anchor 탐색
- 상대 위치 기반 ROI 생성
- label-to-value mapping
- ROI Coverage Rate
- Field Exact Match / Accuracy

**Table Structure / Cell Detection 모델 개발은 하지 않는다.**

---

## 현재 역할 분담

| 구분 | 핵심 역할 | 다음 산출물 |
|---|---|---|
| `dahye_cell_DetectionSurvey` | 구조 모델 + evaluator | exhaustive GT에서 비교 가능한 구조모델 prediction/metrics |
| `bang_` | OpenCV grid → merged cell reconstruction | 실제 `cells.json` + 시각화 + 공통 평가 입력 |
| `heewon` | Morphology vs Contour 비교 | 동일 GT 기반 방식별 성능 비교 |
| 추가 인원 A | OCR / ROI 재인식 | Full vs GT ROI vs Detected ROI OCR 결과 |
| 추가 인원 B | Anchor-ROI / Field Mapping | Anchor 기반 핵심 필드 추출 결과 |

---

## 현재 연구 현황 — 2026-09-14

### 완료/진행

- [x] 범용 Table Structure 모델 예비 조사
- [x] OpenCV line/cell detection 1차 프로토타입
- [x] Morphological / Contour 비교 실험 시작
- [x] GT 라벨링 도구 구현
- [x] 1:1 Greedy Matching evaluator 1차 구현
- [x] TATR spanning-cell reconstruction 1차 구현
- [x] `bang_` Union-Find merged reconstruction 1차 구현
- [x] 연구 가설 H1~H6 정리
- [x] 추가 인원 2명 역할 분리
- [x] 연구 범위 이탈 방지 프롬프트 추가
- [x] 이미지 딥러닝 Cell Detection을 Future Work로 분리

### 가장 먼저 할 일

- [ ] 대표 페이지 exhaustive GT 구축
- [ ] partial GT 기반 FP/Precision 해석 수정
- [ ] `bang_` 실제 `cells.json` / 시각화 결과 생성
- [ ] `bang_` over-merge / irregular component 검증
- [ ] Morphology / Contour / TATR / PP-Structure / OpenCV merged reconstruction을 동일 GT로 비교

### 그 다음 핵심 실험

- [ ] Full OCR vs GT ROI OCR vs Detected ROI OCR
- [ ] Anchor-ROI PoC
- [ ] 최종 Field Accuracy 비교
- [ ] 대표 실패 사례 유형화

---

## 데이터 확보 원칙

1차 실험 목표는 **서로 다른 계약서 양식 10종**을 억지로 모으는 것이 아니라, 동일 또는 유사한 정형 양식에서 내용·해상도·기울기·흐림·촬영조건 등이 다른 이미지 10~20장을 확보하는 것이다.

서로 크게 다른 계약서 양식으로의 일반화는 현재 필수 범위가 아니며, 필요하면 후속 연구에서 확장한다.

---

## Future Work

현재 본 논문에서 구현하지 않는 후보:
- YOLO / DETR / Faster R-CNN 기반 Cell Object Detection
- Mask R-CNN 등 Instance Segmentation 기반 Cell 분할
- 별도 Cell Detector 파인튜닝
- 대규모 Cell Detection 학습 데이터 구축
- 다양한 계약서 양식 간 일반화 실험

이 항목들은 현재 비교 실험과 Field Accuracy 검증이 끝난 뒤 필요성을 다시 판단한다.

---

## 관리 원칙

1. 새 작업·새 모델·새 기능을 추가하기 전에 `00_scope_guard_prompt.md`로 범위를 판정한다.
2. 연구 방향·가설·공통 실험 계획·전체 현황은 `01_research_direction_and_next_steps.md`에서만 관리한다.
3. 담당자 피드백은 `feedback_*.md`에만 기록한다.
4. 추가 인력 작업은 `assignment_*.md`에 기록한다.
5. 공통 연구 아이디어는 피드백 파일에 반복하지 않고 중앙 연구 문서로 이동한다.
6. 새 실험 결과가 나오면 공통 연구 문서의 최신 진행 상황과 현황을 먼저 업데이트한다.
7. 역할이 겹치면 `Cell Detection`, `Structure Reconstruction`, `OCR Re-recognition`, `Field Mapping` 단계 기준으로 다시 분리한다.
8. 범위를 벗어나는 아이디어는 즉시 구현하지 않고 Future Work로 남긴다.
