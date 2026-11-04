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
