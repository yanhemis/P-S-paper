# heewon 최종 작업 — 구조 입력 방식 보조 실험 및 오류 유형 정리

> 재설정일: 2026-10-08
> 내부 마감: 2026-10-10

## 담당 목표

Morphological Opening vs Contour 비교를 **새로 확장하지 않고**, 현재 결과를 구조 복원 단계의 보조 근거와 실패 유형 분석으로 정리한다.

## 해야 할 일

- [ ] 기존 Morphology / Contour 결과표 정리
- [ ] 각 방식의 best setting 명시
- [ ] kernel/filter sensitivity 핵심 결과 요약
- [ ] 끊어진 선, 흐린 선, 표선-글자 간섭 등 실패 유형 정리
- [ ] 가능하면 best setting의 bbox를 machine-readable JSON으로 export
- [ ] JSON export가 즉시 어렵다면 기존 수치/시각화만 논문 보조 실험으로 정리
- [ ] 현재 실제 구현 기준 Pipeline / Sequence 흐름 그림 현행화

## 논문에서의 위치

이 담당 결과는 최종 Field Accuracy의 직접 핵심 비교라기보다,

> OpenCV 구조 복원에서 어떤 입력 검출 방식이 선택되었고 어떤 실패 유형이 있었는가

를 설명하는 보조 실험으로 사용한다.

## 하지 않을 것

- 새로운 검출 방법 추가
- 새로운 Cell Detector 학습
- 대규모 파라미터 탐색 재실행

## 완료 기준

현재 보유한 결과가 논문 Method/Discussion에서 재사용 가능한 표·그림·오류 유형으로 정리되어 있어야 한다.
