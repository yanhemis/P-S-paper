# Final Evaluation Protocol — 2026-11-01

Status: DRAFT — pending normalization policy and Dataset v1.0 handoff
Owner: dahye_cell_DetectionSurvey
Priority: 2026-11-01 team execution instructions

## 1. Evaluation Scope

P0: Raw Full OCR
P1: Rectified Full OCR
P2: GT ROI OCR
P3: bang Detected ROI + OCR
P4: taegu Anchor ROI + OCR (PoC if incomplete)

Report the existing common 10 images and new development data separately.
Evaluate holdout_test only after code and rules are frozen.

## 2. Canonical Field Keys

- address
- deposit
- contract_amount
- lessor_name
- lessee_name

Legacy mappings:
- deposit_num -> deposit
- down_payment -> contract_amount
- deposit_kor -> auxiliary; excluded from the five-field denominator

## 3. Denominators and Missing Predictions

- Count eligible (image_id, field) instances, not just images.
- Report image count, document_group_id count, and field-instance count separately.
- Do not treat repeated photographs of the same document as independent documents.
- A missing ROI or missing prediction counts as incorrect in end-to-end Field Accuracy.
- A missing image-level result must also remain in the expected denominator.
- Record execution failures separately from recognition/localization failures.
- Define exclusions for unusable or unreadable data before evaluation.

## 4. Metrics

Field Accuracy = exact matched eligible fields / all eligible fields.

Recorded ROI Presence = fields with recorded ROI results / eligible fields.

Conditional Field Accuracy = exact matched fields with recorded ROI / fields with recorded ROI.

Geometric ROI Coverage must be evaluated separately when GT boxes exist.
Do not label recorded ROI presence as verified geometric coverage.

### Geometric ROI Coverage (2026-11-08 protocol)

- GT BBox covers only the value text, not labels, cell borders, seals, signatures, or `(인)` marks.
- GT and predicted ROI must use original-image pixel coordinates.
- Coverage = Area(GT BBox intersection Predicted ROI) / Area(GT BBox).
- Covered means unrounded Coverage >= 0.90.
- Report both mean Coverage and Covered Rate.
- Exclude GT `bbox: null`, `unreadable`, and `not_present` from the ROI Coverage denominator.
- For an eligible field with no predicted ROI, Coverage = 0.
- P2: the GT BBox itself is the ROI, so Coverage = 1.0.
- P3: use the maximum Coverage across submitted ROI candidates.
- P4: evaluate only the algorithm-selected final ROI, never a GT-selected candidate.
- Excessively large ROIs require separate failure analysis; Coverage alone does not penalize them.
- ROI Coverage, OCR-conditioned accuracy, and end-to-end Field Accuracy must be reported separately.
- Report common-10 and new-development results separately before any combined table.

### Development GT Denominator Snapshot (2026-11-09)

Source: `origin/dataset-v1` commit `d4b32b6`.
Scope: Development only; not Holdout or final frozen Dataset v1.0.

| Set | Images | ROI Coverage eligible | BBox missing |
|---|---:|---:|---:|
| Common | 10 | 49 | 0 |
| Heewon | 6 | 30 | 0 |
| Tail | 3 | 0 | 15 |
| Total | 19 | 79 | 15 |

- Total five-field slots: 95.
- Text-eligible slots in the current GT snapshot: 94.
- `not_present`: 1; excluded from evaluation.
- Valid GT BBox: 79; eligible for ROI Coverage.
- `bbox: null` among text-eligible fields: 15; excluded from ROI Coverage only.
- Missing predicted ROI for a BBox-eligible field counts as Coverage = 0.
- Final text/E2E denominators also require GT, usable, and exclusion-policy validation.
- Recheck denominators when Tail BBoxes and Dataset v1.0 are finalized.
- Do not merge these provisional Development counts with Holdout results.

### Development GT Integrity Audit (2026-11-09)

Source: `origin/dataset-v1` commit `d4b32b6`.
Status: Automated Development checks passed; Dataset v1.0 is not frozen.

