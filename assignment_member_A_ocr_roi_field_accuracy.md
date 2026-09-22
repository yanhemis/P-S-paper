# tail 작업 배정 — OCR / ROI 재인식 / Field Accuracy

> 재배정일: 2026-09-22
> 조기 체크: 2026-09-25
> 최종 담당 결과 마감: 2026-10-07

## 1. 담당 목표

다음 질문에 답하는 것이 핵심이다.

> **전체 페이지 OCR보다 핵심 필드 ROI를 잘라 다시 OCR했을 때 실제 문자 인식과 Field Accuracy가 좋아지는가?**

이 작업은 연구 가설 H1과 H5를 직접 검증한다.

---

## 2. 09/25 조기 체크

- [ ] 전체 페이지 Korean OCR baseline 실행 성공
- [ ] OCR 결과 JSON 저장
- [ ] text bbox / text / confidence / runtime 저장
- [ ] 최소 1장 이상 결과 시각화 또는 확인 가능한 출력 생성

이 단계에서 OCR baseline이 실제로 돌아가는지 먼저 확인한다.

---

## 3. 실험 구성

### 실험 A — 전체 페이지 OCR baseline

동일 계약서 이미지에 Korean OCR을 적용한다.

저장할 정보:
- text bbox
- text
- confidence
- runtime

### 실험 B — Ground Truth ROI OCR

정답 ROI를 직접 crop해서 OCR한다.

목적:
- Cell Detection 오류를 제외했을 때 ROI OCR이 낼 수 있는 성능 상한선 확인

### 실험 C — 실제 검출 ROI OCR

`bang_`, `heewon` 또는 최종 Cell/ROI Detection 결과를 받아 동일하게 OCR한다.

목적:
- 자동 검출 ROI에서도 개선 효과가 유지되는지 확인

이 단계에서는 ROI 생성 알고리즘을 직접 수정하지 않는다. 받은 bbox를 입력으로 사용한다.

---

## 4. 우선 평가 필드

최소 5개부터 시작한다.

- [ ] 소재지
- [ ] 보증금
- [ ] 계약금
- [ ] 임대인 성명
- [ ] 임차인 성명

여유가 있으면:
- 잔금
- 계약기간

---

## 5. 평가 지표

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

핵심 비교:

```text
Full OCR
vs
GT ROI OCR
vs
Detected ROI OCR
```

---

## 6. 10/07까지 최종 마감

- [ ] 동일/유사 계약서 최소 10장
- [ ] 핵심 필드 최소 5종
- [ ] Full OCR 결과 저장
- [ ] GT ROI OCR 결과 저장
- [ ] 실제 검출 ROI OCR 결과 저장
- [ ] CER / Exact Match / confidence 비교
- [ ] Field Accuracy 표 작성
- [ ] sec/image 기록
- [ ] 대표 성공/실패 사례 3개 이상 저장
- [ ] `bang_`에서 받은 ROI 결과 반영
- [ ] 추가 인원 B에게 통합 가능한 OCR 입력/출력 규격 전달

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
- `bang_` 또는 최종 팀 Cell/ROI bbox
- 공통 evaluator 포맷

### 넘겨줄 대상

- 추가 인원 B: OCR/ROI 재인식 모듈 및 결과 포맷

---

## 최종 산출물

이 작업이 끝나면 다음 문장을 실험으로 판단할 수 있어야 한다.

> ROI를 정확히 특정하는 것이 실제 OCR 및 핵심 필드 추출 정확도 개선으로 이어지는가?
