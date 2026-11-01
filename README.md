# P-S-paper — issue branch

> 마지막 업데이트: 2026-11-01

이 브랜치는 공동연구의 연구 방향, 일정, 담당자별 작업, 데이터/GT 규칙과 피드백을 관리한다.

## 가장 먼저 볼 문서

**현재 팀원이 무엇을 해야 하는지 확인할 때는 `05_current_team_tasks_20261101.md`를 가장 먼저 본다.**

이 문서는 2026-10-21의 `03_team_execution_plan_20261021.md`와 과거 `assignment_*.md`보다 우선한다.

- `05_current_team_tasks_20261101.md` — **현재 6명 역할, 즉시 할 일, 산출물, 완료 기준, 전달 순서**
- `04_data_collection_gt_protocol.md` — 데이터 촬영/GT/manifest/holdout 세부 규칙
- `01_research_direction_and_next_steps.md` — 연구 방향/RQ/실험 기준
- `03_team_execution_plan_20261021.md` — 10/21 역할 재편 기록
- `assignment_*.md` — 과거 역할 기록. 최신 지시와 충돌하면 05 문서를 따른다.
- `feedback_*.md` — 기존 세부 피드백과 근거

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

## 2026-11-01 현재 역할

| 담당 | 현재 역할 | 최종 산출물 |
|---|---|---|
| `bang_` | 자동 구조 복원 / Detected ROI | `cells_original.json`, `report.json`, ROI coverage summary |
| `taegu` | Anchor Field ROI + 최소 End-to-End | field ROI, `final_fields.json`, coverage/실패 사유 |
| `dahye_cell_DetectionSurvey` | 최종 평가 총괄 / Evaluation Gatekeeper | P0~P4 최종 비교표, failure breakdown, 논문용 수치 |
| `heewon` | 정상/통제 촬영 데이터 | 신규 usable 원본 5~6장 + 촬영 조건 |
| `tail` | 난이도 촬영 / 이미지 품질 메타데이터 | 신규 usable 원본 5~8장 + 촬영 조건 |
| **가은 학우 (추가 인원 B)** | **GT / Dataset Manager** | `manifest.csv`, `field_gt.json`, development/holdout split, Dataset v1.0 |

## 지금 팀 전체가 끝내야 하는 것

```text
heewon / tail
  -> 신규 원본 데이터 + 조건 기록

가은
  -> 파일명/manifest 통일
  -> 핵심 5필드 GT 작성·검수
  -> document_group_id 단위 development/holdout 분리
  -> Dataset v1.0 동결

bang / taegu
  -> development에서 코드·규칙 확정
  -> commit SHA 기록 후 동결
  -> holdout에는 동일 설정으로 1회 실행

dahye
  -> P0~P4 최종 평가
  -> ROI Coverage / Field Accuracy / CER / 실패 유형 확정
```

## 데이터 보강 목표

- 기존 공통 10장은 이미 개발/분석에 사용된 데이터로 유지한다.
- 신규 usable 이미지 10~15장을 목표로 한다.
- 최종 총량은 약 20~25장 수준을 권장한다.
- 동일 문서를 여러 조건으로 촬영한 경우 같은 `document_group_id`로 묶는다.
- development / holdout_test는 이미지가 아니라 `document_group_id` 단위로 나눈다.
- 신규 데이터에는 핵심 5필드 GT와 촬영 조건 manifest가 있어야 한다.

## 핵심 5필드

```text
address
deposit
contract_amount
lessor_name
lessee_name
```

## 최종 비교 축

```text
P0 Raw Full OCR
P1 Image-corrected Full OCR
P2 GT ROI OCR
P3 Detected ROI OCR          <- bang
P4 Anchor ROI OCR            <- taegu (PoC 가능)
```

## 운영 원칙

- 새 모델이나 대규모 신규 연구축을 추가하지 않는다.
- `heewon`, `tail`의 현재 우선 업무는 과거 실험 확장이 아니라 신규 평가 데이터 수집이다.
- 가은 학우가 Dataset Manager로서 `split`을 최종 확정한다.
- holdout은 bang/taegu 동결 전까지 공개하지 않는다.
- holdout을 본 뒤 수정한 결과를 untouched test라고 부르지 않는다.
- ROI 누락은 end-to-end 평가에서 실패로 계산한다.
- 좌표계가 다른 prediction과 GT를 함께 평가하지 않는다.
- 이미지 수와 field instance 수를 구분해 보고한다.
- 동일 문서 반복 촬영을 서로 다른 독립 문서처럼 해석하지 않는다.
- 결과를 전체 임대차계약서로 일반화하지 않는다.

## 진행 보고 형식

각 담당자는 진행 상황을 다음 형식으로 남긴다.

```text
[담당자/브랜치]
1. 현재 작업:
2. 완료한 것:
3. 생성/수정 파일:
4. 막힌 점:
5. 다음 작업:
```

세부 작업 지시는 반드시 `05_current_team_tasks_20261101.md`를 확인한다.
