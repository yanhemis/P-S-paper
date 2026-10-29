# tail → dahye 인계: E0 / E1 / E3 / E4 OCR 결과 (2026-10-29)

`issue/03_team_execution_plan_20261021.md` 의 "기존 tail E0/E1/E3/E4 결과를 평가 기준의 출발점으로 인수" 항목용.
수치 원본은 모두 이 저장소(`tail/`)의 json이며, 이 문서는 위치와 주의점만 정리한다.

## 1. 결과 요약 (기존 공통 10장, 평가 필드 49개)

| 단계 | 파이프라인 | Field Accuracy | 평균 CER | sec/image | 원본 위치 |
|---|---|---|---|---|---|
| E0 | P0 Raw Full OCR | 29/49 (59.2%) | 0.141 | 29.32 | `results/eval/summary.md`, `results/eval/field_results.json` |
| E1 | P1 원근 보정 Full OCR | 31/49 (63.3%) | 0.120 | 31.13 | `results/h1/eval_rectified/` |
| E3 | P2 GT ROI OCR | 31/49 (63.3%) | 0.117 | 0.93 | `results/eval/summary.md`, `results/roi_gt/` |
| E4 | P3 Detected ROI (`bang_`, 여유 25%) | 13/49 (26.5%) | 0.985 | 0.95 | `results/eval/detected_bang_pad25/` |
| E4' | P3 Detected ROI (`bang_`, 여유 0) | 10/49 (20.4%) | 1.020 | 0.90 | `results/eval/detected_bang_pad0/` |

오류 분해: [`plan_20261008_ocr_experiments.md`](plan_20261008_ocr_experiments.md) 3-1절(오류 4종 통합 표), [`../results/eval/recognition_errors.md`](../results/eval/recognition_errors.md).

## 2. 재현 명령

```bash
P=/opt/anaconda3/envs/tail/bin/python
B=../bang_/output/common10/handoff_tail/detected_roi_cells.json
$P scripts/roi_ocr.py $B results/roi_detected_bang_pad25
$P scripts/evaluate_fields.py --detected results/roi_detected_bang_pad25 --out-dir results/eval/detected_bang_pad25
```
OCR 조건: `PP-OCRv5_mobile_det` + `korean_PP-OCRv5_mobile_rec`, `limit_side_len=1536` (서버 모델은 OOM). `requirements.txt` 참고.

## 3. 통합 평가 시 확인해야 할 점

1. **분모**: 현재 49 = 5필드 × 10장 − 계약금 1개(#7 미기입). 새 규칙(ROI가 없는 필드는 end-to-end에서 실패로 계산)과 맞는지 확인. 현 E4도 `bang_`이 안 넘긴 필드는 빈 예측으로 실패 처리했다 (분모 49 유지, 전달된 필드만 보면 22개).
2. **필드명 불일치**: tail `deposit_num / deposit_kor / down_payment` ↔ 04 문서 GT `deposit / contract_amount`. `deposit_kor`(한글 금액)는 tail에서 보조 지표라 49에 안 들어간다.
3. **금액 정규화**: tail은 숫자만 추출해 비교하고 끝의 `원`, `(인)`, 공백 등을 제거한다 (`scripts/evaluate_fields.py` normalize). 04 문서의 `raw_text`/`normalized` 방식과 규칙이 같은지 확인 필요.
4. **P3의 조건**: `bang_`이 필드마다 GT ROI를 가장 많이 덮는 검출 셀을 골랐다 (`bang_/docs/08_handoff_tail_common10.md`). 즉 "필드 위치는 안다"는 가정이며 Anchor 성능은 포함하지 않는다. 또 `over_merged_cell`, `no_cell`은 일부러 빠졌다.
5. **ROI sec/image**: 셀 검출 시간은 빠져 있고 OCR 시간만이다.
6. **좌표계**: 입력 quad는 원본 이미지, EXIF 회전 적용 후(3024×4032). P1(원근 보정)은 보정 후 좌표로 별도 GT ROI(`results/h1/gt_roi_rectified.json`)를 쓴다.
7. **파일 번호 ≠ 세트 번호**: `sample_5`=#6, `sample_6`=#5, `sample_8`=#9, `sample_9`=#8 (정답은 이미지 내용 기준).
8. **표본 한계**: 10장 모두 같은 양식이라 이미지 수 ≠ 독립 문서 수. 기존 10장은 개발에 이미 사용됨(hold-out 아님).

## 4. 아직 안 된 것

- E5 (Anchor ROI OCR): `taegu` 10장 ROI 미수신 — 공통 sample 1장 PoC만 있음 (`results/eval/common_sample/`).
- 신규 데이터(Dataset v1.0)에 대한 P0~P3 실행: 데이터 확정 후 위 명령을 그대로 재사용 가능.
