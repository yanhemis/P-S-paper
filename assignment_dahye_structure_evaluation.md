# dahye_cell_DetectionSurvey 작업 배정 — 구조 모델 비교 및 공통 Cell 평가 정리

> 배정일: 2026-09-22
> 1차 마감: 2026-09-30
> 최종 담당 결과 마감: 2026-10-05

## 1. 현재까지 진행된 내용

현재 브랜치에서 다음 작업이 진행되어 있다.

- PP-Structure / TATR / LayoutParser / SLANet 계열 조사 및 실행
- IoU threshold 0.3 / 0.5 / 0.7
- GT-Pred 1:1 Greedy Matching
- TP / FP / FN 기반 Precision / Recall / F1
- general / merged cell GT 확장
- TATR spanning-cell reconstruction
- 결과 JSON 저장 구조

따라서 남은 작업은 모델을 더 늘리는 것이 아니라, **공통 GT와 공통 형식으로 비교 가능한 정량 결과를 만드는 것**이다.

---

## 2. 담당 목표

> 구조 모델별 Cell/ROI 결과를 동일한 평가 기준으로 정리하고 OpenCV 방식과 비교 가능한 결과를 만든다.

---

## 3. 09/30까지 반드시 완료할 1차 산출물

- [ ] 평가 코드 중복 실행부 정리
- [ ] 최소 1개 이상의 구조 모델 결과를 공통 포맷으로 저장
- [ ] partial GT / exhaustive GT를 명확히 구분
- [ ] general / merged cell 평가를 분리
- [ ] IoU 0.3 / 0.5 / 0.7 결과 저장
- [ ] 공통 evaluator 실행 방법 정리

> partial GT에서 unmatched prediction이 모두 FP가 되는 경우 해당 Precision 수치는 최종 논문 성능으로 확정하지 않는다.

---

## 4. 10/05까지 최종 마감

- [ ] PP-Structure / TATR 결과를 동일 형식으로 비교
- [ ] 가능한 범위에서 exhaustive GT 또는 대표 페이지 기준 신뢰 가능한 비교 결과 확보
- [ ] OpenCV 결과를 같은 evaluator로 비교 가능하게 정리
- [ ] 모델별 성공/실패 사례 저장
- [ ] 표 형태의 정량 비교 결과 작성
- [ ] 추가 인원 B에게 실행 환경과 모델 의존성 정보 전달

---

## 5. 다른 담당자와의 경계

### 하지 않을 것

- OpenCV 병합 셀 알고리즘 재구현
- Anchor-ROI 개발
- ROI OCR 성능 비교
- 새로운 구조 모델 추가 조사에 시간 확대

### 받아서 사용할 것

- 공통 Ground Truth
- `bang_` OpenCV prediction
- 필요 시 heewon 방식별 prediction

### 넘겨줄 대상

- 팀 전체: 공통 evaluator
- bang/heewon 담당: 동일 평가 기준
- 추가 인원 B: 구조 모델 실행 의존성 및 결과 포맷

---

## 6. 완료 기준

이 작업이 끝나면 다음 질문에 답할 수 있어야 한다.

> 동일 Ground Truth에서 구조 모델과 OpenCV 방식의 Cell/ROI 결과를 같은 기준으로 비교할 수 있는가?
