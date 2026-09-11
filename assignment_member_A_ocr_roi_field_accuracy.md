# 추가 인원 A 작업 배정 — OCR / ROI 재인식 / Field Accuracy

> 배정일: 2026-09-11

## 이 문서의 역할

이 파일은 현재 별도 작업이 없는 추가 인원 A에게 배정할 **OCR baseline과 ROI 재인식 효과 검증 작업만** 정리한다.

셀 검출 알고리즘 개발, TATR/PP-Structure 구조 비교, 병합 셀 재구성은 다른 담당자의 범위이므로 여기서는 하지 않는다.

---

## 1. 담당 목표

다음 질문에 답하는 것이 핵심이다.

> **전체 페이지 OCR보다 핵심 필드 ROI를 잘라 다시 OCR했을 때 실제 문자 인식과 Field Accuracy가 좋아지는가?**

이 작업은 연구 가설 H1과 H5를 직접 검증한다.

---

## 2. 실험 구성

### 실험 A — 전체 페이지 OCR baseline

동일 계약서 이미지에 Korean OCR을 적용한다.

저장할 정보:
- text bbox
- text
- confidence
- runtime

최소 결과 파일 예시:

```text
results/full_ocr/sample_01/
  text_bbox.jpg
  ocr.json
  metrics.json
```

---

### 실험 B — Ground Truth ROI OCR

정답 ROI를 직접 crop해서 OCR한다.

목적:
- Cell Detection 오류를 제외했을 때 ROI OCR이 낼 수 있는 성능 상한선 확인

비교 대상:
- 전체 OCR 결과에서 해당 필드 값
- GT ROI crop 후 OCR 값

---

### 실험 C — 실제 검출 ROI OCR

`bang_`, `heewon` 또는 최종 Cell/ROI Detection 결과를 받아 동일하게 OCR한다.

목적:
- 이상적인 GT ROI가 아니라 실제 자동 검출 ROI에서 개선 효과가 유지되는지 확인

이 단계에서는 ROI 생성 알고리즘을 직접 수정하지 않는다. 받은 bbox를 입력으로 사용한다.

---

## 3. 우선 평가 필드

최소 5개부터 시작한다.

- [ ] 소재지
- [ ] 보증금
- [ ] 계약금
- [ ] 임대인 성명
- [ ] 임차인 성명

여유가 있으면 추가:
- 잔금
- 계약기간

---

## 4. 평가 지표

### OCR 단위

- [ ] CER
- [ ] Exact Match
- [ ] confidence

### 필드 단위

- [ ] Field Accuracy
- [ ] 필드별 성공/실패 건수

### 성능

- [ ] sec/image
- [ ] ROI별 평균 처리 시간

결과 비교 예시:

| 필드 | Full OCR | GT ROI OCR | Detected ROI OCR | GT | 정답 여부 |
|---|---|---|---|---|---|
| 보증금 |  |  |  |  |  |

---

## 5. Text bbox 안정성 보조 실험

가능하면 H1 검증을 위해 같은 문서를 다음 조건으로 비교한다.

- 원본
- grayscale
- threshold 또는 contrast enhancement

확인:
- 라벨 bbox가 유지되는지
- 값 bbox가 쪼개지거나 합쳐지는지
- confidence가 변하는지

단, 전처리 알고리즘을 새로 연구하는 것이 목적은 아니다. **OCR 입력 조건에 따른 결과 차이를 기록하는 수준**이면 충분하다.

---

## 6. 결과 저장 권장 형식

```json
{
  "image": "sample_01.jpg",
  "field": "보증금",
  "ground_truth": "100000000",
  "full_ocr": {
    "prediction": "",
    "confidence": 0.0,
    "correct": false
  },
  "gt_roi_ocr": {
    "prediction": "",
    "confidence": 0.0,
    "correct": false
  },
  "detected_roi_ocr": {
    "prediction": "",
    "confidence": 0.0,
    "correct": false
  }
}
```

---

## 7. 다른 담당자와 겹치지 않는 범위

### 하지 않을 것

- TATR cell reconstruction 수정
- PP-Structure 모델 조사
- Morphology/Contour 셀 검출 알고리즘 개발
- 병합 셀 bbox 생성 로직 개발
- Anchor 위치 규칙 설계

### 받아서 사용할 것

- 공통 Ground Truth
- 기존 팀원이 만든 ROI bbox
- 공통 evaluator 포맷

즉, 이 담당자는 **검출된 ROI 이후 OCR 성능이 어떻게 변하는지**만 책임진다.

---

## 8. 1차 완료 기준

- [ ] 동일 계약서 최소 10장
- [ ] 핵심 필드 최소 5종
- [ ] Full OCR 결과 저장
- [ ] GT ROI OCR 결과 저장
- [ ] 실제 검출 ROI OCR 결과 저장
- [ ] CER / Exact Match / confidence 비교
- [ ] Field Accuracy 표 작성
- [ ] 대표 성공/실패 사례 3개 이상 저장

---

## 최종 산출물

이 작업이 끝나면 다음 문장을 실험으로 판단할 수 있어야 한다.

> ROI를 정확히 특정하는 것이 실제 OCR 및 핵심 필드 추출 정확도 개선으로 이어지는가?
