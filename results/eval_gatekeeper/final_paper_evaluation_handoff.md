# P0-P4 Final Evaluation Gatekeeper Handoff

Date: 2026-11-12
Owner: dahye_cell_DetectionSurvey
Status: FINAL EVIDENCE-BASED GATEKEEPER HANDOFF
Scope: Verified evaluation evidence and publication-readiness decisions.
This document does not certify unavailable live end-to-end measurements.

## 1. Frozen evaluation definitions

Dataset GT: `origin/dataset-v1`, commit `14f240a`.
Common evaluation code: `e46062a`.
Team-wide normalization policy: not yet formally frozen.

Canonical fields:
- `address`
- `deposit`
- `contract_amount`
- `lessor_name`
- `lessee_name`

Legacy field mappings:
- `deposit_num` -> `deposit`
- `down_payment` -> `contract_amount`
- `deposit_kor` is auxiliary and excluded.

Development:
- Common: 10 images, 10 document groups, 49 eligible fields.
- New: 9 images, 3 document groups, 45 eligible fields.
- Combined: 19 images, 13 document groups, 94 eligible fields.
- `common_007/contract_amount` is `not_present` and excluded.

Repeated photographs within one `document_group_id` are not
independent document samples.

ROI Coverage:
`Area(GT intersection ROI) / Area(GT)` on original image coordinates.
Covered threshold: unrounded coverage >= 0.90.

P3: maximum coverage among independently generated ROI candidates.
P4: coverage of the one final ROI selected by the algorithm.
No ROI with valid GT BBox: coverage 0.
`bbox:null`, `unreadable`, `not_present`: excluded from
the ROI Coverage denominator.

E2E Field Accuracy:
- All eligible field instances remain in the denominator.
- ROI generation failure or missing prediction counts as incorrect.
- A successful ROI is not automatically a correct OCR prediction.
- OCR-conditioned accuracy must be reported separately from
  ROI Coverage and E2E Field Accuracy.

Monetary Field Accuracy uses numeric KRW normalization.
CER uses text normalization on both GT and predictions.
Mean field CER is the arithmetic mean of per-field CER values.
Do not mix legacy CER with newly normalized CER.

## 2. Official Common10 ROI Coverage comparison

| Pipeline | Image correction | ROI source | Mean ROI Coverage | Covered / eligible | Covered rate |
|---|---|---|---:|---:|---:|
| P0 | No | Full page / GT-assisted field assignment | N/A | N/A | N/A |
| P1 | Yes | Full page / GT-assisted field assignment | N/A | N/A | N/A |
| P2 | Fixed | Oracle GT ROI | 1.000000 | 49/49 | 100.00% |
| P3 | Fixed | bang detected ROI candidates | 0.661941 | 21/49 | 42.86% |
| P4 | Fixed | taegu final anchor ROI | 0.956120 | 46/49 | 93.88% |

P2 is an oracle upper bound, not an independently detected ROI.
P3 and P4 use different, explicitly declared ROI-selection policies.
Only this Common10 set is an official direct P3/P4 comparison.

## 3. New Development and combined results

| Subset | Pipeline | Eligible fields | Covered | Covered rate | Mean coverage |
|---|---|---:|---:|---:|---:|
| New 9 images | P3 | 45 | 15 | 33.33% | 0.511347 |
| Full Development 19 | P3 | 94 | 36 | 38.30% | 0.589848 |
| New 9 images | P4 | Outside official scope | N/A | N/A | N/A |
| Separate Development19 ZIP | P4 | 94 | 66 | 70.21% | 0.722892 |

The separate P4 Development19 ZIP is reference evidence only,
not an expansion of the official P4 Common10 evaluation scope.

## 4. Common10 normalized accuracy and CER: REFERENCE ONLY

All scores below were recalculated against the same final GT
and normalized with the existing common evaluator.
They do not share a verified, equivalent live pipeline execution.

| Pipeline | Correct / eligible | Field Accuracy | Mean field CER |
|---|---:|---:|---:|
| P0 historical predictions | 29/49 | 59.18% | 0.577415 |
| P1 historical predictions | 29/49 | 59.18% | 0.555744 |
| P2 historical predictions | 30/49 | 61.22% | 0.554512 |
| P3 historical predictions | 12/49 | 24.49% | 1.156608 |
| P4 cached handoff predictions | 24/49 | 48.98% | 0.339115 |

P0/P1 legacy field assignment used GT geometry.
P2 used oracle GT ROI.
P3 entries are historical OCR predictions, not established
frozen P3 live E2E predictions.
P4 Common10 used `cached_ocr`, not a newly verified live OCR run.

P4 Raw Exact: 22/49 (44.90%), a different metric.
P4 normalized reference: 24/49 (48.98%).
P4 cached reference has 12 empty predictions and 8 invalid
monetary prediction findings; do not add those counts together
as if they were disjoint error categories.

These reference scores MUST NOT populate a table labeled
"final comparable live E2E performance".

## 5. Final E2E, OCR-conditioned accuracy, and timing

| Pipeline | Official normalized live E2E accuracy | OCR-conditioned accuracy | Comparable live E2E CER | Comparable end-to-end sec/image |
|---|---|---|---|---|
| P0 | Not established | Not established | Not established | Not established |
| P1 | Not established | Not established | Not established | Not established |
| P2 | Not independent E2E (GT oracle) | Not established | Not established | Not established |
| P3 | Not established | Not established | Not established | Not established |
| P4 | Not established (cached OCR handoff) | Not established | Not established | Not established |

