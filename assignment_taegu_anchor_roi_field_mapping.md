# taegu 작업 배정 — Anchor-ROI / Field Mapping 완성

> 배정일: 2026-09-22
> 1차 마감: 2026-10-02
> 최종 담당 결과 마감: 2026-10-06

## 1. 현재까지 진행된 내용

현재 `taegu` 브랜치에는 다음 구현이 존재한다.

- `anchor_field_mapper.py`
- `evaluate_fields.py`
- `evaluate_roi_coverage.py`
- `field_gt.json`
- field mapping 결과 JSON

따라서 이 담당은 기존 구현을 이어서 **Anchor 기반 핵심 필드 추출을 정량 평가 가능한 수준까지 완성**한다.

---

## 2. 담당 목표

> 전체 표 구조를 완전히 복원하지 않고도 핵심 라벨의 위치 관계를 이용해 값 ROI를 만들고, 최종 Field Accuracy까지 계산한다.

---

## 3. 10/02까지 반드시 완료할 1차 산출물

- [ ] 핵심 필드 5종 Anchor 규칙 확정
  - 소재지
  - 보증금
  - 계약금
  - 임대인 성명
  - 임차인 성명
- [ ] Anchor Detection Success Rate 계산
- [ ] ROI Coverage Rate 계산
- [ ] Field Exact Match 계산
- [ ] Field Accuracy 계산
- [ ] 금액 / 성명 / 주소 최소 후처리 규칙 적용
- [ ] 대표 실패 사례 저장

---

## 4. 10/06까지 최종 마감

- [ ] Cell 기반 방식과 Anchor 기반 방식 비교표 작성
- [ ] 최소 10장 기준 결과 정리
- [ ] Field Mapping 결과 JSON 형식 고정
- [ ] 성공/실패 사례 유형화
- [ ] 추가 인원 B가 통합 Pipeline에서 호출할 수 있도록 입력/출력 규격 정리

---

## 5. 다른 담당자와의 경계

### 하지 않을 것

- OpenCV line/grid 알고리즘 구현
- Morphology vs Contour 비교
- TATR / PP-Structure 비교
- OCR 엔진 자체 성능 비교
- 서버 환경 구성

### 받아서 사용할 것

- 전체 OCR text + bbox
- 공통 Ground Truth
- 필요 시 다른 담당자의 Cell/ROI 결과

### 넘겨줄 대상

- 추가 인원 A: 필요 시 필드별 ROI 참고
- 추가 인원 B: 최종 Field Mapping 모듈 및 결과 포맷

---

## 6. 완료 기준

이 작업이 끝나면 다음 질문에 답할 수 있어야 한다.

> 전체 Table Structure를 완전히 복원하지 않아도 Anchor-ROI만으로 핵심 필드를 안정적으로 추출할 수 있는가?
