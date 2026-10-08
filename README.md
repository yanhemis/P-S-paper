# P-S-paper — issue branch

> 마지막 업데이트: 2026-10-08

이 브랜치는 공동연구의 **연구 방향, 일정, 담당자별 작업, 피드백**을 관리한다.

## 개정된 논문 중심 주제

**정형 임대차계약서 핵심정보 추출 파이프라인의 단계별 오류 전파 분석: 이미지 품질, 구조 복원, ROI 설정, 문자 인식을 중심으로**

기존처럼 ROI 정확도 향상 자체를 주된 결론으로 삼지 않는다. 동일 데이터와 Ground Truth에서 각 단계가 최종 Field Accuracy에 미치는 영향을 분리해서 비교한다.

```text
이미지 품질
  -> 구조 복원
  -> ROI 설정
  -> OCR 문자 인식
  -> 정규화/검증
  -> Field Accuracy
```

## 최종 연구 질문

1. 이미지 품질 변화가 OCR과 Field Accuracy에 얼마나 영향을 주는가?
2. 구조 복원 오류가 핵심 필드 localization에 얼마나 영향을 주는가?
3. Full OCR, GT ROI OCR, Detected ROI OCR의 차이는 무엇인가?
4. 구조와 ROI 오류를 통제한 뒤 남는 최종 병목은 무엇인가?

## 담당자 재배정

| 담당 | 최종 역할 | 핵심 산출물 | 내부 마감 |
|---|---|---|---|
| `bang_` | 자동 구조 복원 결과 공급 | 공통 10장 `cells_original.json`, report, 실패 사례 | 10/09 |
| `dahye_cell_DetectionSurvey` | 공통 구조 평가 감사/확정 | 좌표계 수정 평가, PP/TATR overlay, 최종 구조 비교표 | 10/09 |
| `heewon` | 구조 입력 방식 보조 실험 | Morphology vs Contour 정리, 가능 시 bbox JSON, 오류 taxonomy | 10/10 |
| `taegu` | Field ROI Localization | 핵심 5필드 ROI, coverage/실패 유형, 가능 시 10장 | 10/10 |
| `tail` | 이미지 품질 + OCR + 최종 Field Accuracy | E0/E1/E3/E4/E5 비교, 최종 단계별 성능표 | 10/11 |
| 추가 인원 B | End-to-End 통합 | requirements, 실행 경로, `final_fields.json`, 보조 Guardrail | 10/10 |
| PM/논문 통합 | 연구 설계/논문 통합 | Method/Experiment/Discussion, 수치 검증 | 10/12 |

## 남은 일정

- **10/08** 연구 설계 및 주장 동결
- **10/09** 좌표계/평가 입력 확정
- **10/10** 자동 ROI 및 End-to-End 마감
- **10/11** 최종 정량표 확정
- **10/12** 논문 최종 검토
- **10/13** 프로젝트 최종 완료

> 10월 8일 이후 신규 모델이나 새로운 대규모 실험축은 추가하지 않는다.

## 최종 비교 축

```text
P0 Raw Full OCR
P1 Image-corrected Full OCR
P2 GT ROI OCR
P3 Detected ROI OCR
P4 Anchor ROI OCR (가능 시)
```

구조 복원은 별도 공통 GT에서 PP-Structure / TATR / OpenCV를 비교한다.

## 공통 평가 기준

- 이미지 품질: 인쇄 한글 재현율, CER, Field Accuracy 변화
- 구조 복원: IoU, Precision, Recall, F1, General/Merged GT localization recall
- ROI: Coverage, 가능하면 IoU, 성공/실패 건수
- OCR: CER, Exact Match, confidence
- 최종: Field Accuracy, sec/image

## 해석 원칙

- ROI가 항상 성능을 높인다고 전제하지 않는다.
- OpenCV가 항상 구조 모델보다 우수하다고 전제하지 않는다.
- 실행 실패와 성능 실패를 구분한다.
- 좌표계가 다른 prediction과 GT를 함께 평가하지 않는다.
- 자동 ROI 성능 저하도 실패가 아니라 연구 결과로 기록한다.
- 10장 결과를 모든 임대차계약서에 일반화하지 않는다.

## 문서 구성

- `00_scope_guard_prompt.md`: 연구 범위 이탈 방지 기준
- `01_research_direction_and_next_steps.md`: 개정 연구 방향 / RQ / 실험 / 일정 / 전체 현황
- `assignment_*.md`: 담당자별 최종 역할과 산출물
- `feedback_*.md`: 담당자별 세부 피드백