- Manifest images: 19; GT images: 19; IDs matched.
- Document groups: 13; all 19 images marked usable.
- All manifest splits were `development`.
- Image IDs, document group IDs, and five-field keys: 0 errors.
- Text-eligible fields: 94.
- Raw text / normalized GT completeness and money consistency: 0 issues.
- Monetary fields requiring manual review in this automated check: 0.
- Address and name normalization comparisons: 57 checked, 0 differences.
- These checks do not establish visual BBox accuracy, privacy/EXIF clearance,
  or Development/Holdout group disjointness.
- Revalidate after the final Dataset v1.0 handoff and record frozen versions.

### Updated Development GT Snapshot - ead8436

Source: `origin/dataset-v1` commit `ead8436`.
Status: Latest Development GT structural validation; not a dataset freeze.

- Images: 19; document groups: 13.
- Text-eligible fields: 94.
- ROI Coverage eligible fields: 94 (Common 49, Heewon 30, Tail 15).
- Missing BBoxes: 0; `not_present`: 1; invalid BBoxes: 0.
- Compared with `d4b32b6`: exactly 15 Tail BBoxes added.
- No non-BBox GT fields or values changed.
- Visual BBox accuracy and final Dataset v1.0 freeze remain unverified.
- Previous P3 audit (29/79) is historical Development evidence,
  not a score recalculated against this updated GT.
- Re-evaluate with frozen P3/P4 submissions before final reporting.

### P3/P4 실패 유형 집계 (2026-11-10)

상태: 제출된 실패 사유의 독립 집계 완료.
실패 원인의 독립적인 확정 또는 최종 Holdout 분석은 아님.

#### P3 - 하겸

출처: `origin/bang_`, `output/eval_v1/development/summary.json`.

| 실패 유형 | Common 10장 | Development 19장 |
|---|---:|---:|
| COORDINATE_ERROR | 13 | 23 |
| ROW_MERGE | 9 | 12 |
| TABLE_MISSING | 6 | 23 |

- 이미지별 `failure_reason`을 세미콜론으로 분리하여 집계.
- 표의 숫자는 제출된 실패 사유 기록 건수이며 Covered Rate가 아님.

#### P4 - 태구

출처: `origin/taegu`, `results/p4_handoff_verified_v1.zip`의 `summary.csv`.

| 제출된 분류 | Common 10장 기록 건수 |
|---|---:|
| ANCHOR_NOT_FOUND | 2 |
| VALUE_SELECTION_FAILED | 11 |
| OCR_TEXT_MISMATCH_OR_INCOMPLETE_VALUE_UNDETERMINED | 12 |
| GT_PRESENT_IN_OCR_TOKENS_SELECTION_OR_JOIN_ERROR | 1 |
| WHITESPACE_ONLY_MISMATCH | 2 |
| NONE | 22 |

- 총 50필드의 원본 실패 사유를 집계.
- `common_007/contract_amount`는 `not_present`이며
  제출 분류는 VALUE_SELECTION_FAILED.
- 따라서 P4 Raw Exact Accuracy 평가 분모는 49필드.
- 실패 유형은 진단용 분류이며 확정된 근본 원인을 뜻하지 않음.
- P3/P4는 실패 유형 정의와 평가 범위가 달라 단순 건수 비교 금지.
- 전체 Development 및 Holdout의 최종 failure breakdown은 별도 확정.

### P4 Development 19장 결과 집계 (GT 수정 확인 전)

상태: P4 동결 버전 Development 19장 제출물 집계.
가은·tail의 GT 수정본 정합성 확인 전이므로 최종 논문 수치로 확정하지 않음.

