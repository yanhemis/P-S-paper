# 연구 방향성 · 가설 · 다음 작업 통합 문서

> 마지막 업데이트: 2026-10-21
> 상태: 연구축 동결, 데이터 보강 + 최종 평가 단계

## 1. 논문 중심 주제

**정형 임대차계약서 핵심정보 추출 파이프라인의 단계별 오류 전파 분석: 이미지 품질, 구조 복원, ROI 설정, 문자 인식을 중심으로**

본 연구는 새 OCR 모델을 제안하는 것이 아니라, 동일/유사 양식의 소규모 임대차계약서 환경에서 다음 단계의 오류가 최종 Field Accuracy에 어떻게 전달되는지 분석한다.

```text
입력 이미지
  -> 이미지 품질 / 전처리
  -> 문서 구조 복원
  -> 필드 ROI 설정
  -> OCR 문자 인식
  -> 정규화 / 검증
  -> 최종 Field Accuracy
```

## 2. 연구 질문

### RQ1. 이미지 품질
거리, 원근, 조명, 접힘/가장자리 문제가 OCR과 Field Accuracy에 어떤 영향을 주는가?

### RQ2. 구조 복원
PP-Structure, TATR, OpenCV 등 구조 복원 방식의 localization 오류가 이후 필드 추출에 어떤 영향을 주는가?

### RQ3. ROI 설정
Full OCR, GT ROI OCR, Detected ROI OCR 사이에서 Field Accuracy와 CER이 어떻게 달라지는가?

### RQ4. 최종 병목
구조/ROI 오류를 통제한 뒤 남는 병목은 localization인가 recognition인가?

Anchor-ROI는 RQ3의 대안 방식이며, 충분한 정량 결과가 없으면 PoC로 유지한다.

## 3. 현재까지 확인된 핵심 결과

기존 공통 10장, 49개 평가 필드 기준 주요 결과:

```text
P0 Raw Full OCR                29/49 (59.2%)
P1 Corrected Full OCR          31/49 (63.3%)
P2 GT ROI OCR                  31/49 (63.3%)
P3 Detected ROI OCR (pad 25%)  13/49 (26.5%)
```

현재 P3 성능 저하의 주요 원인은 OCR 자체보다 ROI 누락/coverage 부족으로 관찰된다. 또한 P1과 P2가 같은 Field Accuracy를 보여 ROI 이득을 순수 localization 효과로만 해석하면 안 된다.

OpenCV 구조 평가는 Affine 좌표 감사 후 재평가됐지만 단일 이미지/지정 영역 결과이므로 일반화하지 않는다.

## 4. 최종 실험 축

- E0: Raw Full OCR
- E1: Image-corrected Full OCR
- E2: Structure Recovery Evaluation
- E3: GT ROI OCR
- E4: Detected ROI OCR
- E5: Anchor ROI OCR (가능 시)
- E6: 최소 End-to-End 재현

최종 비교표:

| Pipeline | ROI source | ROI Coverage | Field Accuracy | CER | 비고 |
|---|---|---:|---:|---:|---|
| P0 | Full page | - | 확정값 | 확정값 | baseline |
| P1 | Full page | - | 확정값 | 확정값 | image correction |
| P2 | GT ROI | 100% | 확정값 | 확정값 | oracle |
| P3 | bang Detected ROI | 확정값 | 확정값 | 확정값 | 실제 자동 ROI |
| P4 | taegu Anchor ROI | 가능 시 | 가능 시 | 가능 시 | 보조 비교 |

## 5. 2026-10-21 역할 재편

실제 진행 상황을 반영해 **핵심 3명 + 데이터/GT 3명**으로 운영한다.

### 핵심 3명

- `bang_`: 구조 복원/Detected ROI, 동결 설정으로 전체 batch
- `taegu`: Anchor Field ROI + 최소 End-to-End
- `dahye_cell_DetectionSurvey`: 최종 평가 총괄 / Evaluation Gatekeeper

### 데이터/GT 3명

- `heewon`: 정상/통제 촬영 데이터
- `tail`: 난이도 촬영 + 이미지 품질 메타데이터
- 추가 인원 B: 핵심 5필드 GT + manifest + Dataset v1.0 관리

세부 작업은 `03_team_execution_plan_20261021.md`를 따른다.

## 6. 데이터 보강 계획

기존 공통 10장은 이미 개발/분석에 사용됐으므로 untouched holdout이 아니다.

권장 목표:

```text
기존 10장
+ 신규 usable 10~15장
= 총 20~25장 수준
```

신규 데이터는 최소 2~3개 원본 문서 그룹을 사용하고, 동일 문서를 다른 촬영 조건으로 반복 촬영할 수 있다. 단 동일 원본 문서의 반복 촬영은 같은 `document_group_id`로 묶는다.

필수 요소:
- 촬영 조건 manifest
- 핵심 5필드 text GT
- document_group_id
- development / holdout_test split

분할은 반드시 document_group_id 단위로 한다. 자세한 규칙은 `04_data_collection_gt_protocol.md`를 따른다.

## 7. 평가 원칙

- ROI가 생성되지 않은 필드는 end-to-end Field Accuracy에서 실패로 계산한다.
- ROI Coverage와 ROI가 존재할 때의 OCR 정확도를 분리해서 본다.
- 좌표계가 다른 prediction/GT를 섞지 않는다.
- 이미지 수, 원본 문서 그룹 수, field instance 수를 구분해 보고한다.
- 같은 이미지에서 나온 여러 field를 독립 문서 표본처럼 해석하지 않는다.
- holdout 결과를 보고 튜닝하면 해당 결과는 더 이상 untouched final test가 아니다.

## 8. 최종 해석 범위

본 논문은 다음을 주장하지 않는다.

- ROI가 항상 Full OCR보다 우수하다.
- OpenCV가 모든 구조 모델보다 우수하다.
- 20~25장의 결과가 모든 임대차계약서에 일반화된다.

대신 다음을 보여주는 것이 목표다.

> 동일/유사한 정형 임대차계약서의 제한된 데이터에서 이미지 품질, 구조 복원, ROI localization, OCR recognition의 오류가 최종 필드 추출 성능에 어떤 방식으로 전달되는지를 단계별로 정량 분석한다.
