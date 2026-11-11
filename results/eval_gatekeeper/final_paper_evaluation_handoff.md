# P0~P4 최종 평가 검증 및 논문 수치 판정 보고서

- 작성일: 2026-11-12
- 담당: dahye_cell_DetectionSurvey (Evaluation Gatekeeper)
- 기준 GT: `origin/dataset-v1` / `14f240a`
- 공통 평가 코드: `e46062a`
- 문서 상태: **평가 담당자 검증 결과 제출 완료 / 논문 최종 E2E 수치 미확정**

## 1. 평가 총괄 결론

본 보고서는 P0~P4의 기존 제출물 및 Git 기록을 검증하여
평가 기준, 분모, ROI Coverage, 참고 정확도, 실패 유형,
실행 출처와 논문 사용 가능성을 정리한 최종 검증 인계 자료이다.

**확인된 수치는 보존하고, 서로 다른 실행 조건의 수치를
최종 End-to-End(E2E) 성능으로 혼합하지 않는다.**

주요 판정:

- P3 Development 19장 ROI Coverage: **36/94 (38.30%)**
- P3 Common 10장 ROI Coverage: **21/49 (42.86%)**
- P4 공식 Common 10장 ROI Coverage: **46/49 (93.88%)**
- P3 Holdout ROI Coverage: **3/30 (10.00%), 보조 검증**
- P0~P4 Common 10장 공통 정규화 정확도·CER: **참고 평가**
- 동일 조건의 최종 E2E 정확도·CER·처리 시간: **확정 보류**

위 ROI 수치는 최종 GT와 평가 범위를 명시하는 조건에서
논문 사용 후보로 분류한다.

## 2. 최종 평가 기준

### 2.1 평가 대상 필드

공통 필드는 다음 5개로 고정한다.

1. `address`
2. `deposit`
3. `contract_amount`
4. `lessor_name`
5. `lessee_name`

기존 P0~P2 자료의 필드 이름은 다음과 같이 대응한다.

| 기존 필드 | 공통 필드 |
|---|---|
| `deposit_num` | `deposit` |
| `down_payment` | `contract_amount` |

`deposit_kor`는 보조 지표로, 공식 5필드 평가에서 제외한다.

### 2.2 평가 데이터와 분모

| 구분 | 이미지 수 | 문서 그룹 수 | 평가 대상 필드 |
|---|---:|---:|---:|
| Common | 10 | 10 | 49 |
| 신규 Development | 9 | 3 | 45 |
| Development 전체 | 19 | 13 | 94 |
| Holdout 후보 | 6 | 2 | 30 |

Development에는 총 95개 필드 슬롯이 있으나,
`common_007/contract_amount`는 원본에 값이 없어
`status:not_present`로 표시된 필드이다.
따라서 해당 필드를 공식 평가 대상에서 제외하여 94개로 계산한다.

동일한 `document_group_id`의 반복 촬영 이미지는
독립적인 문서 표본으로 해석하지 않는다.

### 2.3 ROI Coverage

ROI Coverage 계산식:

`Area(GT ∩ ROI) / Area(GT)`

- 좌표계: 원본 이미지 좌표
- GT BBox: 필드 라벨이 아닌 실제 값 영역
- Covered 판정: 반올림 전 Coverage가 **0.90 이상**
- P3: 생성된 여러 ROI 후보 중 최대 Coverage
- P4: 알고리즘이 최종 선택한 ROI 1개만 평가
- 유효 GT BBox가 있지만 ROI가 없으면 Coverage 0
- `bbox:null`, `unreadable`, `not_present`는
  ROI Coverage 분모에서 제외

GT를 이용해 P3/P4의 최종 ROI를 사후 선택하지 않는다.

### 2.4 정확도와 CER

다음 지표는 구분하여 보고한다.

1. ROI Coverage
2. ROI가 존재하는 경우의 OCR 정확도
3. End-to-End Field Accuracy
4. CER
5. sec/image

ROI가 생성되지 않았거나 예측값이 없는 유효 필드는
E2E Field Accuracy의 분모에서 제거하지 않고 오답으로 처리한다.