- 제출물: `p4_development_19_frozen.zip` (태구 전달).
- 보고된 코드 기준: `00e3e4e` (실제 실행 버전의 별도 확인 필요).
- 이미지 19장, 필드 95개.
- GT `not_present` 1개를 제외한 평가 가능 필드 94개.
- ROI Covered: 66/94 (70.21%).
- 평균 ROI Coverage: 0.722892 (GT `14f240a` 반영; 수정 전 0.731590).
- GT 변경: Development `tail_001`의 5필드 BBox만 수정, GT 텍스트는 동일.
- P3 `tail_001`: 후보 ROI가 5필드 모두 없으므로 Coverage 0 유지. Development 36/94 유지.
- P4 `tail_001`: Covered 개수 변동 없음. Development 66/94 유지.
- `tail_005`는 Holdout으로 Development 집계에서 제외.
- Raw Exact Accuracy: 29/94 (30.85%).
- Common 10장: ROI Covered 46/49, Raw Exact 22/49.
- 신규 Development 9장: ROI Covered 20/45, Raw Exact 7/45.
- GT가 유효하지만 ROI가 없는 필드는 Coverage 0으로 집계.
- Raw Exact Accuracy는 공식 정규화 기반 Field Accuracy와 구분.
- 제출 CSV 집계와 공식 GT BBox 좌표 재검증 결과를 구분하여 관리.
- 가은·tail 수정 GT 수령 후 기존 동결 ROI·OCR 결과와 정합성 확인.
- 기존 Common 10장 검증 기록과 OCR 캐시는 보존.
- Holdout 최종 평가 결과가 아님.

### P4 Common10 독립 검증 (2026-11-10, v6 중간 결과)

상태: P4 Common 10장 ROI Coverage 및 Raw Exact Accuracy 독립 검증 통과.
전체 Development 또는 Holdout 최종 평가 결과는 아님.

- GT 출처: `origin/dataset-v1` (`fb069e7`).
- P4 제출물: `results/p4_handoff_verified_v1.zip` (`063c656`).
- `sample_1.JPG`~`sample_10.JPG`와 `common_001`~`common_010` 매핑 검증 통과.
- 총 50필드 중 `common_007/contract_amount`는 `not_present`로 평가 제외.
- ROI Coverage: 46/49 (93.88%), 평균 Coverage 0.956120.
- P4는 필드별 최종 선택 `bbox` 1개만 사용.
- ROI 미생성: `common_010`의 임대인·임차인 성명 2건.
- ROI 좌표 구조 및 이미지 범위 오류: 0건.
- Raw Exact Accuracy: 22/49 (44.90%).
- 공식 GT 원문 불일치 및 제출 정확도 플래그 오류: 0건.
- ROI 미생성은 유효한 GT에 대해 Coverage 0으로 처리.
- Raw Exact Accuracy는 정규화 기반 최종 Field Accuracy와 별도 지표.
- 실패 유형의 상세 독립 검증 및 전체 Development 평가는 별도 진행.
- Holdout 평가 결과로 사용하지 않음.

### P3 Development Independent Audit - Updated GT (2026-11-10)

Status: Independent P3 Development ROI Coverage verification PASS.
This is not a Holdout evaluation.

- GT source: `origin/dataset-v1` at `ead8436`.
- P3 output source: `origin/bang_` at `91fb3ee`.
- P3 reported frozen code commit: `55c30b0`.
- Input: `output/eval_v1/development/roi_candidates.json`.
- Method: recomputed original-coordinate ROI Coverage from GT BBoxes
  and each field's ROI candidates; used maximum candidate Coverage.
- Covered threshold: unrounded Coverage >= 0.90.
- Common: 21/49 covered; mean Coverage 0.661941.
- Heewon: 8/30 covered; mean Coverage 0.457083.
- Tail: 7/15 covered; mean Coverage 0.619876.
- Overall: 36/94 covered (38.30%); mean Coverage 0.589848.
- Evaluated images: 19; missing prediction images: 0.
- Excluded from ROI Coverage: 1 `not_present` field.
- Result: Matches P3's reported 36/94 and rounded mean 0.590.
- Previous 29/79 result remains a historical snapshot.
- Failure taxonomy, E2E metrics, and final Holdout protocol
  are not verified by this ROI Coverage check.

### P3 Development Independent Audit (2026-11-09)

