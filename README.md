# P-S-paper — issue branch

> 마지막 업데이트: 2026-10-21

이 브랜치는 공동연구의 연구 방향, 일정, 담당자별 작업, 데이터/GT 규칙과 피드백을 관리한다.

## 논문 중심 주제

**정형 임대차계약서 핵심정보 추출 파이프라인의 단계별 오류 전파 분석: 이미지 품질, 구조 복원, ROI 설정, 문자 인식을 중심으로**

```text
이미지 품질
  -> 구조 복원
  -> ROI 설정
  -> OCR 문자 인식
  -> 정규화/검증
  -> Field Accuracy
```

## 2026-10-21 현재 운영 기준

실제 진행 상황을 반영해 팀을 **핵심 개발/평가 3명 + 데이터/GT 3명**으로 재편한다.

| 담당 | 현재 역할 |
|---|---|
| `bang_` | 자동 구조 복원 / Detected ROI |
| `taegu` | Anchor Field ROI + 최소 End-to-End |
| `dahye_cell_DetectionSurvey` | 최종 평가 총괄 / Evaluation Gatekeeper |
| `heewon` | 정상/통제 촬영 데이터 |
| `tail` | 난이도 촬영 / 이미지 품질 메타데이터 |
| 추가 인원 B | GT / Dataset Manager |

기존 10/08 assignment는 이전 역할 기록이다. 현재 작업은 다음 문서를 우선한다.

## 현재 기준 문서

1. `01_research_direction_and_next_steps.md` — 연구 방향/RQ/실험 기준
2. `03_team_execution_plan_20261021.md` — 최신 6명 역할 및 상세 작업지시
3. `04_data_collection_gt_protocol.md` — 데이터 촬영, GT, manifest, development/holdout 규칙
4. `assignment_*.md` — 개인별 과거/요약 지시
5. `feedback_*.md` — 기존 세부 피드백과 근거

## 데이터 보강 목표

- 기존 공통 10장은 이미 개발/분석에 사용된 데이터로 유지한다.
- 신규 usable 이미지 10~15장을 목표로 한다.
- 최종 총량은 약 20~25장 수준을 권장한다.
- 동일 문서를 여러 조건으로 촬영한 경우 같은 `document_group_id`로 묶는다.
- development / holdout_test는 이미지가 아니라 `document_group_id` 단위로 나눈다.
- 신규 데이터에는 핵심 5필드 GT와 촬영 조건 manifest가 있어야 한다.

## 최종 비교 축

```text
P0 Raw Full OCR
P1 Image-corrected Full OCR
P2 GT ROI OCR
P3 Detected ROI OCR
P4 Anchor ROI OCR (가능 시)
```

## 운영 원칙

- 새 모델이나 대규모 신규 연구축을 추가하지 않는다.
- holdout을 본 뒤 수정한 결과를 untouched test라고 부르지 않는다.
- ROI 누락은 end-to-end 평가에서 실패로 계산한다.
- 좌표계가 다른 prediction과 GT를 함께 평가하지 않는다.
- 이미지 수와 field instance 수를 구분해 보고한다.
- 동일 문서 반복 촬영을 서로 다른 독립 문서처럼 해석하지 않는다.
- 결과를 전체 임대차계약서로 일반화하지 않는다.
