# heewon 작업 배정 — Morphology vs Contour 비교 및 Pipeline 현행화

> 배정일: 2026-09-22
> 1차 마감: 2026-09-30
> 최종 담당 결과 마감: 2026-10-04

## 1. 현재까지 진행된 내용

현재 `heewon` / `Documents` 브랜치에는 Pipeline 및 Sequence Diagram이 있고, 기존 연구 방향상 Morphological Opening과 Contour 기반 검출 비교를 담당한다.

`bang_`이 최종 병합 셀 reconstruction을 맡고 있으므로 이 담당은 **입력 단계 검출 방식 비교**에 집중한다.

---

## 2. 담당 목표

> Morphology와 Contour 방식이 동일 계약서에서 어떤 차이를 보이는지 정량/정성 비교하고, 현재 실제 구현에 맞게 Pipeline 문서를 갱신한다.

---

## 3. 09/30까지 반드시 완료할 1차 산출물

- [ ] Morphological Opening 기반 line/cell 검출 실행
- [ ] Contour 기반 검출 실행
- [ ] 동일 이미지 / 동일 GT에서 결과 비교
- [ ] 주요 kernel / filter parameter 기록
- [ ] 대표 성공/실패 이미지 저장
- [ ] 표선이 흐리거나 끊긴 경우의 실패 유형 정리

---

## 4. 10/04까지 최종 마감

- [ ] 두 방식의 공통 비교표 작성
- [ ] 가능한 경우 공통 evaluator에 넣을 prediction 파일 생성
- [ ] parameter sensitivity 요약
- [ ] 현재 구현 기준으로 `PipeLine.jpg` / `Sequence Diagram.jpg` 현행화
- [ ] `bang_` 담당에게 참고할 검출 결과 전달
- [ ] 추가 인원 B에게 실제 통합 Pipeline 흐름 전달

---

## 5. 다른 담당자와의 경계

### 하지 않을 것

- Union-Find 기반 merged reconstruction 재구현
- TATR / PP-Structure 비교
- Anchor-ROI 개발
- OCR 정확도 자체 비교

### 받아서 사용할 것

- 공통 GT
- 공통 evaluator 형식

### 넘겨줄 대상

- `bang_`: 입력 검출 방식 비교 참고
- 추가 인원 B: 최신 Pipeline / Sequence 흐름

---

## 6. 완료 기준

이 작업이 끝나면 다음 질문에 답할 수 있어야 한다.

> Morphology와 Contour 중 각 방식은 어떤 조건에서 안정적이고, 어떤 조건에서 실패하며, 전체 Pipeline에서 어느 위치에 적용되는가?