Status: Verified Development result; NOT a final frozen or Holdout score.

Sources:
- GT: `origin/dataset-v1` commit `d4b32b6`.
- P3 candidates: `origin/bang_` commit `4f48f6e`.
- Independent evaluator: `scripts/eval_gatekeeper/roi_coverage_evaluator.py`.
- GT `manifest.csv` and `field_gt.json` SHA-256 hashes matched the P3 report.

| Set | Images | Eligible | Covered | Covered Rate | Mean Coverage |
|---|---:|---:|---:|---:|---:|
| Common | 10 | 49 | 21 | 42.86% | 66.19% |
| Heewon | 6 | 30 | 8 | 26.67% | 45.71% |
| Tail | 3 | 0 | N/A | N/A | N/A |
| Total | 19 | 79 | 29 | 36.71% | 58.41% |

Independent recalculation:
- Covered count: 29/79, matching the submitted P3 report.
- Mean Coverage: 0.584147, matching reported 0.5841 within 0.0001.
- Excluded ROI Coverage fields: 16 (15 BBox-null, 1 not_present).
- The omitted `common_007/contract_amount` candidate entry was `not_present`.
- No Covered-status differences were caused by four-decimal rounding.
- Evaluated submitted ROI candidates using the maximum geometric Coverage.
- This does not validate visual BBox annotation accuracy or approve a freeze.
- Re-evaluate after final Tail BBoxes and frozen P3 outputs are supplied.
- Do not mix this Development snapshot with Holdout or historical OCR metrics.

### CER Calculation Policy

Historical tail evaluation:
- Per-field CER = Levenshtein(pred_norm, gt_norm) / max(len(gt_norm), 1).
- Mean CER = arithmetic mean of per-field CER values (macro-average).
- The historical common-10 results use this macro-average definition.

Final evaluation requirements:
- Use the same eligible (image_id, field) denominator as Field Accuracy.
- Missing image-level or field-level predictions must not be silently excluded.
- For an eligible field with a non-empty GT, a missing prediction is treated as an empty string (CER = 1.0).
- Exclude fields with legitimately absent GT before evaluation.
- Calculate CER using one explicitly versioned normalization policy.
- Monetary Field Accuracy uses numeric KRW normalization.
- Monetary CER uses text-level normalization for BOTH GT and prediction, regardless of whether numeric conversion succeeds.
- Monetary text normalization removes permitted whitespace and currency markers without correcting OCR errors.
- Example: GT "오십만", prediction "소십만 원" -> text CER = 1/3.
- Example: GT "오백만", prediction "1백만 원" -> text CER = 1/3, numeric Field Accuracy = incorrect.
- Missing predictions use an empty string, giving CER = 1.0 for non-empty GT.
- Do not mix numeric-string CER with text-level CER in the same aggregate.
- Recalculate final CER using one versioned text-normalization policy across pipelines.
- Report raw OCR CER separately if needed; do not mix raw-text CER with numeric-normalized CER.
- CER may exceed 1.0 when insertion errors are numerous.
- Do not silently combine historical CER values with results recalculated under a different normalization policy.

The final evaluator must generate failure records for missing image-level results instead of skipping them.

sec/image must identify included processing stages.
OCR-only timing must not be represented as complete end-to-end latency.

## 5. Normalization

### 5.1 Canonical Field Keys

The five evaluation fields are:
- address
- deposit
- contract_amount
- lessor_name
- lessee_name

Legacy field mappings:
- deposit_num -> deposit
- down_payment -> contract_amount
- deposit_kor -> auxiliary; excluded from the five-field denominator

### 5.2 Monetary Amount Normalization

Proposed common policy:
- Normalize both deposit and contract_amount into numeric KRW strings.
- Preserve the original OCR text and GT raw_text separately.
- Remove permitted currency markers, whitespace, and thousands separators.
- Convert valid Korean monetary expressions into integer KRW values.
- Do not automatically correct OCR recognition errors.
- Return None for invalid or unparseable amounts.
- Treat missing or unparseable predictions as incorrect in Field Accuracy.