금액 필드 정확도는 KRW 숫자 정규화 결과를 비교한다.
CER는 정답과 예측값 양쪽에 동일한 텍스트 정규화를 적용한다.
평균 Field CER는 필드별 CER의 산술평균이다.

현재 공통 평가 구현 기준은 `e46062a`이지만
팀 전체 정규화 평가 규약의 최종 동결은 별도로 확인해야 한다.

## 3. 공식 Common 10장 P0~P4 비교표

| Pipeline | 이미지 보정 | ROI 출처 | 평균 ROI Coverage | Covered / 분모 | ROI Covered 비율 |
|---|---|---|---:|---:|---:|
| P0 | X | Full page | 해당 없음 | 해당 없음 | 해당 없음 |
| P1 | O | Full page | 해당 없음 | 해당 없음 | 해당 없음 |
| P2 | 조건 고정 | GT ROI | 1.000000 | 49/49 | 100.00% |
| P3 | 조건 고정 | bang Detected ROI | 0.661941 | 21/49 | 42.86% |
| P4 | 조건 고정 | taegu Anchor ROI | 0.956120 | 46/49 | 93.88% |

P2는 GT ROI를 이용한 Oracle 기준으로,
독립적인 ROI 검출 결과가 아니다.

P3와 P4의 직접 비교는 **Common 10장, 49필드**로 제한한다.
P3는 후보 최대 Coverage, P4는 최종 선택 ROI 1개라는
평가 방식의 차이를 함께 명시해야 한다.

## 4. 신규 Development 및 전체 결과

| 구분 | Pipeline | 대상 필드 | Covered | Covered 비율 | 평균 Coverage |
|---|---|---:|---:|---:|---:|
| 신규 9장 | P3 | 45 | 15 | 33.33% | 0.511347 |
| Development 19장 | P3 | 94 | 36 | 38.30% | 0.589848 |
| 신규 9장 | P4 | 공식 범위 밖 | - | - | - |
| 별도 제출 Development 19장 | P4 | 94 | 66 | 70.21% | 0.722892 |

P4 별도 Development 19장 제출물은 참고 자료이다.
**P4 공식 평가 범위는 Common 10장으로 유지한다.**

## 5. 공통 정규화 정확도·CER 재평가

동일한 최종 GT `14f240a`와 공통 평가 코드를 적용하여
기존 제출 예측값을 재평가한 결과이다.

| Pipeline | 정답 / 대상 | Field Accuracy | 평균 Field CER |
|---|---:|---:|---:|
| P0 기존 예측 | 29/49 | 59.18% | 0.577415 |
| P1 기존 예측 | 29/49 | 59.18% | 0.555744 |
| P2 기존 예측 | 30/49 | 61.22% | 0.554512 |
| P3 과거 예측 | 12/49 | 24.49% | 1.156608 |
| P4 캐시 기반 예측 | 24/49 | 48.98% | 0.339115 |

**위 표는 공통 정규화 참고 비교이며 최종 Live-OCR E2E 표가 아니다.**

제약 사항:

- P0/P1은 기존 필드 할당 과정에 GT 위치 정보를 사용했다.
- P2는 GT ROI를 직접 사용했다.
- P3 예측값은 과거 OCR 결과이며 동결 파이프라인의
  최종 E2E 실행 결과로 확인되지 않았다.
- P4 공식 Common 10장 제출물의 OCR 출처는 `cached_ocr`이다.
- 실행 버전과 입력 조건이 모든 파이프라인에서 동일하게
  검증된 것은 아니다.

P4의 기존 Raw Exact는 **22/49 (44.90%)**이고,
이번 공통 정규화 참고 정확도는 **24/49 (48.98%)**이다.
두 수치는 서로 다른 지표이므로 구분한다.

P4 참고 평가에서 빈 예측은 12건,
유효하지 않은 금액 예측은 8건으로 집계됐다.
두 진단 건수를 서로 배타적인 오류라고 가정해 합산하지 않는다.

## 6. 최종 E2E 및 OCR 조건부 정확도 판정

