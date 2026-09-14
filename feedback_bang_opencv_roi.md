# 담당자 피드백 — `bang_`

> 마지막 업데이트: 2026-09-14

## 이 문서의 역할

이 파일은 `bang_` 브랜치의 **OpenCV 기반 표선/셀/ROI 검출과 병합 셀 구조 복원에 대한 피드백만** 기록한다.

구조 모델 조사·평가기는 `dahye_cell_DetectionSurvey`, Morphology/Contour 방식 비교는 `heewon`, OCR 재인식은 추가 인원 A, Anchor-ROI는 추가 인원 B가 담당한다.

공통 연구 방향과 전체 다음 작업은 `01_research_direction_and_next_steps.md`에서 관리한다.

---

## 1. 현재 작업 상태

이전 피드백 이후 `bang_` 브랜치는 단순한 병합 셀 후보 탐지 단계에서 **실제 병합 셀 구조 복원 구현 단계**로 발전했다.

현재 추가된 주요 기능:

- HoughLinesP 기반 기울기 보정(deskew)
- 이미지 해상도 비례 parameter scaling
- adaptive threshold block size 보정
- 수평/수직 closing 길이 분리
- shared boundary 존재 여부 판정
- 외곽선 손상과 내부 boundary 누락 구분
- Union-Find 기반 primitive cell 병합
- general / merged bbox 생성
- primitive cell 구성 정보 저장
- 표준 `cells.json` 출력 코드
- 병합 과정 시각화 코드

따라서 기존의

> 병합 후보 탐지는 구현, 실제 merged bbox 재구성은 미구현

이라는 평가는 더 이상 현재 상태와 맞지 않는다.

현재는 다음처럼 정리한다.

> **병합 셀 reconstruction 로직 1차 구현 완료. 이제 실제 결과 생성, 오류 검증, Ground Truth 기반 정량평가가 필요하다.**

---

## 2. 잘 반영된 피드백

### 2.1 실제 병합 bbox 재구성

primitive cell을 node로 보고 내부 경계가 없는 인접 셀을 Union-Find로 연결하여 최종 bbox를 만드는 구조가 추가되었다.

이 방향은 2열/2행뿐 아니라 여러 primitive cell이 연결된 병합 구조를 하나의 로직으로 처리할 수 있다는 점에서 적절하다.

### 2.2 `close_gaps()` 수평/수직 기준 분리

기존에는 closing 길이가 `img_w` 하나를 기준으로 수평/수직에 모두 적용되었으나, 현재는 수평선은 폭, 수직선은 높이 기준으로 분리되었다.

### 2.3 해상도 비례 파라미터

절대 픽셀값만 사용하는 대신 해상도에 따라 gap threshold, strip 폭 등을 조정하는 방향이 추가되었다.

### 2.4 후속 실험에서 사용할 표준 출력

최종 셀마다 다음 정보를 남기는 구조가 추가되었다.

```json
{
  "id": 0,
  "bbox": [x1, y1, x2, y2],
  "type": "general or merged",
  "primitive_cells": [[row, col]]
}
```

이 결과는 이후 공통 evaluator와 ROI OCR 담당자에게 전달하기 적합하다.

---

## 3. 지금 가장 먼저 확인할 문제

### 3.1 `h_ratio=0.4`, `v_ratio=0.4` 문제는 아직 남아 있음

실제 실행부에서 `extract_hv_lines()`를 기본값으로 호출하고 있으므로 현재도 수평/수직 opening kernel이 이미지 폭/높이의 약 40%이다.

임대차계약서에는 짧은 내부 경계선이 많기 때문에 이 값이 지나치게 크면 내부 선이 사라질 수 있다.

이번에는 이 문제가 더 중요하다.

```text
짧은 선 검출 실패
  -> shared boundary 없음으로 판정
  -> Union-Find 연결
  -> 실제로는 다른 셀인데 하나로 합쳐짐
  -> 오병합
```

따라서 다음을 최소한 확인한다.

- [ ] 대표 샘플에서 짧은 내부 경계가 실제로 남는지 시각화
- [ ] `0.4`와 더 작은 몇 개 값에서 결과 비교
- [ ] 목적은 최적 파라미터 탐색이 아니라 **오병합 원인이 line extraction인지 reconstruction인지 분리**하는 것

세부 Morphology 최적화 자체는 `heewon` 작업과 겹치므로 과도하게 확장하지 않는다.

---

### 3.2 비직사각형 Union component 검증

현재 연결된 primitive cell component의 최소/최대 row, col로 하나의 bbox를 생성한다.

만약 잘못된 boundary 판정 때문에 다음과 같은 L자 연결이 생기면,

```text
XX
X.
```

bounding rectangle은 실제 component에 포함되지 않은 오른쪽 아래 영역까지 포함할 수 있다.

따라서 최종 merged bbox 생성 전에 최소한 다음 검사를 권장한다.

```text
row_span = max_row - min_row + 1
col_span = max_col - min_col + 1
expected_count = row_span * col_span

len(primitive_cells) == expected_count ?
```

불일치하면 `irregular_component` 또는 reconstruction failure로 기록하고 정상 merged cell로 확정하지 않는 것이 안전하다.

---

### 3.3 코드 구현과 실제 실험 결과를 분리

현재 브랜치에는 reconstruction 코드가 추가되었지만, 공통 결과로 사용할 실제 `cells.json`과 최종 시각화 결과가 아직 충분히 남아 있지 않다.