Examples:
- 일억 -> 100000000
- 일천만 -> 10000000
- 일천팔백만 -> 18000000
- 금 오백만원정 -> 5000000
- 1백만 -> 1000000
- 소십만 -> None
- 일벽만 -> None

Implementation:
scripts/eval_gatekeeper/amount_normalizer.py

### 5.2.1 Raw OCR Input Policy (Draft)

- Final evaluation must start from pred_raw, not historical pred_norm.
- Preserve the original prediction before preprocessing.
- Remove only explicitly permitted contract-form labels and currency markers.
- Do not remove arbitrary non-digit characters to recover a plausible amount.
- OCR substitutions such as O -> 0 or ㅇ -> 0 are not automatically allowed.
- Numeric grouping separators must follow one documented validation rule.
- If Korean and numeric monetary expressions appear together, validate them independently.
- Do not select whichever expression matches the GT.
- Conflicting or partially corrupted expressions require a predefined handling rule.
- Empty predictions count as incorrect; distinguish missing ROI records from empty OCR output.
- Preserve legacy pred_norm only for reproducing historical evaluations.

This policy is provisional until parsing cases and evaluator tests are completed.

### 5.3 Verified Tests

- Amount normalization unit tests: 20/20 passed.
- Additional edge-case validation: 7/7 passed.
- Fixed invalid Korean amount parsing: "일억만" now returns None.
- Existing common-10 contract_amount GT conversion: 9/9 succeeded.
- Numeric contract_amount evaluation:

| Pipeline | Correct | Invalid | Mismatch | Missing |
|---|---:|---:|---:|---:|
| P0 | 6/9 | 2 | 1 | 0 |
| P1 | 5/9 | 3 | 1 | 0 |
| P2 | 7/9 | 2 | 0 | 0 |
| P3 | 0/9 | 9 | 0 | 0 |

The P3 invalid count includes empty predictions and predictions
containing unrelated text. It must not be interpreted entirely
as character-recognition failures.

### 5.4 Historical Results and Remaining Decisions

The historical P0-P3 common-10 scores used legacy normalization
and must remain unchanged as previously reported.

The monetary normalization implementation has been tested,
but the team-wide final evaluation protocol is not yet frozen.

Before the final evaluation:
- Confirm the same monetary policy for every pipeline.
- Verify address and name normalization against the existing evaluator.
- Specify the CER aggregation and invalid-prediction policy.
- Recalculate full five-field results under one normalization version.
- Record the normalization version and evaluation code commit SHA.

Do not combine historical CER values with newly normalized CER
without clearly distinguishing their calculation rules.

Detailed audit:
results/eval_gatekeeper/amount_normalization_audit.md

### 5.5 Common Evaluator Verification (2026-11-05)

Implementation:
- scripts/eval_gatekeeper/common_evaluator.py
- scripts/eval_gatekeeper/test_common_evaluator.py

The DRAFT common evaluator was tested on the historical common-10
development set using raw OCR predictions.

| Pipeline | Eligible Fields | Correct | Field Accuracy | DRAFT Mean CER |
|---|---:|---:|---:|---:|
| P0 | 49 | 29 | 59.2% | 0.1509 |
| P1 | 49 | 31 | 63.3% | 0.1222 |
| P2 | 49 | 31 | 63.3% | 0.1193 |
| P3 | 49 | 13 | 26.5% | 1.0238 |

Verification:
- All four pipelines retained the same 49-field denominator.
- Field Accuracy matched the historical common-10 results.
- The new CER uses a different text-normalization policy and must
  not be substituted for historical CER without clear labeling.
- Removing one correct prediction retained 49 eligible fields
  and reduced the correct count from 29 to 28.
- Removing all five predictions for one image retained 49 eligible
  fields and recorded five missing predictions.
- Duplicate prediction records are rejected.
- Five automated evaluator tests passed.
- P3 contained 27 empty predictions, 13 correct predictions,
  and 9 non-empty incorrect predictions.

