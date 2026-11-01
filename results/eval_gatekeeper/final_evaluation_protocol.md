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

CER = total or mean character error rate, with the aggregation rule stated explicitly.

sec/image must identify included processing stages.
OCR-only timing must not be represented as complete end-to-end latency.

## 5. Normalization

Existing tail evaluation:
- Unicode NFC
- Remove whitespace
- deposit_num: retain digits
- down_payment: normalize Korean money text using legacy form-specific cleanup
- Names: remove selected labels and punctuation
- Address: remove selected punctuation

IMPORTANT:
The new GT protocol uses numeric normalized money examples, including
contract_amount, while legacy tail evaluation compares Korean amount text
for down_payment.

The canonical money normalization policy MUST be resolved and frozen
before final cross-dataset comparison. Existing historical values must
not be silently combined with incompatible new normalized values.

Retain raw_text and normalized values with explicit normalization version.

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

P4:
- sample.jpg only
- Anchor found: 5/5
- Raw Exact Match: 5/5
- Not comparable to the common-10 results

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
