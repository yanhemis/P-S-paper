# 담당자 피드백 — `bang_`

## 이 문서의 역할

이 파일은 `bang_` 브랜치의 **OpenCV 기반 표선/셀/ROI 검출 프로토타입과 병합 셀 구조 복원에 대한 피드백만** 기록한다.

구조 모델 조사·평가기는 `dahye_cell_DetectionSurvey`, Morphology/Contour 방식 비교는 `heewon`, OCR 재인식은 추가 인원 A, Anchor-ROI는 추가 인원 B가 담당한다.

공통 연구 방향과 전체 다음 작업은 `01_research_direction_and_next_steps.md`에서 관리한다.

---

## 1. 현재 작업의 의미

이 브랜치는 연구 가설 중 다음 부분을 직접 구현한 프로토타입에 해당한다.

> 정형 임대차계약서에서 물리적 표선을 이용한 OpenCV 기반 Cell/ROI Detection이 실제로 가능한가?

현재 구현에는 다음 요소가 들어가 있다.

- CLAHE + adaptive threshold를 이용한 대비 강화/이진화
- 수평/수직 morphology 기반 표선 추출
- morphology closing을 이용한 끊어진 선 보정
- connected component 길이 기준의 문자 획 오검출 제거
- grid 좌표 추출
- 경계선 유무 기반 병합 셀 후보 탐지
- rows × cols 기반 cell bbox 생성
- 처리 시간 출력

즉, 현재까지는 **OpenCV Cell Detection baseline prototype** 단계이다.

---

## 2. 현재 코드에서 가장 중요한 보완점

### 2.1 병합 셀 후보 탐지와 실제 bbox 재구성이 연결되지 않음

현재 `detect_merged_cells()`는 오른쪽/아래쪽 경계가 없는 셀을 병합 후보로 기록한다.

하지만 최종 bbox는 `get_cell_boxes_from_grid(rows, cols)`에서 모든 `rows × cols` 조합으로 생성된다.

따라서 현재 상태는 다음과 같이 표현하는 것이 정확하다.

> 병합 셀 **후보 탐지는 구현**, 병합 정보를 반영한 **최종 merged bbox 재구성은 미구현**.

다음 단계에서는 병합 후보 정보를 이용하여 인접 기본 셀들을 실제 하나의 bbox로 합치는 로직이 필요하다.

---

### 2.2 morphology kernel 비율이 짧은 내부 경계선을 제거할 가능성

현재 수평/수직 선 추출 커널은 이미지 폭/높이의 약 40%를 기준으로 잡는다.

임대차계약서에는 페이지 전체 길이에 비해 짧은 내부 셀 경계가 많기 때문에, 고정된 큰 커널을 사용하면 짧은 선이 opening 단계에서 사라질 수 있다.

다만 이 파라미터 자체의 방식 비교와 최적화는 `heewon`의 Morphology/Contour 비교와 겹칠 수 있으므로, `bang_`은 **검출기 선택보다 검출 결과를 받아 병합 구조를 복원하는 쪽에 우선 집중**한다.

필요한 최소 확인만 한다.

- [ ] 입력 line/grid가 정상일 때 merged reconstruction이 제대로 작동하는지 확인
- [ ] 입력 선이 일부 끊긴 경우 오병합이 어떻게 발생하는지 기록
- [ ] 해상도에 따라 boundary tolerance가 지나치게 달라지지 않도록 상대값 사용

---

### 2.3 `close_gaps()`의 수직선 보정 길이 기준 점검

현재 closing 길이가 `img_w` 기준 하나로 계산되어 수평/수직 모두에 사용된다.

수평선과 수직선은 다음처럼 별도로 두는 것이 더 자연스럽다.

```python
h_close_len = int(img_w * ratio)
v_close_len = int(img_h * ratio)
```

이 수정은 현재 프로토타입 안정화를 위한 최소 수정으로 처리하고, 이후 세부 파라미터 탐색은 `heewon` 비교 결과를 참고한다.

---

## 3. 현재 결과를 해석할 때 주의할 점

### `병합 셀 처리 가능`은 아직 강한 표현

현재는 병합 후보를 찾는 단계이므로 다음 표현이 적절하다.

> 경계선 누락을 이용한 병합 셀 후보 탐지는 가능하며, 실제 병합 bbox 재구성은 후속 구현이 필요하다.

### `셀 개수`만으로 정확도를 판단하면 안 됨

검출 셀 개수가 정답 개수와 같아도 위치와 병합 관계가 틀릴 수 있다. 정량 평가는 공통 evaluator가 수정된 이후 동일 Ground Truth로 수행한다.

### 처리 시간 일반화 주의

샘플 한 장의 실행 시간을 전체 데이터셋 성능으로 일반화하지 않는다.

---

# 4. 다음 단계 확정 — Merged Cell Reconstruction

## 목표

`bang_`의 다음 핵심 산출물은 **OpenCV로 검출된 기본 grid를 실제 일반 셀/병합 셀 bbox로 복원하는 모듈**이다.

셀 검출 방법 자체를 계속 늘리는 것이 아니라, 어떤 검출 결과가 들어오더라도 다음 흐름을 수행하는 것을 목표로 한다.

```text
horizontal / vertical line mask
        +
rows / cols primitive grid
        ↓
각 인접 셀 사이 shared boundary 존재율 계산
        ↓
boundary가 없는 인접 셀 연결
        ↓
연결된 primitive cells를 하나의 component로 묶음
        ↓
General / Merged Cell bbox 생성
        ↓
cells.json 저장
```

