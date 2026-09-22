# bang_ 작업 배정 — OpenCV Cell/ROI 및 병합 셀 복원 마무리

> 배정일: 2026-09-22
> 1차 마감: 2026-09-30
> 최종 담당 결과 마감: 2026-10-04

## 1. 현재까지 진행된 내용

`bang_` 브랜치에서 다음 단계까지 구현이 진행되었다.

- HoughLinesP 기반 deskew
- 해상도 비례 parameter scaling
- 수평/수직 line extraction
- shared boundary 판정
- Union-Find 기반 primitive cell 병합
- general / merged bbox 생성
- `cells.json` 출력 방향 구현

따라서 새로운 검출 모델을 추가하기보다 현재 구현을 실제 공통 실험 입력으로 사용할 수 있는 상태까지 마무리한다.

---

## 2. 담당 목표

> OpenCV 기반 표선/셀 검출 결과를 안정적인 Cell/ROI JSON으로 만들고, 병합 셀 복원 결과를 다른 담당자가 그대로 사용할 수 있게 한다.

이 담당은 **Cell/ROI Detection + merged reconstruction**까지만 책임진다.

---

## 3. 09/30까지 반드시 완료할 1차 산출물

- [ ] 실제 계약서 이미지에서 `cells.json` 생성
- [ ] primitive / boundary / final bbox 시각화 저장
- [ ] general / merged cell을 구분해서 저장
- [ ] 다른 담당자가 읽을 수 있도록 bbox JSON 포맷 고정
- [ ] 짧은 내부 경계 누락 사례 최소 1개 확인
- [ ] boundary 누락으로 인한 over-merge 사례 여부 확인
- [ ] 비직사각형 component 발생 여부 확인

### 최소 전달 형식 예시

```json
{
  "image": "sample_01.jpg",
  "cells": [
    {
      "bbox": [0, 0, 0, 0],
      "type": "general"
    }
  ]
}
```

정확한 키 이름은 기존 코드와 맞추되, 최종 포맷은 이후 변경하지 않는 것을 원칙으로 한다.

---

## 4. 10/04까지 최종 마감

- [ ] 공통 GT/evaluator에 넣을 수 있는 최종 prediction 파일 정리
- [ ] 대표 성공 사례 3개 이상 저장
- [ ] 대표 실패 사례 3개 이상 저장
- [ ] 주요 parameter와 실행 방법 문서화
- [ ] 추가 인원 A에게 Detected ROI OCR용 결과 전달
- [ ] 추가 인원 B에게 통합 실행에 필요한 입력/출력 규격 전달

---

## 5. 다른 담당자와의 경계

### 하지 않을 것

- TATR / PP-Structure 구조 모델 비교
- OCR 엔진 정확도 비교
- Anchor-ROI 규칙 개발
- 서버 환경 통합
- 새로운 YOLO/DETR 계열 Cell Detector 추가

### 받아서 사용할 것

- 공통 Ground Truth
- 공통 evaluator 형식
- 필요 시 heewon의 Morphology/Contour 비교 결과

### 넘겨줄 대상

- 추가 인원 A: Detected ROI OCR용 bbox
- dahye 담당: OpenCV 방식 비교용 prediction
- 추가 인원 B: End-to-End 통합용 Cell/ROI 출력

---

## 6. 완료 기준

이 작업이 끝나면 다음 질문에 답할 수 있어야 한다.

> 현재 OpenCV 방식이 실제 계약서에서 어떤 Cell/ROI를 검출했고, 병합 셀을 어디까지 안정적으로 복원했으며, 그 결과를 다음 OCR 단계에 바로 넘길 수 있는가?
