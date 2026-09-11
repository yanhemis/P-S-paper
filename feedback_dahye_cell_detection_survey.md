# 담당자 피드백 — `dahye_cell_DetectionSurvey`

> 마지막 업데이트: 2026-09-11

## 이 문서의 역할

이 파일은 `dahye_cell_DetectionSurvey` 브랜치의 **표 구조 인식 모델 조사, TATR/PP-Structure 실험, 정량 평가 코드에 대한 피드백만** 기록한다.

OpenCV 구현 피드백은 다른 담당자 문서에서 관리하며, 공통 연구 방향과 전체 다음 작업은 `01_research_direction_and_next_steps.md`에서 관리한다.

---

## 1. 현재 작업의 의미

이 브랜치는 초기 모델 조사 단계에서 한 단계 발전했다.

현재 역할:
- PP-Structure, TATR, LayoutParser, SLANet 등 구조 모델 후보 조사
- 한국어 임대차계약서 적용 가능성 예비 확인
- 실행 환경/의존성 문제 기록
- TATR cell bbox 재구성 실험
- GT 수동 라벨링 도구 작성
- Cell IoU 기반 정량 평가 코드 초안 작성

즉, 현재는 단순 Survey가 아니라 **구조 모델 비교와 공통 evaluator의 기초를 만드는 역할**까지 포함한다.

---

## 2. 잘 반영된 부분

이전 피드백 중 다음 내용이 실제 README와 코드에 반영되었다.

- 실행 실패와 모델 성능 실패를 분리해서 서술
- `한국어라서 좌표가 붕괴한다`는 식의 과도한 일반화 완화
- TATR의 row/column 결과에서 cell bbox를 재구성하는 코드 추가
- Ground Truth 라벨링 도구 추가
- 일반 셀과 병합 셀을 분리해 평가하려는 방향 추가
- OpenCV를 `최적`이라고 단정하지 않고 후속 정량 비교 대상으로 변경

방향 자체는 현재 연구 흐름과 잘 맞는다.

---

## 3. 이번 버전에서 우선 수정할 부분

### 3.1 IoU threshold 코드와 출력 문구 불일치

현재 `evaluate.py`의 기본값은 다음과 같다.

```python
def evaluate_model(gt_data, pred_boxes, iou_threshold=0.01):
```

하지만 출력 문구와 README 설명은 `IoU Threshold: 0.5`를 기준으로 작성되어 있다.

따라서 현재 출력된 점수는 문서에 적힌 평가 조건과 일치하지 않는다.

필수 수정:
- [ ] 실제 평가 threshold를 0.5로 할지 다른 값으로 할지 먼저 확정
- [ ] 함수 기본값과 출력 문구를 동일하게 수정
- [ ] threshold를 코드에 하드코딩하기보다 인자로 명시
- [ ] 기존 점수는 수정 후 재측정

현재 README의 `IoU > 0.5에서 33.3%` 같은 수치는 재평가 전까지 확정 결과로 사용하지 않는다.

---

### 3.2 현재 평가는 과분할 False Positive를 충분히 반영하지 못함

현재 평가는 각 GT에 대해 가장 높은 IoU의 예측 bbox 하나를 찾아 match 여부만 확인한다.

이 방식은 예측 bbox가 매우 많이 생성되는 경우에도 GT 하나와 조금이라도 겹치는 bbox가 있으면 match로 처리될 수 있다.

예를 들어 PP-Structure에서 166개의 bbox가 생성되었다면, 단순 Recall만으로는 over-segmentation을 충분히 벌점 줄 수 없다.

필수 보완:
- [ ] GT-Pred 1:1 matching 방식 구현
- [ ] 이미 매칭된 prediction은 다시 사용하지 않도록 처리
- [ ] TP / FP / FN 계산
- [ ] Precision / Recall / F1 출력
- [ ] General / Merged 셀을 각각 별도 집계

가능하면 IoU 0.5를 기본 threshold로 두고 필요 시 0.3/0.5/0.7 민감도 비교를 추가한다.

---

