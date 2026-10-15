# tail 작업 배정 — 이미지 품질 + OCR + 최종 Field Accuracy

> 재배정일: 2026-10-08 (원문: `../issue/assignment_member_A_ocr_roi_field_accuracy.md`)
> 내부 마감: 2026-10-11 (논문 검토 10/12, 프로젝트 완료 10/13)
> 이전 배정(09-22, ROI 재인식 중심)은 이 문서로 대체. 10/08 이후 신규 모델·대규모 실험축 추가 금지.

## 1. 담당 목표

논문 핵심 정량 담당. **각 단계(이미지 품질 → ROI → 문자 인식)를 통제했을 때 최종 Field Accuracy가 얼마나 변하는지** 같은 기준으로 비교한다.

> ROI가 항상 좋다고 전제하지 않는다. 자동 ROI 성능 저하도 실패가 아니라 결과로 기록한다. 10장 결과를 일반화하지 않는다.

연구 질문 대응: RQ1(이미지 품질), RQ3(Full/GT/Detected ROI), RQ4(남는 병목).

---

## 2. 실험 단계와 현황 (2026-10-16 기준)

| 단계 | 내용 | 파이프라인 | 상태 | 결과 위치 |
|---|---|---|---|---|
| E0 | Raw Full OCR | P0 | ✅ 확정 | `results/eval/summary.md` |
| E1 | 원근 보정 Full OCR | P1 | ✅ 확정 | `results/h1/eval_rectified/` |
| E3 | GT ROI OCR (oracle) | P2 | ✅ 확정 | `results/eval/summary.md` |
| E4 | Detected ROI OCR (`bang_` 공통 10장) | P3 | ✅ 실행 (2026-10-16) | `results/eval/detected_bang_pad25/`, `detected_bang_pad0/` |
| E5 | Anchor ROI OCR (`taegu`) | P4 | 🔶 10장 미수신 → 공통 sample PoC만 유지 | `results/detected_roi/taegu_common_sample.json` |

E2(구조 복원 평가)는 dahye, E6(End-to-End)는 추가 인원 B 담당 — tail은 하지 않는다.

### 최종 핵심 표 (필드 49개: 5필드 × 10장, #7 계약금 제외)

| Pipeline | Image correction | ROI source | Field Accuracy | CER | sec/image |
|---|---|---|---:|---:|---:|
| P0 | X | Full page | 29/49 (59.2%) | 0.141 | 29.3 |
| P1 | 원근 보정 | Full page | 31/49 (63.3%) | 0.120 | 31.1 |
| P2 | X | GT ROI | 31/49 (63.3%) | 0.117 | 0.93 |
| P3 | X | Detected ROI (bang_), pad 25% | 13/49 (26.5%) | 0.985 | 0.95 |
| P3' | X | Detected ROI (bang_), pad 0 | 10/49 (20.4%) | 1.020 | 0.90 |
| P4 | — | Anchor ROI | PoC만 (10장 미수신) | — | — |

주의: P3는 `bang_`이 필드 60개 중 25개만 넘겼고(나머지는 구조 복원 실패로 누락), 필드↔셀 대응은 GT ROI를 기준으로 고른 것이라 Anchor 성능은 포함되지 않는다. ROI sec/image에는 셀 검출 시간이 없다.

---

## 3. 오류 분석 (Detected ROI 실패 36건, pad 25% 기준)

| 분류 | 건수 | 의미 |
|---|---:|---|
| 구조/ROI 누락 (ROI 없음) | 27 | 구조 복원이 표를 못 찾음 (`bang_` 전달 25/60; sample_5·7·10은 0개) |
| ROI 혼입/경계 (GT ROI는 성공) | 4 | 계약금 칸에 "계약시에 지급하고 영수함…"까지 포함 등 |
| Recognition (GT ROI도 실패) | 5 | 소재지 손글씨 등 문자 인식 병목 후보 |

- ROI가 전달된 22개 필드만 보면: Full 15 / GT ROI 15 / Detected 13 → 전달된 ROI만 놓고는 손실이 작다. 병목은 **ROI의 정확도보다 ROI가 아예 없는 경우(커버리지)**.
- GT ROI에서도 실패하는 필드: 소재지 0/10 → 문자 인식 병목. 이미지 보정(P1)으로도 근본 해결 안 됨.
- 이미지 품질: 원근 보정만으로 31/49로 GT ROI와 동일 → ROI 이득 일부는 해상도/보정 효과 (H1).