Historical runtime observations, NOT final comparable E2E timing:

| Pipeline | Archived sec/image | Limitation |
|---|---:|---|
| P0 | 29.318067 | Historical measurement; full E2E equivalence unverified |
| P1 | 31.126809 | Historical measurement; full E2E equivalence unverified |
| P2 | 0.925516 | ROI OCR sum, excluding cell/ROI detection |
| P3 historical | 0.951126 | Historical stage/cache context unverified |
| P3 Development structure | 1.178000 | Structure restoration stage only, excludes OCR |
| P4 | Not established | Official handoff uses cached OCR |

No final E2E number may be inferred from ROI Coverage,
OCR-only timing, or cached predictions.

## 6. Failure breakdown

P3 Common10 diagnostic reason occurrences:
- `COORDINATE_ERROR`: 13
- `ROW_MERGE`: 9
- `TABLE_MISSING`: 6

P3 New9 diagnostic reason occurrences:
- `COORDINATE_ERROR`: 10
- `ROW_MERGE`: 3
- `TABLE_MISSING`: 17

P4 Common10 diagnostic field classifications:
- `ANCHOR_NOT_FOUND`: 2
- `VALUE_SELECTION_FAILED`: 11
- `OCR_TEXT_MISMATCH_OR_INCOMPLETE_VALUE_UNDETERMINED`: 12
- `GT_PRESENT_IN_OCR_TOKENS_SELECTION_OR_JOIN_ERROR`: 1
- `WHITESPACE_ONLY_MISMATCH`: 2
- `NONE`: 22

P3 counts are reason occurrences, not mutually exclusive
field-level failures. P4 has 50 diagnostic field records,
including the one `not_present` field.
The two taxonomies are useful for descriptive error analysis,
not directly comparable per-field failure rates.
Diagnostic labels are not independently proven root causes.

## 7. GT and execution provenance

Dataset GT commit: `14f240a` (verified).
Common evaluator/amount normalizer: `e46062a`.

P0/P2 archived result history:
- `results/eval/field_results.json` added at `1e9bbe2`
- Updated at `a92c1c8` with related evaluation/ROI code changes

P1:
- `results/h1/eval_rectified/field_results.json` added
  at `45abadb` with related H1 code changes

P0/P2 reviewed code defaults:
- `PAD_RATIO=0.25`
- `WHOLE_BOX_RATIO=0.5`
- `BORDER_PX=32`

P1 reviewed defaults:
- `LINE_PAD=0.15`
- `NO_WHOLE_BOX=1.01`

Actual historical execution arguments remain unverified.

P3:
- Reported code-freeze commit `55c30b0` exists.
- ROI evaluator script SHA-256 matches the archived result.
- Archived result metadata records `frozen_commit=11af316`.
- Archived result GT hash matches pre-correction `6c7180f`.
- Final GT `14f240a` ROI Coverage was independently rechecked.
- Matching hashes do not establish full live execution provenance.

P4:
- Official handoff at `063c656`, Common10 only.
- All ten official `final_fields.json` records use `cached_ocr`.
- `00e3e4e` is CODE_BASELINE_ONLY, not verified full-run provenance.
- Separate Development19 submission remains reference only.

## 8. Holdout procedural exception

Holdout package release: 2026-11-10 16:04 KST,
before the P3/P4 code freezes.

P3 code freeze: 2026-11-10 16:42 KST.
A single P3 Holdout run at approximately 16:43 and no
subsequent retuning were reported and recorded.

P3 Holdout ROI Coverage: 3/30 (10.00%).
Final GT `14f240a` recheck preserved the count.

Classification: supplementary validation with a
release-before-freeze procedural exception.
It is NOT an untouched independent final Holdout.
No further Holdout runs or algorithm changes are authorized
by this evaluation handoff.

## 9. Publication-ready claim and final decision

Supported ROI-only finding:
"On the 10 common Development images (49 eligible fields),
P3 achieved ROI Coverage 21/49 (42.86%) using maximum
coverage among detected candidates, whereas P4 achieved
46/49 (93.88%) using its single algorithm-selected final ROI.
Both were assessed against the final GT under the declared
coverage threshold of 0.90."

Gatekeeper decision:
- ROI Coverage tables: publication candidates, subject to
  final dataset/evaluation-policy sign-off.
- Common10 normalized accuracy/CER: diagnostic references only.
- Separate P4 Development19: reference only.
- P3 Holdout 3/30: supplementary only with explicit exception.
- Final unified P0-P4 E2E Field Accuracy, CER and sec/image:
  NOT established from currently verified comparable evidence.

Remaining independent blockers:
1. Team-wide final normalization/evaluation-policy freeze.
2. Final dataset-wide freeze approval and file-hash inventory.
3. Comparable independent live-run provenance for final E2E,
   OCR-conditioned accuracy and end-to-end timing.

This is the completed evidence-based Gatekeeper handoff.
It does not falsely claim that the requested fully populated
final live-E2E paper table is already certified.

Sources:
- `results/eval_gatekeeper/final_evaluation_protocol.md`
- `results/eval_gatekeeper/p0_p4_comparison_template.md`
- `origin/dataset-v1` at `14f240a`
- `origin/tail` archived Common10 evaluations
- P3 archived Development results at `55c30b0`
- `origin/taegu:results/p4_handoff_verified_v1.zip`