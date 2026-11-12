# 2026-11-12 연구 마감 결정 — 최종 증빙 확인·논문 결과 사용 기준

> **효력:** 2026-11-12부터 최종 마감 판단에는 이 문서가 `05_current_team_tasks_20261101.md`의 기존 "P0~P4 논문용 전체 E2E 표를 반드시 완성" 조건보다 우선합니다. 05의 연구 단계별 작업은 이력으로 유지합니다. 이 문서는 새 실험 지시가 아닙니다.

## 1. 총괄 결정

1. **다혜 `de7073b` 한국어 최종 평가 검증 보고서는 담당 검증 업무 완료로 인정한다.** 전체 P0~P4 최종 Live-OCR E2E 수치 부재는 보고서의 결함 또는 다혜 개인의 미완료로 판정하지 않는다.
2. **새 알고리즘 수정, 추가 데이터 촬영, OCR 재실행 및 Holdout 재실행을 요청하지 않는다.** 기존 증빙이 있다면 출처만 제출하고, 없다면 "미검증"으로 끝낸다.
3. 최종 GT 비교 기준: `dataset-v1@14f240a`. 공통 평가 **코드 버전 기준**: `e46062a`. **2026-11-12 평가·논문 보고 규약은 `668aac6` 승인안에 한정하여 프로젝트 마감 기준으로 승인**한다(아래 4절). 코드에 `DRAFT` 표시가 남아 있고 Tail Common10 전용 실행 경로가 있으므로 **방법론 승인만으로 전체 Dataset 자동 평가 실행, 성능, E2E 재현성이 입증되지는 않는다.**
4. 논문용 표는 **검증된 ROI 지표 / 기존 예측값 재평가 참고 수치 / 최종 Live E2E 미검증**으로 분리한다. 누락 칸을 임의 값이나 이질적인 실행 조건의 과거 수치로 채우지 않는다.
5. Holdout 공개가 P3 코드 동결보다 먼저 이루어진 절차상 예외를 숨기지 않는다. P3 Holdout 결과는 **보조 검증**으로만 사용한다.

## 2. 검증된 수치와 범위

### 공식 Common 10장

- 이미지 10장, 문서 그룹 10개, 유효 필드 49개. `common_007/contract_amount`의 `not_present` 1개는 공식 분모 제외.
- P2 GT ROI: 49/49 (100.00%), **Oracle 기준**이며 자동 검출 성능 아님.
- P3 Detected ROI: **21/49 (42.86%)**, 평균 GT Coverage **0.661941**.
- P4 Anchor ROI: **46/49 (93.88%)**, 평균 GT Coverage **0.956120**.
- P3는 제출된 여러 ROI **후보 중 GT와 겹침이 최대인 값**을 보고한다. P4는 알고리즘의 **선택된 최종 ROI 1개**를 보고한다. 방식이 다르므로 같은 자동 추출 성공률 또는 공정한 최종 E2E 우열로 단정하지 않는다.
- Coverage = `Area(GT ∩ ROI) / Area(GT)`; 반올림 전 값 `>= 0.90`이면 Covered. 지나치게 큰 ROI의 과검출은 별도 한계로 보고한다.

### Development, Holdout

- 신규 Development 9장, 문서 그룹 3개, 유효 필드 45개: P3 **15/45 (33.33%)**.
- Development 전체 19장, 문서 그룹 13개, 유효 필드 94개: P3 **36/94 (38.30%)**.
- P4 별도 Development 19장 **66/94 (70.21%)**는 공식 Common 10장과 별개 **참고 자료**다.
- Holdout 후보 6장, 문서 그룹 2개, 유효 필드 30개: P3 **3/30 (10.00%)**, 절차상 예외가 있어 **untouched test로 주장하지 않는 보조 결과**다.

### 기존 예측값 공통 정규화 재평가 (Common 10장, 49필드)

| Pipeline | 정답/분모 | 공통 정규화 참고 Field Accuracy | 참고 평균 Field CER |
|---|---:|---:|---:|
| P0 과거 예측 | 29/49 | 59.18% | 0.577415 |
| P1 과거 예측 | 29/49 | 59.18% | 0.555744 |
| P2 과거 예측, GT ROI | 30/49 | 61.22% | 0.554512 |
| P3 과거 예측 | 12/49 | 24.49% | 1.156608 |
| P4 공식 캐시 기반 예측 | 24/49 | 48.98% | 0.339115 |

**위 표는 최종 Live-OCR E2E 비교표가 아니다.** P0/P1 과거 필드 할당은 GT 위치 기반; P2는 GT ROI; P3 예측은 동결 실행의 최종 Live E2E 증빙 부재; P4 공식 Common 10장 OCR 출처는 `cached_ocr`. CER는 문자 수 가중 전체 CER가 아니라 **정규화 후 필드별 CER 산술평균**이다.

### 논문 최종 E2E 표

