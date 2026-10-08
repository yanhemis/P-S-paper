# 추가 인원 B 최종 작업 — End-to-End 통합 / 재현성 / 보조 품질검증

> 재설정일: 2026-10-08
> 내부 마감: 2026-10-10

## 담당 목표

각 담당자가 만든 결과를 실제 실행 가능한 하나의 흐름으로 연결하고, clean environment에서 재현 가능한 최소 End-to-End 경로를 완성한다.

## 최소 연결 경로

```text
input image
  -> image correction / structure or field ROI
  -> OCR
  -> normalization
  -> final_fields.json
```

## 해야 할 일

- [ ] 각 브랜치 실제 import/requirements 확인
- [ ] Python 버전 및 CPU/GPU 조건 정리
- [ ] `bang_` Cell/ROI 입력 규격 확인
- [ ] `taegu` Field ROI 입력/출력 규격 확인
- [ ] `tail` OCR 입력/출력 규격 확인
- [ ] 최소 하나의 최종 pipeline entry point 작성
- [ ] 입력 이미지 1장 이상 End-to-End 실행
- [ ] `final_fields.json` 생성 확인
- [ ] 실행 순서와 오류 처리 README 작성
- [ ] clean environment 설치/실행 문제 기록

## Guardrail 처리

이미 구현된 OCR Guardrail은 시간이 허용되면 실제 OCR 결과에 연결하여 PASS / RECHECK / BLOCK의 **보조 품질검증 예시**로 사용한다.

단,
- threshold 최적화 연구
- 새로운 risk model 개발
- 별도 성능 논문 축 확장

은 하지 않는다.

## 하지 않을 것

- 새 Cell Detection 알고리즘 개발
- Anchor 규칙 개발
- OCR 모델 성능 연구
- 새로운 모델 추가

## 완료 기준

새 환경에서 저장소와 입력 이미지를 받아 정해진 실행 순서대로 수행했을 때 최종 필드 JSON까지 재현할 수 있어야 한다.
