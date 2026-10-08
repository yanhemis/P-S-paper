# 연구 방향성 · 가설 · 다음 작업 통합 문서

> 마지막 업데이트: 2026-10-08
> 상태: 논문 중심축 재설정 및 최종 실험 단계 진입

## 1. 개정된 논문 주제

**정형 임대차계약서 핵심정보 추출 파이프라인의 단계별 오류 전파 분석: 이미지 품질, 구조 복원, ROI 설정, 문자 인식을 중심으로**

기존 연구에서는 ROI 재인식을 주요 개선 수단으로 보았으나, 현재 실험에서는 GT ROI OCR의 개선 폭이 제한적이고 원근 보정만으로도 유사한 수준의 개선이 관찰되었다. 따라서 이제 ROI 자체의 우수성을 전제로 하지 않고, 각 단계가 최종 Field Accuracy에 미치는 영향을 통제 실험으로 분리한다.

핵심 흐름:

```text
입력 이미지
  -> 이미지 품질 / 전처리
  -> 문서 구조 복원
  -> 필드 ROI 설정
  -> OCR 문자 인식
  -> 정규화 / 검증
  -> 최종 Field Accuracy
```

본 연구의 핵심 기여는 새로운 OCR 모델 제안이 아니라 **같은 데이터와 Ground Truth에서 각 단계의 오류를 하나씩 분리하고, 최종 필드 추출 성능에 미치는 영향을 정량적으로 귀속하는 것**이다.

---

## 2. 최종 연구 질문

### RQ1. 이미지 품질
촬영 거리, 원근 왜곡, 접힘, 가장자리 누락, 유효 해상도 등 이미지 품질 차이가 OCR과 최종 Field Accuracy에 어느 정도 영향을 주는가?

### RQ2. 구조 복원
PP-Structure, TATR, OpenCV 등 구조 복원 방식의 Cell/ROI localization 오류가 이후 핵심 필드 추출에 어떤 영향을 주는가?

### RQ3. ROI 설정
Full OCR, GT ROI OCR, 실제 검출 ROI OCR 사이에서 Field Accuracy와 CER이 어떻게 변하며, ROI가 해결하는 오류와 해결하지 못하는 오류는 무엇인가?

### RQ4. 최종 병목
구조와 ROI 오류를 통제한 이후에도 남는 오류는 어디에서 발생하며, 현재 데이터에서 최종 성능의 주요 병목은 구조/ROI인가 문자 Recognition인가?

Anchor-ROI는 RQ3의 대안적 ROI 생성 방법으로 평가하며, 10장 정량평가가 완료되지 않으면 PoC 수준으로 보고한다.

---

## 3. 현재까지 확인된 핵심 결과

### 이미지 품질
- 동일/유사 양식 10장에 대해 Full OCR, GT ROI OCR, 이미지 품질 분석이 진행되었다.
- 품질이 좋은 촬영본에서는 인쇄 한글 재현율이 높고, 거리/접힘/가장자리 문제가 있는 이미지에서 재현율 저하가 관찰되었다.
- H1은 현재 데이터에서 지지되는 방향이다.

### ROI 재인식
현재 확보된 49개 평가 필드 기준:

```text
Full OCR Field Accuracy: 29/49 (59.2%)
GT ROI OCR Field Accuracy: 31/49 (63.3%)
평균 CER: 0.141 -> 0.117
```

ROI 개선은 존재하지만 크지 않다. 또한 원근 보정된 전체 이미지 OCR에서도 유사한 Field Accuracy가 관찰되어, ROI의 이득 중 일부는 해상도/문서 보정 효과와 구분할 필요가 있다.

### 구조 복원
OpenCV 기반 grid + merged reconstruction은 실제 cells JSON, 원본 좌표 JSON, report, 시각화까지 생성 가능한 상태다.

다만 현재 구조 비교표에서는 좌표계가 다른 OpenCV aligned 좌표와 원본 GT가 함께 평가된 흔적이 있으므로 **최종 수치 확정 전 original-coordinate prediction으로 재평가가 필수**다.

PP-Structure/TATR의 낮은 IoU 결과도 같은 표 영역/좌표계가 맞는지 overlay 확인 후 해석한다.

