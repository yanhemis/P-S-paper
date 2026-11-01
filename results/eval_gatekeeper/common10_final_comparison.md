# 공통 10장 파이프라인 비교 결과 — 2026-11-01

**상태:** 기존 실험 결과 검증 완료 / 신규 데이터 통합 최종 평가 대기  
**담당:** `dahye_cell_DetectionSurvey`

## 1. 평가 범위

- 평가 데이터: 기존 공통 이미지 10장 (`sample_1` ~ `sample_10`)
- 평가 대상: 핵심 필드 인스턴스 49개
- 핵심 5필드: `address`, `deposit`, `contract_amount`, `lessor_name`, `lessee_name`
- 기존 필드명 매핑:
  - `deposit_num` → `deposit`
  - `down_payment` → `contract_amount`
- 보조 필드 `deposit_kor`는 최종 평가 분모에서 제외한다.
- P0~P3는 동일한 이미지-필드 조합과 정규화된 GT 정답을 사용했음을 검증했다.
- 독립 원본 문서 그룹(`document_group_id`)의 수는 아직 확인되지 않았다.

## 2. 공통 10장 파이프라인 비교표

| Pipeline | 이미지 보정 | ROI 출처 | ROI Coverage / 존재율 | Field Accuracy | 평균 CER | sec/image |
|---|---|---|---|---|---|---|
| P0 | 없음 | 전체 페이지 | 해당 없음 | 29/49 (59.2%) | 0.141 | 29.32 |
| P1 | 원근 보정 (Rectified) | 전체 페이지 | 해당 없음 | 31/49 (63.3%) | 0.120 | 31.13 |
| P2 | 기존 GT ROI 평가 조건 | GT ROI | 100% (정답 ROI 제공) | 31/49 (63.3%) | 0.117 | 0.93 |
| P3 | 기존 Detected ROI 평가 조건 | bang Detected ROI, padding 25% | 22/49 (44.9%, ROI 기록 존재율) | 13/49 (26.5%) | 0.985 | 0.95 |

위 결과는 모두 기존 공통 10장에 대한 실험 결과이다.

**처리 시간 해석 시 주의사항**

- P0/P1의 시간은 전체 페이지 OCR 실행 결과를 기준으로 한다.
- P1의 이미지 보정 시간이 포함되었는지는 확인되지 않았다.
- P2/P3의 시간은 ROI OCR 처리 시간이며, 전체 파이프라인 실행 시간이 아니다.
- P3의 구조 검출 및 필드 매핑 시간은 포함되지 않았다.
- 따라서 위 `sec/image` 수치를 완전한 End-to-End 처리 속도로 직접 비교해서는 안 된다.

## 3. P3 ROI 존재율 및 오류 분석

| 결과 유형 | 필드 수 |
|---|---:|
| ROI 기록 존재 + 필드 정답 | 13 |
| ROI 기록 존재 + 필드 오답 | 9 |
| ROI 기록 없음 + 필드 오답 | 27 |
| **전체 평가 대상** | **49** |

- ROI 기록 존재율: **22/49 = 44.9%**
- ROI 기록이 존재할 때의 조건부 Field Accuracy: **13/22 = 59.1%**
- 전체 Field Accuracy: **13/49 = 26.5%**
- ROI 기록이 없는 27개 필드는 모두 오답으로 처리되었음을 확인했다.

**해석상 주의사항**

ROI 기록 존재율은 평가 JSON에 해당 필드가 기록되어 있는지를 나타내며, 실제 GT 영역과의 기하학적 일치 여부를 검증한 ROI Coverage는 아니다.

ROI가 기록되었으나 오답인 9개 필드는 필드 매핑, ROI 위치 설정, OCR 인식 또는 정규화 단계에서 오류가 발생했을 가능성이 있다. 다만 세부 원인은 아직 확정적으로 분류되지 않았다.

## 4. P4 — 별도 PoC 평가

- 결과 출처: `origin/taegu`
- 평가 이미지: `sample.jpg` 1장
- Anchor 발견: **5/5**
- 원문 문자열 기준 Exact Match: **5/5**
- 공통 정규화 규칙 적용 여부, CER, 기하학적 ROI Coverage 및 처리 시간은 아직 검증되지 않았다.

따라서 P4 결과는 **단일 이미지 PoC 결과로 별도 보고**하며, 기존 공통 10장에 대한 P0~P3 결과와 직접 비교하지 않는다.

## 5. 결과 해석

1. P1의 원근 보정 Full OCR과 P2의 GT ROI OCR은 모두 **31/49 (63.3%)**의 Field Accuracy를 기록했다. 그러나 정확도가 같다는 사실이 두 방법의 오류 발생 원인까지 동일하다는 의미는 아니다.

2. P3는 **13/49 (26.5%)**의 Field Accuracy를 기록했으며, 전체 49개 필드 중 27개에서 ROI 기록이 누락되었다.

3. P3의 조건부 Field Accuracy **13/22 (59.1%)**는 ROI 선택·매핑과 OCR 인식 결과가 함께 반영된 수치다. OCR 모델 자체의 독립적인 인식 정확도로 해석해서는 안 된다.

4. 기존 P0/P1 평가에서는 전체 페이지 OCR 결과를 각 필드에 배정할 때 GT ROI 좌표를 사용했다. 따라서 GT의 도움 없이 작동하는 완전 자동 End-to-End 필드 추출 성능으로 주장할 수 없다.

5. P2는 정답 ROI를 제공한 Oracle 조건의 비교 실험이며, 자동 ROI 검출 성능을 나타내는 결과가 아니다.

6. 본 비교는 제한된 공통 10장 데이터에 대한 결과이므로, 모든 임대차계약서에 일반화해서는 안 된다.

## 6. 최종 논문 결과 확정 전 남은 작업

- 공통 정규화 규칙 확정, 특히 `contract_amount`의 숫자 금액 정규화 기준 통일
- 신규 Dataset v1.0 검수 및 `document_group_id` 기준 development/holdout 분할 확인
- 기존 평가와 신규 데이터 평가의 정규화 기준 일치 여부 확인
- bang/taegu의 development 결과 인수 및 코드 동결 commit SHA 확인
- GT bbox가 제공되는 경우 기하학적 ROI Coverage 추가 검증
- 단계별 처리 시간 또는 전체 파이프라인 처리 시간 확보
- 증거가 확보된 P3/P4 실패 유형별 원인 분석
- 신규 데이터 결과를 기존 공통 10장과 별도 표로 먼저 작성
- 코드 및 평가 규칙 동결 이후 untouched holdout 최종 1회 평가

## 7. 참고 자료 및 검증 출처

- `origin/tail:results/eval/field_results.json`
- `origin/tail:results/h1/eval_rectified/field_results.json`
- `origin/tail:results/eval/detected_bang_pad25/field_results.json`
- `origin/tail:results/eval/detected_bang_pad25/summary.md`
- `origin/taegu:field_gt.json`
- `origin/taegu:field_mapping_result.json`
- `results/eval_gatekeeper/p3_roi_audit_common10.md`
- `results/eval_gatekeeper/common10_field_eval_audit.md`
- `results/eval_gatekeeper/common10_normalization_audit.md`
- `results/eval_gatekeeper/p4_anchor_poc_audit.md`

---

**최종 상태:** 기존 공통 10장 평가 결과의 비교 및 감사는 완료되었다. 다만 신규 Dataset v1.0, 공통 금액 정규화 기준, 코드 동결 및 holdout 평가가 완료되지 않았으므로 본 문서는 최종 논문 수치 확정 전 비교표 초안이다.