| Pipeline | 최종 E2E Field Accuracy | ROI 존재 시 OCR 정확도 | 최종 E2E CER | 최종 sec/image |
|---|---|---|---|---|
| P0 | 미확정 | 미확정 | 미확정 | 미확정 |
| P1 | 미확정 | 미확정 | 미확정 | 미확정 |
| P2 | GT Oracle이므로 독립 E2E 아님 | 미확정 | 미확정 | 미확정 |
| P3 | 미확정 | 미확정 | 미확정 | 미확정 |
| P4 | 미확정 | 미확정 | 미확정 | 미확정 |

ROI Coverage가 높다는 이유만으로 OCR 정확도가 높다고 판단하지 않는다.
ROI가 있는 경우의 OCR 정확도와 전체 E2E 정확도는
별도 분모를 명시해 계산해야 한다.

현재 확인된 자료만으로 동일 조건의 최종 Live E2E 수치를
정확하게 확정할 수 없어 해당 칸을 비워 둔다.

### 6.1 과거 처리 시간 기록

| Pipeline | 기록된 sec/image | 해석 및 제한 |
|---|---:|---|
| P0 | 29.318067 | 과거 측정, 최종 E2E 동일 조건 미검증 |
| P1 | 31.126809 | 과거 측정, 최종 E2E 동일 조건 미검증 |
| P2 | 0.925516 | ROI OCR 시간 합계, ROI 검출 시간 제외 |
| P3 과거 결과 | 0.951126 | 측정 단계 및 캐시 조건 미검증 |
| P3 Development 구조 복원 | 1.178000 | 구조 복원만 측정, OCR 제외 |
| P4 | 미확정 | 공식 제출물은 캐시 OCR 기반 |

이 시간들을 최종 P0~P4 E2E 속도 비교표에
그대로 넣어서는 안 된다.

## 7. 공통 실패 유형 분석

### 7.1 P3 Common 10장

| 실패 유형 | 발생 횟수 |
|---|---:|
| `COORDINATE_ERROR` | 13 |
| `ROW_MERGE` | 9 |
| `TABLE_MISSING` | 6 |

### 7.2 P3 신규 Development 9장

| 실패 유형 | 발생 횟수 |
|---|---:|
| `COORDINATE_ERROR` | 10 |
| `ROW_MERGE` | 3 |
| `TABLE_MISSING` | 17 |

### 7.3 P4 Common 10장

| 실패 유형 | 발생 횟수 |
|---|---:|
| `ANCHOR_NOT_FOUND` | 2 |
| `VALUE_SELECTION_FAILED` | 11 |
| `OCR_TEXT_MISMATCH_OR_INCOMPLETE_VALUE_UNDETERMINED` | 12 |
| `GT_PRESENT_IN_OCR_TOKENS_SELECTION_OR_JOIN_ERROR` | 1 |
| `WHITESPACE_ONLY_MISMATCH` | 2 |
| `NONE` | 22 |

P3 집계는 실패 원인의 발생 횟수로,
고유한 실패 필드 수와 동일하지 않다.

P4 진단은 `not_present` 필드 1개를 포함한
총 50개 필드 기록을 기준으로 한다.

따라서 두 표를 직접적인 필드별 실패율로 비교하지 않는다.
실패 유형은 진단 라벨이며 근본 원인이 독립적으로
입증됐다는 의미는 아니다.

## 8. GT·코드·결과 재현성 검증

### 8.1 데이터셋과 평가 코드

- 최종 GT 기준: `14f240a`
- 공통 평가 구현: `e46062a`
- Development manifest 및 필드 분모 검증 완료
- 2026-11-05 이미지 SHA-256 복사 검증 불일치 0건:
  Dataset README에 기록
- 데이터셋 전체 최종 동결 승인과 최종 파일별 해시 목록:
  별도 확정 증빙 미확인
- 공통 정규화 정책의 팀 전체 최종 동결: 미확인

### 8.2 P0~P2

- P0/P2 결과 파일 최초 추가: `1e9bbe2`
- P0/P2 결과 파일 수정: `a92c1c8`
- P1 원근 보정 결과 추가: `45abadb`
- 관련 평가 및 H1 코드 변경 이력 확인

코드에서 확인된 기본값:

- P0/P2: `PAD_RATIO=0.25`
- P0/P2: `WHOLE_BOX_RATIO=0.5`
- ROI 처리 코드: `BORDER_PX=32`
- P1: `LINE_PAD=0.15`
- P1: `NO_WHOLE_BOX=1.01`