### Anchor-ROI
현재 공통 sample 수준의 PoC는 있으나 일부 금액 ROI가 여러 행에 걸쳐 다른 값이 섞이는 문제가 있다. 10장 정량평가가 완료되지 않으면 최종 핵심 결과로 확대하지 않는다.

---

## 4. 최종 실험 단계

### E0 — Raw Full OCR Baseline
목적: 아무 단계도 통제하지 않은 현실 baseline.

지표:
- CER
- Exact Match
- confidence
- Field Accuracy
- sec/image

### E1 — Image-corrected Full OCR
목적: ROI를 사용하지 않고 이미지 품질/원근 보정 효과만 분리.

비교:
```text
Raw Full OCR vs Corrected Full OCR
```

### E2 — Structure Recovery Evaluation
목적: 구조 복원 단계 자체의 localization 성능 확인.

대상:
- PP-Structure
- TATR Grid
- TATR + Spanning
- OpenCV Grid
- OpenCV + Merged Reconstruction
- heewon 방식은 machine-readable 결과가 즉시 가능할 때 보조 비교

필수 조건:
- 같은 원본 이미지 좌표계
- Exhaustive GT
- 1:1 matching

지표:
- IoU 0.3 / 0.5 / 0.7
- Precision / Recall / F1
- General GT localization recall
- Merged GT localization recall

### E3 — Oracle ROI OCR
목적: 구조/ROI 오류를 제거했을 때 OCR Recognition의 상한선과 잔여 오류 확인.

```text
GT ROI -> OCR -> Field Accuracy
```

### E4 — Detected ROI OCR
목적: 실제 자동 Cell/Field ROI에서 개선 효과가 유지되는지 확인.

```text
자동 구조/ROI -> ROI OCR -> Field Accuracy
```

E3와 E4 차이가 크면 ROI localization이 병목이고, 차이가 작으면서 둘 다 낮으면 Recognition이 병목이라는 해석이 가능하다.

### E5 — Anchor-ROI OCR
목적: 전체 표 복원을 우회하는 필드 ROI 방식의 가능성 확인.

- 10장 결과가 10/10까지 나오면 정량 비교
- 아니면 공통 sample PoC 및 실패 사례만 보고

### E6 — End-to-End 재현
목적: 최종 선택 경로가 실제 서버/환경에서 재현되는지 확인.

최소 흐름:
```text
input image
  -> image correction / structure or field ROI
  -> OCR
  -> normalization
  -> final_fields.json
```

이미 구현된 Guardrail은 E6의 보조 검증으로만 사용하며 논문의 새 핵심 주장으로 확장하지 않는다.

---

## 5. 공통 평가 기준

### 이미지 품질 단계
- 인쇄 한글 재현율
- CER
- Field Accuracy 변화량

### 구조 단계
- Cell IoU
- Precision / Recall / F1
- General/Merged GT localization recall

### ROI 단계
- ROI Coverage Rate
- 가능하면 ROI IoU
- 필드 ROI 성공/실패 건수

### 문자 인식 단계
- CER
- Exact Match
- confidence
- 필드별 성공/실패 유형

### 최종 성능
- Field Accuracy
- 필드별 Accuracy
- sec/image

모든 결과는 가능하면 동일한 10장 데이터와 동일한 field GT를 사용한다.

---

## 6. 최종 논문에서 만들어야 할 핵심 표

최종적으로 다음 형태의 표가 하나 있어야 한다.

| Pipeline | Image correction | Structure/ROI | OCR condition | Field Accuracy | CER | 비고 |
|---|---|---|---|---:|---:|---|
| P0 | X | Full page | Full OCR | 확정값 | 확정값 | baseline |
| P1 | O | Full page | Full OCR | 확정값 | 확정값 | 이미지 품질 효과 |
| P2 | O/동일 | GT ROI | ROI OCR | 확정값 | 확정값 | oracle ROI |
| P3 | O/동일 | Detected ROI | ROI OCR | 확정값 | 확정값 | 실제 자동 ROI |
| P4 | O/동일 | Anchor ROI | ROI OCR | 가능 시 | 가능 시 | 보조 비교 |

이 표와 구조 복원 비교표가 논문의 핵심 정량 결과가 된다.

---

