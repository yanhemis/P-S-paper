# 추가 인원 B 작업 배정 — Anchor-ROI / Field Mapping PoC

> 배정일: 2026-09-11

## 이 문서의 역할

이 파일은 현재 별도 작업이 없는 추가 인원 B에게 배정할 **Anchor-ROI 기반 핵심 필드 매핑 PoC 작업만** 정리한다.

전체 표의 Cell Detection, 병합 셀 재구성, 구조 모델 비교, OCR 모델 자체 성능 비교는 다른 담당자의 범위이므로 여기서는 하지 않는다.

---

## 1. 담당 목표

다음 질문에 답하는 것이 핵심이다.

> **전체 표 구조를 복원하지 않고 `보증금`, `임대인`, `소재지` 같은 라벨의 위치를 기준으로 값 영역을 찾는 것만으로 핵심 필드 추출이 가능한가?**

이 작업은 연구 가설 H6을 직접 검증한다.

---

## 2. 기본 아이디어

```text
전체 페이지 OCR 결과
  -> 핵심 라벨 탐색
  -> 라벨 bbox 확보
  -> 상대 위치 기반 값 ROI 생성
  -> ROI 내부 텍스트 선택 또는 재OCR
  -> 필드별 형식 후처리
  -> Ground Truth와 비교
```

예:

```text
"보증금" bbox
   -> 오른쪽 일정 범위
   -> 금액 후보 텍스트 탐색
   -> 숫자/원 단위 후처리
```

목적은 완벽한 표 복원이 아니라 **핵심 필드 추출에 필요한 최소 공간 구조만 사용하는 것**이다.

---

## 3. 우선 대상 필드

1차 PoC는 다음 5개로 제한한다.

- [ ] 보증금
- [ ] 계약금
- [ ] 소재지
- [ ] 임대인 성명
- [ ] 임차인 성명

여유가 있으면:
- 잔금
- 계약기간

---

## 4. 1단계 — Anchor label 검출

전체 OCR 결과에서 핵심 라벨을 찾는다.

확인할 항목:
- [ ] 정확히 일치하는 라벨
- [ ] 공백 포함 변형
- [ ] OCR 오인식이 있는 라벨

예:

```text
보증금
보 증 금
보증 금
```

1차 구현은 단순 문자열 정규화 수준이면 충분하다.

기록:
- Anchor Detection Success Rate
- 어떤 라벨이 자주 실패하는지

---

## 5. 2단계 — 상대 위치 ROI 정의

절대 pixel 좌표를 고정하기보다 가능한 한 이미지 크기나 anchor bbox 기준 상대 좌표를 사용한다.

예시 개념:

```text
anchor = [x1, y1, x2, y2]

value_roi =
  x: anchor.x2 ~ anchor.x2 + k * anchor_width
  y: anchor.y1 - margin ~ anchor.y2 + margin
```

필드별로 `right`, `below`, `same-row` 등 관계를 기록한다.

권장 포맷:

```json
{
  "field": "보증금",
  "anchor": "보증금",
  "direction": "right",
  "x_ratio": 5.0,
  "y_margin_ratio": 0.5
}
```

---

## 6. 3단계 — 값 후보 선택

ROI 안에 텍스트가 여러 개 있을 수 있으므로 필드 특성에 따라 최소한의 규칙을 적용한다.

### 금액 필드

- 숫자 포함 여부
- `원` 포함 여부
- 쉼표/공백 제거 후 숫자 정규화

### 성명

- anchor 오른쪽 또는 인접 셀 텍스트
- 너무 긴 문자열 제외

### 소재지

- 같은 행 또는 우측 넓은 영역 사용
- 여러 text bbox를 x 좌표 순으로 결합할 수 있는지 확인

이 작업에서 복잡한 NLP 모델까지 도입할 필요는 없다.

---

## 7. 평가 지표

### Anchor

- [ ] 라벨 검출 성공률

### ROI

- [ ] GT value bbox가 생성한 ROI 안에 포함되는 비율
- [ ] ROI Coverage Rate

### 필드

- [ ] Exact Match
- [ ] Field Accuracy

### 속도

- [ ] sec/image

가능하면 다음 비교표를 만든다.

| 필드 | Anchor 성공 | GT 값 포함 | Prediction | GT | Exact Match |
|---|---|---|---|---|---|
| 보증금 |  |  |  |  |  |

---

## 8. 핵심 비교 실험

Anchor-ROI의 의미를 보기 위해 최소 다음 두 방법을 비교한다.

```text
A. Cell 기반
Cell Detection -> Cell Mapping -> OCR -> Field

B. Anchor 기반
Full OCR -> Anchor Detection -> Relative ROI -> Field
```

비교:
- Field Accuracy
- 실패 유형
- 처리 시간
- 전체 표 구조가 무너진 문서에서도 추출 가능한지

셀 검출 결과 자체는 다른 담당자가 제공한 것을 사용한다.

---

## 9. 실패 사례 분류

최소 다음 유형을 기록한다.

- Anchor OCR 실패
- Anchor는 찾았으나 값이 ROI 밖에 있음
- ROI 안에 후보 텍스트가 너무 많음
- 같은 라벨이 여러 번 등장함
- 촬영/스캔 변형으로 상대 위치가 달라짐
- 병합 셀 때문에 라벨-값 거리가 크게 달라짐

이 실패 사례는 향후 Anchor-ROI 적용 범위를 정하는 데 중요하다.

---

## 10. 다른 담당자와 겹치지 않는 범위

### 하지 않을 것

- OpenCV line/grid 알고리즘 구현
- Morphology vs Contour 성능 비교
- merged cell bbox reconstruction
- TATR / PP-Structure 실험
- OCR 엔진 성능 자체 비교

### 받아서 사용할 것

- 전체 OCR text + bbox
- 공통 Ground Truth
- 다른 팀원의 Cell/ROI 결과

즉, 이 담당자는 **라벨과 값의 공간 관계를 이용해 핵심 필드를 매핑하는 로직**에만 집중한다.

---

## 11. 1차 완료 기준

- [ ] 핵심 필드 5개 Anchor 정의
- [ ] OCR 결과에서 Anchor 탐색 구현
- [ ] 상대 ROI 규칙 구현
- [ ] ROI Coverage Rate 계산
- [ ] Field Exact Match / Accuracy 계산
- [ ] 최소 10장 테스트
- [ ] 대표 실패 사례 3종 이상 저장
- [ ] Cell 기반 방식과 간단 비교표 작성

---

## 최종 산출물

이 작업이 끝나면 다음 질문에 답할 수 있어야 한다.

> 전체 Table Structure를 정확히 복원하지 못하더라도, 라벨의 위치 관계만으로 핵심 필드를 충분히 안정적으로 추출할 수 있는가?
