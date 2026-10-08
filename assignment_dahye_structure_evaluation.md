# dahye 최종 작업 — 공통 구조 평가 감사 및 확정

> 재설정일: 2026-10-08
> 내부 마감: 2026-10-09

## 담당 목표

구조 모델의 성능을 새로 넓히는 것이 아니라, **같은 이미지·같은 좌표계·같은 Exhaustive GT에서 구조 복원 성능을 신뢰할 수 있게 확정**한다.

## 최우선 수정

- [ ] OpenCV 평가 입력을 `cells_original.json` / `cells_primitive_original.json`으로 교체
- [ ] 원본 GT와 동일 좌표계인지 확인
- [ ] PP-Structure prediction overlay 확인
- [ ] TATR Grid / Spanning prediction overlay 확인
- [ ] 같은 표 영역을 비교하는지 확인

## 최종 평가

IoU threshold:
- 0.3
- 0.5
- 0.7

지표:
- Precision
- Recall
- F1
- General GT localization recall
- Merged GT localization recall

prediction type을 실제 클래스 정확도로 평가하지 않는다면 지표명을 `Merged Cell Accuracy`처럼 과장하지 않고 `Merged GT Localization Recall`로 표기한다.

## 최종 산출물

- [ ] 좌표계 검증된 evaluator 입력 목록
- [ ] 최종 구조 복원 비교표
- [ ] 모델별 overlay 이미지 또는 확인 기록
- [ ] 평가 불가/실행 실패와 낮은 성능을 구분한 설명
- [ ] 논문에 사용할 수 있는 해석 문장

## 하지 않을 것

- 새 구조 모델 추가
- 새 딥러닝 Cell Detector 추가
- OpenCV 알고리즘 재개발

## 완료 기준

구조 비교표의 각 숫자에 대해 **어떤 이미지, 어떤 좌표계, 어떤 GT, 어떤 prediction을 사용했는지 설명 가능**해야 한다.