## 7. 역할 재설정 — 2026-10-08

### `bang_` — 자동 구조 복원 결과 공급
- 기존 알고리즘 수정 최소화
- 공통 10장에 batch 실행
- `cells_original.json` 중심으로 전달
- 원본 좌표/보정 좌표 혼동 방지
- 성공/실패 사례 및 report 전달

### `dahye_cell_DetectionSurvey` — 공통 구조 평가 감사자
- OpenCV 평가를 original-coordinate prediction으로 재실행
- PP/TATR 결과 overlay 확인
- 같은 표 영역/좌표계인지 검증
- 최종 Structure Recovery 비교표 확정
- 지표 이름과 해석 정리

### `heewon` — 구조 입력 방식 보조 실험 + 오류 유형 정리
- Morphology vs Contour 기존 결과를 신규 구현 없이 정리
- 즉시 가능하면 best setting bbox JSON export
- 공통 평가 연결이 어렵다면 기존 결과를 구조 방식 선정 근거/실패 taxonomy로 정리
- 단계별 오류 흐름 그림/Pipeline 현행화

### `taegu` — Field ROI Localization
- 핵심 5개 필드의 ROI 생성 규칙 고정
- 가능한 경우 공통 10장에 ROI 출력
- ROI Coverage / 실패 유형 정리
- 금액 ROI의 행 간 혼입 문제 수정은 최소 범위에서만 수행
- 10장 완료 불가 시 Anchor-ROI를 PoC로 명확히 축소

### `tail` — 이미지 품질 + OCR + 최종 Field Accuracy
- 기존 E0/E1/E3 결과 확정
- `bang_`/`taegu` 결과를 받아 E4/E5 OCR 실행
- 모든 pipeline의 Field Accuracy/CER를 같은 규칙으로 계산
- 단계별 성능 변화표 작성
- Recognition 잔여 오류 분석

### 추가 인원 B — End-to-End 통합 + 보조 품질검증
- 각 담당 모듈의 입출력 연결
- clean environment/requirements 확인
- 입력 이미지 -> final_fields.json 최소 경로 완성
- 기존 OCR Guardrail이 실제 OCR 결과에 연결 가능하면 PASS/RECHECK/BLOCK 보조 분석
- Guardrail threshold 연구 확장은 하지 않음

### PM/논문 통합
- 연구 질문/주장 동결
- 서로 다른 좌표계/평가 정의 방지
- 결과표 숫자 일치 확인
- 논문 Method/Experiment/Discussion 통합

---

## 8. 남은 일정

### 10/08 — 연구 설계 동결
- 새 주제/RQ/실험축 확정
- 신규 모델/대규모 기능 추가 금지

### 10/09 — 평가 입력 확정
- OpenCV 좌표계 수정 평가
- PP/TATR overlay 확인
- 공통 10장 자동 구조/ROI 결과 최대한 확보

### 10/10 — 자동 ROI 및 End-to-End 마감
- Detected ROI 입력 확보
- Anchor 10장 가능 여부 최종 결정
- 최소 End-to-End 실행 성공

### 10/11 — 최종 정량표 확정
- 단계별 Field Accuracy 표
- Structure Recovery 표
- 실패 taxonomy
- 대표 사례 확정

### 10/12 — 논문 최종 검토
- 결과/본문 숫자 일치
- 과장된 주장 제거
- 한계/후속 연구 정리

### 10/13 — 프로젝트 최종 완료
- 코드/결과/문서 동결
- 재현 명령 확인
- 최종 논문본 정리

---

## 9. 최종 해석 원칙

본 논문은 다음을 증명하려 하지 않는다.

- ROI가 항상 Full OCR보다 우수하다.
- OpenCV가 모든 구조 모델보다 우수하다.
- 현재 10장 결과가 모든 임대차계약서에 일반화된다.

대신 다음을 실험적으로 보여주는 것이 목표다.

> 동일/유사한 정형 임대차계약서 환경에서 이미지 품질, 구조 복원, ROI 설정, 문자 인식 단계가 최종 핵심정보 추출 성능에 서로 다른 방식으로 영향을 미치며, 각 단계를 통제했을 때 실제 병목이 어디에 남는지를 정량적으로 분석할 수 있다.