다음 산출물을 커밋 또는 결과 폴더에 보관한다.

```text
primitive_grid.jpg
boundary_result.jpg
merged_cells.jpg
cells.json
runtime / parameter 기록
```

코드가 있다는 것과 실제 계약서에서 성능이 검증됐다는 것은 구분한다.

---

## 4. 다음 확정 작업

### A. reconstruction 기능 검증

- [ ] 대표 계약서에서 실제 `cells.json` 생성
- [ ] general / merged bbox 시각화
- [ ] primitive grid → boundary → final bbox 3단계 비교 이미지 저장
- [ ] 2열 병합 / 2행 병합 / 다중 병합 사례 확인
- [ ] rectangularity 검사 추가 또는 비정상 component 로그 저장

### B. 공통 평가 연결

`bang_`은 별도의 평가기를 만들 필요가 없다.

공통 evaluator에 전달할 prediction만 동일 형식으로 준비한다.

평가 전제:
- representative page의 exhaustive GT 확보
- IoU threshold 명시
- GT-Pred 1:1 matching
- General / Merged 분리
- Precision / Recall / F1

### C. 실패 사례 기록

최소 다음 유형을 구분한다.

- line detection failure
- missing boundary 오판
- over-merge
- under-merge
- irregular component
- deskew 실패

---

## 5. 데이터 확보 관련 피드백

공통 데이터 확보를 돕는 것은 현재 연구 범위 안에 있다.

다만 목표를 `서로 다른 계약서 양식 10종`으로 고정하지 않는다.

현재 1차 실험에서는 **동일 또는 유사한 정형 임대차계약서 양식의 이미지 10~20장**을 우선 확보하고, 다음 차이를 기록하는 것이 더 중요하다.

- 스캔 / 촬영
- 해상도
- 기울기
- 흐림
- 그림자
- 압축 손상
- 작성 내용 차이

양식 자체가 크게 다른 계약서들 사이의 일반화는 현재 논문의 필수 목표가 아니며, 필요하면 후속 단계에서 확장한다.

---

## 6. 이미지 딥러닝 Cell Detection 아이디어 처리

셀 자체를 이미지 객체처럼 보고 Object Detection 또는 Instance Segmentation으로 찾는 아이디어는 연구적으로 의미가 있다.

예:
- YOLO / DETR / Faster R-CNN 기반 Cell Detection
- Mask R-CNN 기반 Cell Instance Segmentation
- 별도 학습 데이터로 Cell Detector 파인튜닝

하지만 현재는 **구현하지 않는다.**

이유:
- 새로운 학습 데이터셋 구축이 필요함
- 모델 선택/학습/검증이라는 별도 실험축이 생김
- 기존 OpenCV / TATR / PP-Structure / Anchor-ROI 비교가 끝나기 전에 범위가 과도하게 넓어짐
- 현재 중심 질문인 ROI 활용에 따른 최종 Field Accuracy 검증이 늦어질 수 있음

따라서 이 아이디어는 `Future Work`로 이동한다.

현재 방법을 충분히 비교한 뒤에도 Cell/ROI Detection이 최종 성능의 핵심 병목으로 남을 경우 다음 연구에서 검토한다.

**`bang_`의 현재 다음 작업으로는 배정하지 않는다.**

---

## 7. 다른 담당자와의 작업 경계

### `bang_`이 담당

- primitive grid → merged/general cell 구조 복원
- shared boundary 판정
- Union-Find/connected component 기반 병합
- final cell bbox
- 표준 `cells.json`
- 병합 전/후 시각화
- reconstruction 실패 유형 기록

### `bang_`이 하지 않음

- 새로운 Table Structure 모델 조사 → `dahye`
- Morphology vs Contour 방식 선정/비교 → `heewon`
- evaluator 설계 → `dahye`
- ROI OCR / CER / Field Accuracy → 추가 인원 A
- Anchor label 기반 ROI 생성 → 추가 인원 B
- Object Detection / Instance Segmentation 기반 Cell Detector 학습 → **Future Work**

---

## 8. 1차 완료 조건

다음 조건을 만족하면 `bang_`의 Merged Cell Reconstruction 1차 작업을 완료한 것으로 본다.

- [x] primitive cell 인접 관계 기반 merged bbox 생성 로직 구현
- [x] general / merged bbox 구조 정의
- [x] 표준 `cells.json` 출력 코드 구현
- [x] deskew / scale-aware boundary 처리 1차 구현
- [ ] 실제 대표 샘플의 `cells.json` 생성 및 보관
- [ ] 병합 전 / boundary / 병합 후 시각화 결과 보관
- [ ] rectangularity 또는 비정상 component 검사
- [ ] 공통 exhaustive GT 샘플에서 prediction 생성
- [ ] `primitive grid vs merged reconstruction` 평가 가능 상태 확보
- [ ] 대표 오병합 / 미병합 / irregular 사례 최소 3종 기록

완료 후에는 별도 딥러닝 셀 검출로 확장하지 않고 결과를 공통 실험으로 넘긴다.

---

## 한 줄 피드백

> `bang_`은 병합 셀 reconstruction 1차 구현까지 진전했으므로, 이제 새 기능을 늘리기보다 **실제 결과 파일 생성·오병합 검증·공통 GT 평가까지 마무리**하는 것이 우선이며, Object Detection/Instance Segmentation 기반 셀 검출은 후속 연구로 미룬다.
