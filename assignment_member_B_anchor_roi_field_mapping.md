# 추가 인원 B 작업 배정 — 서버 통합 / 의존성 / End-to-End 실행

> 재배정일: 2026-09-22
> 조기 체크: 2026-09-25
> 최종 담당 결과 마감: 2026-10-10

## 1. 역할 변경 사유

기존 Anchor-ROI / Field Mapping 역할은 현재 `taegu` 브랜치에서 실제 구현이 진행 중이므로 중복된다.

따라서 이 담당은 **서버 실행 환경 정리와 전체 Pipeline 통합**으로 역할을 변경한다.

---

## 2. 담당 목표

> 각 담당자가 만든 모듈과 결과를 서버에서 재현 가능하게 실행할 수 있도록 의존성, 실행 순서, 입력/출력 규격을 정리하고 최소 End-to-End 흐름을 완성한다.

---

## 3. 09/25 조기 체크

- [ ] `dev/requirements.txt` 확인
- [ ] 각 브랜치 실제 import 목록 확인
- [ ] 직접 사용하는 패키지와 하위 의존성 구분
- [ ] PaddleOCR / PaddlePaddle / Torch / Transformers / LayoutParser 사용 여부 확인
- [ ] Python 버전 조건 초안 작성
- [ ] GPU 사용 시 CUDA / Paddle / Torch 호환성 확인 항목 정리

이 단계에서는 완벽한 requirements가 아니라 **서버에 무엇을 설치해야 하는지 빠짐없이 파악하는 것**이 목표다.

---

## 4. 10/04까지 통합 시작 준비

- [ ] 담당자별 출력 포맷 수집
- [ ] Cell/ROI JSON 입력 형식 확인
- [ ] OCR 결과 JSON 형식 확인
- [ ] Anchor/Field Mapping 입출력 확인
- [ ] 공통 경로/파일명 규칙 제안
- [ ] 각 모듈 실행 순서 문서화

권장 흐름:

```text
input image
  -> preprocessing / cell-roi detection
  -> OCR or ROI OCR
  -> field mapping / postprocess
  -> evaluation or final JSON
```

---

## 5. 10/10까지 최종 마감

- [ ] 최종 `requirements.txt` 또는 환경 설치 문서 작성
- [ ] CPU / GPU 설치 차이 정리
- [ ] 깨끗한 환경에서 설치 테스트
- [ ] 최소 End-to-End 실행 스크립트 또는 entry point 작성
- [ ] 입력 이미지 1장 이상 전체 흐름 실행
- [ ] 최종 Field 결과 JSON 생성 확인
- [ ] 서버에서 불필요한 GUI 의존성 분리 여부 확인
- [ ] 실행 오류 / 환경 이슈 목록 작성
- [ ] README 또는 실행 문서 작성

---

## 6. 다른 담당자와의 경계

### 하지 않을 것

- 새로운 Cell Detection 알고리즘 개발
- TATR / PP-Structure 성능 연구
- Anchor 규칙 설계
- OCR 모델 정확도 연구

### 받아서 사용할 것

- `bang_`: Cell/ROI 결과와 실행 방법
- `dahye`: 구조 모델 의존성 및 evaluator
- `heewon`: 최신 Pipeline / Sequence 흐름
- `taegu`: Field Mapping 모듈과 입출력
- 추가 인원 A: OCR/ROI 재인식 모듈과 결과 포맷

### 넘겨줄 결과

- 팀 전체가 사용할 서버 설치 방법
- 최종 requirements
- End-to-End 실행 순서/스크립트

---

## 7. 완료 기준

이 작업이 끝나면 다음 질문에 답할 수 있어야 한다.

> 새로운 서버/환경에서 저장소를 받아 필요한 패키지를 설치하고, 입력 이미지부터 최종 Field 결과까지 재현 가능한가?