Monetary parsing remains DRAFT:
- Contract-form labels may be removed according to explicit rules.
- Numeric commas and periods between digit groups may be removed.
- OCR character substitutions are not automatically corrected.
- When both Korean and numeric amounts are present, they must
  independently parse and agree.
- The permitted preprocessing rules require final review before
  protocol freeze.

These results do not constitute Dataset v1.0 or holdout evaluation.

## 6. Verified Common-10 Baselines

| Pipeline | Field Accuracy | Mean CER |
|---|---|---|
| P0 | 29/49 (59.2%) | 0.141 |
| P1 Rectified | 31/49 (63.3%) | 0.120 |
| P2 GT ROI | 31/49 (63.3%) | 0.117 |
| P3 Detected ROI pad25 | 13/49 (26.5%) | 0.985 |

All four pipelines use the same 49 unique image-field instances.
Normalized GT values matched across all 49 instances.

P3:
- Recorded ROI field presence: 22/49 (44.9%)
- Missing ROI records: 27/49
- Conditional Field Accuracy: 13/22 (59.1%)
- Missing-ROI correct predictions: 0/27

P4 (sample.jpg only):

Initial Anchor Mapping PoC:
- Anchor found: 5/5
- Raw Exact Match: 5/5

Latest ROI Re-OCR Evaluation (2026-11-04):
- ROI generated: 5/5
- GT bounding boxes fully contained in detected ROIs: 5/5
- Raw Exact Match: 4/5 (80.0%)
- Failed field: address
- Observed error: missing Korean character "층"
- Recorded total time: 11.9423 sec (first-pass OCR cache reused)

Limitations:
- The initial PoC and latest ROI re-OCR use different processing paths.
- The latest result covers only one image and five fields.
- The recorded runtime is not a verified uncached end-to-end latency.
- P4 results must not be directly compared with P0-P3 common-10 results.

Detailed audit:
results/eval_gatekeeper/p4_e2e_sample_audit.md

## 7. Important Evaluation Limitations

- P0/P1 historical field assignment used GT ROI coordinates.
  Do not claim GT-independent end-to-end field extraction.
- P3 recorded ROI presence is not proven geometric ROI Coverage.
- The existing tail evaluator can skip images absent from predictions;
  final evaluation must account for these image-level failures.
- P2 requires usable GT ROI boxes. If absent, report P2 as unavailable
  for those instances rather than inventing oracle ROI results.
- Preserve coordinate-frame consistency between predictions and GT.
- Historical numbers are not automatically final numbers under
  a revised normalization policy.

## 8. Failure Breakdown

P3 expected categories:
TABLE_MISSING, ROW_MERGE, COLUMN_MERGE, CELL_MERGE,
WRONG_MAPPING, COORDINATE_ERROR.

P4 expected categories:
ANCHOR_NOT_FOUND, WRONG_ANCHOR, MIXED_ROWS,
ROI_TOO_LARGE, ROI_TOO_SMALL, OCR_FAILURE.

Distinguish field ROI missing, wrong ROI/mapping, OCR mismatch,
and technical execution failure.

## 9. Dataset v1.0 and Holdout Rules

Dataset Manager: Gaeun
Data contributors: heewon, tail

Required inputs:
- development images
- manifest.csv
- field_gt.json
- document_group_id
- usable and split metadata

Development and holdout_test must be disjoint by document_group_id.
Existing common 10 images are not untouched holdout.

Do not access or evaluate holdout_test until bang/taegu code,
parameters, and this evaluation protocol are frozen and versioned.

## 10. Remaining Work

- Resolve and freeze the canonical money normalization policy.
- Receive and validate Dataset v1.0 development inputs.
- Receive bang/taegu outputs and code-freeze commit SHAs.
- Produce separate common-10 and new-data comparison tables.
- Produce failure breakdown and comparable stage-specific timing.
- Run untouched holdout evaluation once after freeze.
- Publish final paper-ready results with explicit denominators.

Current blocker:
Dataset v1.0 development package has not yet been received.