### 권장 구현 방식

단순히 `merged_cells` 리스트를 만드는 데서 끝내지 말고, primitive cell을 node로 보고 인접 관계를 연결하는 방식이 적합하다.

예:

- 오른쪽 내부 경계가 없으면 `(r,c)`와 `(r,c+1)` 연결
- 아래 내부 경계가 없으면 `(r,c)`와 `(r+1,c)` 연결
- 연결된 셀 그룹을 Union-Find 또는 graph connected component로 묶음
- 그룹 전체의 `xmin, ymin, xmax, ymax`로 최종 merged bbox 생성

이를 통해 2칸 병합뿐 아니라 여러 행/열에 걸친 병합도 동일한 방식으로 처리할 수 있는지 확인한다.

---

## 5. boundary 판정 로직에서 확인할 것

현재처럼 경계 주변의 작은 strip에서 pixel 존재율을 측정하는 방향은 사용할 수 있지만, 다음을 보완한다.

- [ ] 모서리 교차점은 boundary 존재율 계산에서 일부 제외해 과대평가 방지
- [ ] 수직/수평 경계마다 별도 tolerance 사용
- [ ] `presence_ratio`를 절대적인 한 값으로 고정하기보다 최소 몇 개 값에서 민감도 확인
- [ ] 외곽 테두리와 내부 shared boundary를 구분
- [ ] 끊어진 선을 `병합`으로 오판하는 실패 사례 별도 저장

특히 현재처럼 대부분의 셀이 merged 후보가 되는 현상이 나타나면 **실제 병합 셀이 많은 것이 아니라 boundary 판정 자체가 실패한 것인지 먼저 확인**한다.

---

## 6. 표준 출력 형식

`bang_`은 OCR까지 수행하지 않고, 다음 담당자가 바로 사용할 수 있는 구조 결과를 생성한다.

권장 예시:

```json
{
  "image": "sample_01.jpg",
  "method": "opencv_grid_merge",
  "cells": [
    {
      "id": 0,
      "bbox": [x1, y1, x2, y2],
      "type": "general",
      "primitive_cells": [[0, 0]]
    },
    {
      "id": 1,
      "bbox": [x1, y1, x2, y2],
      "type": "merged",
      "primitive_cells": [[1, 0], [1, 1]]
    }
  ]
}
```

가능하면 디버깅을 위해 각 병합에 사용한 boundary score도 별도 저장한다.

---

## 7. 실험 설계

### A. 기능 검증

먼저 대표 샘플에서 다음 세 결과를 각각 시각화한다.

```text
1. primitive grid bbox
2. missing boundary 판정 결과
3. 최종 merged/general bbox
```

이렇게 해야 오류가 `선 검출`, `boundary 판정`, `union` 중 어디서 생겼는지 구분할 수 있다.

### B. Ablation 비교

공통 Ground Truth가 준비되면 다음 둘을 비교한다.

```text
OpenCV primitive grid
vs
OpenCV + merged reconstruction
```

목적은 병합 로직을 추가했을 때 특히 merged cell 성능이 실제로 좋아지는지 확인하는 것이다.

### C. 공통 평가기 연결

`bang_`이 별도의 평가기를 새로 만드는 것은 우선순위가 아니다.

`dahye_cell_DetectionSurvey`의 evaluator가 다음 조건을 갖춘 뒤 같은 형식으로 prediction을 전달한다.

- IoU threshold 명시
- GT-Pred 1:1 matching
- Precision / Recall / F1
- General / Merged 분리

---

## 8. 다른 담당자와의 작업 경계

### `bang_`이 담당

- primitive grid → merged/general cell 구조 복원
- shared boundary 판정
- union/connected component 기반 병합
- 최종 cell bbox
- 표준 `cells.json`
- 병합 전/후 결과 시각화

### `bang_`이 하지 않음

- 새로운 Table Structure 모델 조사 → `dahye`
- Morphology vs Contour 방식 선정/비교 → `heewon`
- evaluator 설계 → `dahye`
- ROI OCR / CER / Field Accuracy → 추가 인원 A
- Anchor label 기반 ROI 생성 → 추가 인원 B

이 경계를 유지하면 기능별 작업이 중복되지 않는다.

---

## 9. 완료 조건

다음 조건을 만족하면 `bang_`의 Merged Cell Reconstruction 1차 작업을 완료한 것으로 본다.

- [ ] primitive cell 인접 관계를 이용한 실제 merged bbox 생성
- [ ] 2열 병합, 2행 병합, 다중 행/열 병합을 동일 로직으로 처리 가능
- [ ] general / merged bbox 구분 출력
- [ ] 병합 전 / boundary 판정 / 병합 후 시각화 3종 저장
- [ ] 표준 `cells.json` 생성
- [ ] 공통 GT 샘플에서 prediction 파일 생성
- [ ] `primitive grid vs merged reconstruction` 평가 가능 상태 확보
- [ ] 대표 오병합 / 미병합 사례 최소 3종 기록

완료 후에는 추가 기능을 계속 붙이기보다 결과를 공통 실험으로 넘기고, 다음 단계인 ROI OCR/Field Accuracy는 담당 A가 이어받는다.

---

## 한 줄 피드백

> `bang_`의 다음 단계는 OpenCV 검출 방법을 더 늘리는 것이 아니라, **검출된 기본 grid를 일반/병합 셀 구조로 안정적으로 재구성하고 표준 bbox 결과를 만들어 후속 OCR 실험에 넘기는 것**으로 고정한다.
