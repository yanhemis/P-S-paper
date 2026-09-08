# 담당자 피드백 — `dahye_cell_DetectionSurvey`

## 이 문서의 역할

이 파일은 `dahye_cell_DetectionSurvey` 브랜치의 **표 구조 인식 모델 조사와 비교 실험에 대한 피드백만** 기록한다.

OpenCV 구현 피드백은 `feedback_bang_opencv_roi.md`에서 별도로 관리하며, 공통 연구 방향과 다음 작업은 `01_research_direction_and_next_steps.md`에서 관리한다.

---

## 1. 현재 작업의 의미

이 브랜치는 다음 역할을 한다.

- PP-Structure, TATR, LayoutParser, SLANet 등 구조 모델 후보 조사
- 한국어 임대차계약서 적용 가능성 예비 확인
- 실행 환경/의존성 문제 기록
- 범용 구조 모델의 한계를 통해 후속 비교 실험 후보를 좁히는 역할

즉, 본 실험의 최종 성능 비교라기보다 **모델 후보 선별용 예비 탐색**으로 보는 것이 적절하다.

---

## 2. 잘 된 점

- 셀 좌표 반환 여부, 한국어 적용 가능성, CPU 실행, 설치 난이도, 처리 시간 등 연구에 필요한 비교 기준을 잡음
- 실행 성공뿐 아니라 환경 충돌과 실패 이유도 기록함
- TATR의 구조 검출 결과, SLANet의 레이아웃 붕괴 등 실제 관찰을 남김
- 범용 구조 모델만 고집하지 않고 OpenCV + OCR 방향을 후속 후보로 제시함

---

## 3. 해석 수정이 필요한 부분

### 실행 실패와 성능 실패를 구분

예:
- LayoutParser가 Windows/CPU에서 실행되지 않은 경우 → `성능이 낮음`이 아니라 `현재 환경에서 평가하지 못함`
- 특정 PP-Structure 버전에서 한국어 설정이 제한된 경우 → Paddle 계열 전체가 한국어를 지원하지 않는다고 일반화하지 않음

### TATR의 `셀 좌표 반환 불가` 표현 수정

TATR는 row / column / spanning-cell 등의 구조 결과를 이용하여 cell bbox를 재구성할 수 있다.

따라서 다음처럼 정리하는 것이 적절하다.

> 본 임대차계약서 실험에서는 TATR 구조 결과로부터 목표 병합 셀을 안정적으로 재구성하지 못하였다.

핵심 질문은 `셀 좌표를 반환 가능한가?`가 아니라 **재구성된 cell bbox가 Ground Truth와 얼마나 일치하는가?** 이다.

### `한국어라서 좌표가 붕괴한다`는 표현 피하기

Text Detection, Recognition, Table Structure를 분리해서 해석한다.

### `완벽`, `최적`, `가장 확실` 표현 피하기

현재 단계에서는 다음 정도가 적절하다.

> 예비 조사에서 OpenCV 기반 ROI 접근의 적용 가능성을 확인했으며, 후속 정량 비교 대상으로 선정한다.

---

## 4. 이 담당자에게 필요한 다음 보완

- [ ] 사용한 모델/라이브러리 버전과 실행 환경을 명확히 유지
- [ ] 실행 실패와 모델 성능 실패를 표에서 분리
- [ ] 최신 PP-StructureV3 + Korean OCR 조합 재확인
- [ ] TATR row/column/spanning-cell 결과 저장
- [ ] TATR 결과에서 실제 cell bbox 재구성
- [ ] 일반 셀 / 병합 셀을 나눠 평가
- [ ] 동일 계약서에서 bbox 시각화 결과 저장
- [ ] 가능하면 IoU / Precision / Recall 같은 정량 지표 추가

---

## 5. README 개선 권장 형식

| 모델 | 실행 성공 | Text bbox | Cell bbox | 병합 셀 | 한국어 OCR | 한계/제외 사유 |
|---|---|---|---|---|---|---|
| PaddleOCR | O | O | - | - | O | 구조 정보 없음 |
| PP-StructureV3 | 확인 | O | 확인 | 확인 | O | 최신 버전 재검증 |
| TATR | O | OCR 별도 | 재구성 | 검증 필요 | 별도 OCR | 복잡 구조 평가 필요 |
| LayoutParser | 환경 의존 | 평가 불가 | 평가 불가 | 평가 불가 | - | 환경 문제 |

결과 이미지는 가능하면 동일 샘플 기준으로 남긴다.

- 원본
- text bbox
- row/column/span 결과
- cell bbox
- 병합 셀 결과

---

## 한 줄 피드백

> 현재 조사는 모델 후보를 좁히는 예비 탐색으로 충분히 가치가 있으며, 다음 단계에서는 `지원 여부`를 단정하기보다 동일 Ground Truth에서 Cell Reconstruction과 병합 셀 성능을 정량 비교하는 방향으로 발전시키면 좋다.