### 3.3 Ground Truth 샘플 검수 필요

현재 `gt_sample.json`은 평가 코드 작동 확인용으로는 적절하지만 논문용 평가 데이터로는 부족하다.

확인된 점:
- GT가 5개뿐임
- 병합 셀 좌표 중 거의 동일한 bbox가 두 개 존재하여 중복 라벨 가능성이 있음

필수 작업:
- [ ] 현재 5개 GT 수동 검수
- [ ] 중복 bbox 여부 확인
- [ ] 대표 한 페이지의 실제 셀을 더 충분히 라벨링
- [ ] 이후 최소 10장 이상으로 확장
- [ ] 가능하면 `image_id`, `cell_id`, `type`, `bbox`를 포함하도록 포맷 개선

---

### 3.4 TATR reconstruction에 `spanning-cell`이 실제로 반영되어야 함

현재 README에는 row / column / spanning-cell 결과에서 cell bbox를 재구성했다고 설명되어 있으나, 현재 코드에서는 실제로 `table row`, `table column`만 수집한 뒤 모든 row×column 조합을 cell로 생성한다.

따라서 현재 구현은 **regular grid reconstruction**에 가깝고, 병합 셀 복원 로직은 아직 부족하다.

필수 작업:
- [ ] `table spanning cell` label 결과도 별도 수집
- [ ] spanning 영역과 겹치는 기본 cell들을 병합
- [ ] 단순 row×column 방식과 spanning 반영 방식 결과 비교
- [ ] 일반 셀 / 병합 셀 Precision, Recall을 별도로 출력

이 부분이 H3 검증의 핵심이다.

---

### 3.5 `PP-Structure`와 `PP-StructureV3` 명칭 분리

현재 저장된 실행 코드는 다음 계열이다.

```python
from paddleocr import PPStructure
```

실행 환경도 `paddleocr==2.8.1`로 기록되어 있다.

따라서 이 결과를 `PP-StructureV3 예비 검증 결과`라고 표기하면 실제 실행 코드와 모델 버전이 불일치하게 된다.

권장:
- 현재 결과 → `PP-Structure (PaddleOCR 2.8.1)`
- 향후 별도 실행 → `PP-StructureV3`

필수 작업:
- [ ] README 명칭 수정
- [ ] 실제 V3를 실행했다면 별도 폴더/버전/requirements로 분리
- [ ] V2.x 결과와 V3 결과를 섞지 않기

---

## 4. 논문 표현에서 아직 보류할 문장

현재 README의 다음 수준 표현은 평가 체계 수정 전까지 조금 약하게 유지하는 것이 좋다.

피해야 할 확정 표현:
- `정량적으로 입증함`
- `기술 개발이 필수적임`
- `기존 오픈소스 모델은 해결할 수 없음`

현재 권장 수준:

> 예비 평가에서는 복잡한 병합 셀 영역에서 과분할 및 낮은 일치율이 관찰되었으며, 평가 코드와 Ground Truth를 보완한 뒤 구조 모델과 후처리 방법의 성능을 추가 검증한다.

---

## 5. 이 담당자의 다음 완료 기준

다음 조건이 충족되면 이 브랜치의 1차 역할이 상당히 완성된다.

- [ ] IoU threshold 오류 수정
- [ ] 1:1 matching 구현
- [ ] Precision / Recall / F1 출력
- [ ] GT 중복 검수 및 확대
- [ ] TATR spanning-cell 반영 reconstruction
- [ ] PP-Structure 2.x / V3 명칭 분리
- [ ] TATR / PP-Structure 결과를 동일 GT에서 평가
- [ ] 결과 JSON과 대표 bbox 이미지 저장

---

## 한 줄 피드백

> 이전 피드백이 상당 부분 반영되어 Survey에서 정량 평가 단계로 발전했다. 이제 모델을 더 추가하기보다 **평가 코드의 신뢰성을 먼저 고치고, TATR 병합 셀 reconstruction을 실제 spanning-cell 정보까지 반영하는 것**이 가장 중요하다.