| Pipeline | E2E Field Accuracy | E2E CER | E2E sec/image | 판정 |
|---|---|---|---|---|
| P0 | 미검증 | 미검증 | 미검증 | GT 보조 필드 할당 |
| P1 | 미검증 | 미검증 | 미검증 | GT 보조 필드 할당 |
| P2 | 독립 E2E 아님 | 미검증 | 미검증 | GT ROI Oracle |
| P3 | 미검증 | 미검증 | 미검증 | 동결 Live-OCR 실행 증빙 부족 |
| P4 | 미검증 | 미검증 | 미검증 | 공식 Common 10장 cached OCR |

- 과거 속도 수치는 단계 경계 및 캐시/장비 조건이 달라 최종 동일 조건 비교에 넣지 않는다.
- ROI Coverage가 높아도 OCR 조건부 정확도나 최종 Field Accuracy가 높다는 뜻은 아니다.
- 논문에서 **전체 E2E 성능 검증 완료**라는 표현을 사용하지 않는다.

## 3. 담당자별 최종 확인 이슈

| 담당 | 최종 확인 범위 | GitHub 이슈 | 마감 인정 기준 |
|---|---|---|---|
| 하겸 (`bang_`) | P3 과거 Live-OCR E2E 실행 결과·커밋·로그·시간 경계의 **존재 여부** | [#5](https://github.com/yanhemis/P-S-paper/issues/5) | 기존 증빙 인계 또는 **증빙 없음** 회신 |
| 태구 (`taegu`) | P4 공식 Common 10장 cached OCR와 별도 19장 live OCR 구분; 기존 Live 실행 증빙 확인 | [#6](https://github.com/yanhemis/P-S-paper/issues/6) | 출처 구분 및 기존 증빙 여부 확인 |
| 다혜 (`dahye_cell_DetectionSurvey`) | 제출 보고서 완료 인정, 공통 규약 승인안, 새로운 증빙의 적합성만 검토 | [#7](https://github.com/yanhemis/P-S-paper/issues/7) | **보고서 검증 업무 완료**; 규약 승인 여부 별도 기록 |
| 가은 (추가 인원 B) | `14f240a` 기준 manifest·GT·그룹 분리·파일 해시·개인정보/EXIF 검수·Dataset 동결 상태 | [#8](https://github.com/yanhemis/P-S-paper/issues/8) | 기존 검수/동결 증빙 또는 미확인 항목 명시 |
| 희원 (`heewon`) | 정상·통제 촬영 원본/조건/그룹의 기존 인계 확인 | [#9](https://github.com/yanhemis/P-S-paper/issues/9) | 기존 인계 완료 또는 누락 기록 |
| Tail (`tail`) | 난이도 촬영 인계 + P0~P2 과거 실행·타이밍 증빙 확인 | [#10](https://github.com/yanhemis/P-S-paper/issues/10) | 기존 증빙 인계 또는 미확인 기록 |

이슈는 담당 **브랜치/역할**로 표시하며, 확인되지 않은 GitHub 사용자명으로 자동 할당하지 않는다.

## 4. 평가 규약 `e46062a` 승인 조건

`e46062a`는 **현재 사용한 공통 평가 구현 버전**으로 고정한다. **규약 동결 승인은 별도 문서 결정**이며, 아래 사항을 명시한 뒤 팀 책임자가 승인한다.

- 공통 필드: `address`, `deposit`, `contract_amount`, `lessor_name`, `lessee_name`; 구 필드 `deposit_num` → `deposit`, `down_payment` → `contract_amount`; `deposit_kor`는 보조.
- 문자 NFC·공백 및 필드별 문장부호·이름/주소 전처리, 금액 KRW 정규화와 허용 가능한 천 단위 구분자 패턴. 임의 OCR 오류 교정 금지; 한글/숫자 금액 동시 표현은 각각 유효하고 일치해야 한다.
- `image_id × field` 기준 GT 분모, `not_present` 제외. 예측/ROI 누락은 **유효 E2E 필드의 오답**이며 분모에서 제거하지 않는다. `bbox:null`·`unreadable`는 ROI Coverage 분모 정책에 따르되 텍스트 분모와 혼동하지 않는다.
- CER는 **GT·예측에 같은 정규화** 적용 후 필드별 Levenshtein/GT 길이를 구하고 산술평균한다(코퍼스 전체 문자 수 가중 CER와 다름).
- 최종 GT `14f240a`, 원본 이미지 좌표계, ROI 겹침과 P3/P4 후보 선택 방식, Development/Common/Holdout 분리 및 문서 그룹 수를 함께 명시.
- 코드의 모든 실행 경로가 최신 Dataset에 대해 독립 검증된 것은 아니므로 **규약 승인 = E2E 실행 증빙 승인**이 아님.

### 4.1 평가 규약 승인 기록 (2026-11-12)

**판정: 논문·평가 결과의 산출/표기 규약으로 승인.** 담당자 제출안 `dahye_cell_DetectionSurvey@668aac6`의 문서 [`results/eval_gatekeeper/final_evaluation_protocol.md`](https://github.com/yanhemis/P-S-paper/blob/668aac6/results/eval_gatekeeper/final_evaluation_protocol.md)에서 **맨 아래 "최종 평가 규약 승인용 요약 (2026-11-12)" 1~6항을 최신 규약으로 적용**한다. 그 이전의 `DRAFT` 표시 및 `d4b32b6`·`ead8436` 데이터 스냅샷, 과거 실험 작업 목록은 **이력**으로 남긴다. 최신 규약과 충돌할 때 최신 요약과 이 06 문서를 우선한다.

승인 내용:
- 최종 GT `14f240a`와 공통 평가 구현 참조 버전 `e46062a`를 변경하지 않고 기록한다. 구현 소스 `common_evaluator.py`, `amount_normalizer.py`의 당시 정규화 동작은 정책을 재현할 때의 코드 참고점이다.
- 5필드/구 필드 매핑, 이미지×필드 분모, `not_present` 제외, 예측·ROI 누락 실패 처리, 금액의 **숫자 KRW Exact Match**, 정규화된 **문자열 기반 필드별 CER 산술평균**, Covered `>=0.90`을 승인한다.
- P3 후보들의 **GT 기준 최대 Coverage는 평가 시 상한 성격의 지표 산출 방식**이지 실제 모델이 GT를 사용해 최종 ROI를 선택했다는 뜻이 아니다. P4는 알고리즘 선택 최종 ROI만 평가한다. 두 방식의 차이를 표와 캡션에 필수 명기한다.
- 공식 지표를 **검증된 ROI 결과**, **기존 예측 공통 정규화 참고 정확도·CER**, **동일 조건 Live E2E 미검증**으로 계속 분리한다. P4 캐시 `24/49` 공백 무시 참고치와 `24/49` 공통 정규화 참고치는 수치가 같아도 동일 계산으로 단정하지 않는다.
- P0/P1 GT 기반 필드 할당, P2 Oracle, P3 코드 동결 이후 Live-OCR E2E 자료 부재, P4 캐시/동결 종류, Holdout 공개-동결 순서 예외를 모든 해당 결과의 방법·한계로 기재한다.
- 독립적인 `e46062a`의 Dataset v1.0 전체 실행 테스트, P0~P4 Live E2E 정확도·CER·속도, 전체 Dataset 동결/이미지별 해시·EXIF 검수는 **승인 범위에 포함하지 않는다**. 평가 규약 승인은 프로그램 전체 검증 완료/논문 최종 게재 승인과 다르다.

승인에 따라 다혜 평가 **증빙 적합성 확인 업무와 규약 승인안 제출 업무를 완료 처리**한다. 데이터셋 최종 동결은 [#8](https://github.com/yanhemis/P-S-paper/issues/8)에서 별도로 판정한다.

## 5. 마감 체크리스트

- [x] 다혜 `de7073b` 최종 검증 인계 보고서 제출 및 평가 업무 완료 인정
- [x] 검증 ROI Coverage와 참고 정확도·CER 구분
- [x] P3 Holdout 공개-동결 순서 예외 명시
- [x] 기존 증빙 확인을 위한 담당자별 이슈 게시
- [x] P3 #5, P4 #6, 희원 #9, Tail #10 기존 제출물·한계 검토 완료
- [ ] 가은 Dataset v1.0 전체 동결·최종 파일 해시 및 기존 검수 상태 확인
- [x] 정규화/평가·논문 보고 규약 승인 기록 — `668aac6` 최신 요약 기준, `e46062a` 코드는 참고 구현(전체 실행 검증 아님)
- [ ] 각 담당자 기존 실행/인계 자료의 존재 여부 회신 정리 — #5·#6·#7·#9·#10 검토 완료, #8 대기
- [ ] 최종 논문 표·캡션·한계 문구 책임자 승인

**종료 규칙:** 위 미확인 이슈는 "기존 증빙 없음 / 미검증" 등으로 닫을 수 있다. 그러나 이슈 종료가 P0~P4 Live E2E 성능 검증을 의미하지는 않는다. 미검증은 미검증 그대로 논문에 남긴다.

## 6. 근거 링크

- [다혜 한국어 최종 평가 검증 인계 보고서 (`de7073b`)](https://github.com/yanhemis/P-S-paper/blob/de7073b/results/eval_gatekeeper/final_paper_evaluation_handoff.md)
- [P0~P4 비교표 및 출처 상세 (`de7073b`)](https://github.com/yanhemis/P-S-paper/blob/de7073b/results/eval_gatekeeper/p0_p4_comparison_template.md)
- [GT 최종 변경 (`14f240a`)](https://github.com/yanhemis/P-S-paper/commit/14f240a50133be26b71733b26079b1ebe3fe2253)
- [공통 평가 구현 변경 (`e46062a`)](https://github.com/yanhemis/P-S-paper/commit/e46062a65a303bfe5d116629cba1563f5f8e9bad)