### 3-1. 오류 4종 통합 표 (필드 49개, 필드별로 P0~P3 결과를 대조한 값)

**(a) 최종 Detected ROI(P3) 실패 36건의 원인**

| 오류 종류 | 건수 | 판정 기준 | 해석 |
|---|---:|---|---|
| ① 구조/ROI localization (ROI 없음) | 16 | P3에 ROI 없음, GT ROI는 성공 | ROI만 있었으면 맞았을 필드 |
| ② ROI crop 혼입/잘림 | 4 | P3 ROI 있음·실패, GT ROI는 성공 | 계약금 칸에 인접 글자 포함 등 |
| ③ Recognition (구조/ROI와 무관) | 16 | GT ROI도 실패 | ROI 없음 11 + ROI 있음 5. ROI가 없는 11건도 ROI가 있었어도 틀렸을 필드 |
| ④ 이미지 품질 | 0* | — | *아래 (b) 참고. P3 단계에서는 따로 분리되지 않음 |
| 합계 | 36 | | |

**(b) Full OCR(P0) 실패 20건에서 단계별로 고쳐진 수**

| 통제한 단계 | 고쳐진 필드 | 새로 틀린 필드 | 순효과 |
|---|---:|---:|---:|
| ④ 이미지 보정 (P0→P1 원근 보정) | 4 | 2 | +2 (29→31) |
| ROI 설정 (P0→P2 GT ROI) | 5 | 3 | +2 (29→31) |
| 자동 ROI (P0→P3) | 2 | 18 | −16 (29→13) |

- 두 개선(P1, P2)은 효과가 같고 서로 다른 필드를 고치는 부분이 있어 합산할 수 없다. 이 표는 각 단계 단독 효과다.
- P1·P2 모두 소재지 0/10은 그대로이다.

**(c) 결론**: 최종 자동 파이프라인의 손실 36건 중 ROI 없음/혼입(① + ②)이 20건, 인식 한계(③)가 16건이다. 단, ①~③은 한 필드에 겹칠 수 있어 ③으로 분류한 11건은 ROI를 고쳐도 남는다. 즉 **ROI를 모두 복구해도 Field Accuracy는 GT ROI 상한(31/49) 근처에서 멈춘다.** 이미지 보정은 +2건 수준이다 (n=49, 일반화 주의).

---

## 4. 남은 작업 (10/11 마감 기준)

- [x] E0/E1/E3 최종값 확정
- [x] `bang_` 공통 10장 ROI 수신 → 같은 OCR 조건(`PP-OCRv5_mobile`, 1536)으로 실행
- [x] Field Accuracy / CER / confidence 계산
- [x] 단계별 성능표 초안 (위 2절)
- [ ] `taegu` 10장 ROI 수신 시 E5 실행 (없으면 PoC로 축소 명시)
- [x] Recognition 잔여 오류 유형 정리 (`results/eval/recognition_errors.md`)
- [ ] README.md에 E4 결과·표 반영, `docs/ocr_io_spec.md` 추가 인원 B 전달 확인
- [ ] 이전 커밋에 남은 GPS 원본 사진 처리 결정 (히스토리 재작성은 팀 합의 필요)

## 5. 하지 않을 것

- Cell Detection 알고리즘 수정, Anchor 규칙 재설계, 새 OCR 모델 학습
- TATR / PP-Structure 조사 (dahye), 셀 검출 개발 (bang_/heewon)

## 6. 받아서 쓰는 것 / 넘겨주는 것

- 받음: 공통 GT, `bang_` `cells_original.json`·`handoff_tail/`, `taegu` Anchor ROI, 공통 evaluator 포맷(dahye)
- 넘김: 추가 인원 B에게 OCR/ROI 모듈 및 입출력 규격(`docs/ocr_io_spec.md`), PM에게 최종 단계별 표

## 재현 명령

```bash
P=/opt/anaconda3/envs/tail/bin/python
B=../bang_/output/common10/handoff_tail/detected_roi_cells.json
$P scripts/roi_ocr.py $B results/roi_detected_bang_pad25
$P scripts/roi_ocr.py $B results/roi_detected_bang --pad 0
$P scripts/evaluate_fields.py --detected results/roi_detected_bang_pad25 --out-dir results/eval/detected_bang_pad25
$P scripts/evaluate_fields.py --detected results/roi_detected_bang --out-dir results/eval/detected_bang_pad0
```