이는 코드 기본값이며 실제 과거 실행 명령어와
모든 적용 파라미터의 증빙을 대신하지 않는다.

### 8.3 P3

- 보고된 동결 커밋 `55c30b0`: Git 존재 확인
- ROI 평가 스크립트 SHA-256: 보존된 결과 기록과 일치
- 과거 결과의 `frozen_commit` 메타데이터: `11af316`
- 과거 결과의 GT 해시: 수정 직전 `6c7180f`와 일치
- 최종 GT `14f240a` 기준 ROI Coverage: 별도 재검증

스크립트 해시 일치만으로 최종 동결 코드의
전체 실행 이력이 확인됐다고 주장하지 않는다.

### 8.4 P4

- 공식 Common 10장 제출물: `063c656`
- 공식 `final_fields.json` 10개 OCR 출처: `cached_ocr`
- 코드 기준 `00e3e4e`: CODE_BASELINE_ONLY
- 동결 코드 기반 전체 Live-OCR 실행 이력: 미검증
- 별도 Development 19장 ZIP: 참고용

## 9. Holdout 절차상 예외

- Holdout 패키지 공개: 2026-11-10 16:04 (KST)
- P3 코드 동결: 2026-11-10 16:42 (KST)
- P3 Holdout 1회 실행: 동결 후 약 16:43
- 이후 성능 개선 목적 재튜닝 없음: 기존 실행 기록 기준
- 최종 GT 기준 P3 Covered: **3/30 (10.00%)**

Holdout이 코드 동결 전에 공개되었으므로
기존 05번 문서에서 정한 공개·동결 순서와 차이가 있다.

해당 결과는 폐기하지 않고,
**절차상 예외가 있는 보조 검증 결과**로 보존한다.
독립적인 untouched Holdout 성능으로 주장하지 않는다.

P4 공식 범위는 Common 10장으로 유지한다.
추가 Holdout 실행이나 알고리즘 수정은 진행하지 않는다.

## 10. 논문 사용 가능성 최종 판정

| 자료 | 최종 판정 |
|---|---|
| P3 Development ROI Coverage 36/94 | 사용 후보, 평가 규약 승인 조건 |
| P3 Common 10 ROI Coverage 21/49 | 사용 후보, 평가 규약 승인 조건 |
| P4 Common 10 ROI Coverage 46/49 | 사용 후보, 평가 규약 승인 조건 |
| P4 별도 Development 19장 | 참고용 |
| P0~P4 공통 정규화 정확도·CER | 참고용 |
| P3 Holdout 3/30 | 절차상 예외를 명시한 보조 결과 |
| 최종 P0~P4 Live E2E 정확도·CER·속도 | 증빙 부족으로 확정 보류 |

### 논문에 기재 가능한 ROI 비교 문장

공통 Development 10장(평가 대상 49필드)에서
P3 Detected ROI는 후보 중 최대 Coverage 기준
21/49(42.86%)의 Covered 비율을 보였으며,
P4 Anchor ROI는 알고리즘이 선택한 단일 최종 ROI 기준
46/49(93.88%)를 보였다.
두 결과는 동일한 최종 GT와 Coverage 임계값 0.90을 기준으로
평가했으나, ROI 선택 방식에는 차이가 있다.

### 최종 미확정 항목

1. 공통 정규화·평가 규약의 팀 전체 최종 동결
2. 데이터셋 전체 동결 및 최종 파일 해시 증빙
3. P0~P4의 동일 조건 독립 E2E 실행 결과 및
   OCR 조건부 정확도·CER·처리 시간 증빙

**평가 담당자의 기존 자료 검증과 판정 문서 제출은 완료한다.**
다만 최종 E2E 비교 수치가 확보되지 않은 상태에서
논문의 전체 성능 평가가 완료됐다고 표시하지 않는다.

## 11. 근거 자료

- `results/eval_gatekeeper/final_evaluation_protocol.md`
- `results/eval_gatekeeper/p0_p4_comparison_template.md`
- `origin/dataset-v1` / `14f240a`
- `origin/tail`의 과거 Common 10장 평가 결과
- P3 `55c30b0`의 Development 평가 자료
- `origin/taegu:results/p4_handoff_verified_v1.zip`