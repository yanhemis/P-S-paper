# P0-P4 Final Evaluation Comparison Template

Status: DRAFT - verified ROI metrics entered; final E2E/CER/timing pending
Owner: dahye_cell_DetectionSurvey

References:
- 04_data_collection_gt_protocol.md, sections 7 and 10
- 05_current_team_tasks_20261101.md, section 4

## 1. Evaluation versions

| Item | Version / Commit |
|---|---|
| Dataset GT | `origin/dataset-v1` / `14f240a` (verified) |
| Dataset-wide freeze / file hashes | TBD |
| Evaluation code commit | TBD |
| Normalization policy version | TBD |
| P0-P2 code and parameters | TBD |
| P3 code freeze | `55c30b0` (reported); parameters/provenance TBD |
| P4 code freeze | `00e3e4e` (CODE_BASELINE_ONLY) |
| P4 official Common10 handoff | v6 handoff at `063c656`; exact frozen-code provenance not established |

TBD means not yet verified. Do not substitute Raw Exact for normalized E2E Field Accuracy.

## 2. Common 10 images

Images: 10
Document groups: 10
Text/E2E eligible fields: 49
ROI Coverage eligible fields: 49 (one `not_present` excluded)

| Pipeline | Image correction | ROI source | Mean ROI Coverage | Covered Rate (>=0.90) | E2E Field Accuracy | CER | sec/image |
|---|---|---|---|---|---|---|---|
| P0 | No | Full page | N/A | N/A | TBD | TBD | TBD |
| P1 | Yes | Full page | N/A | N/A | TBD | TBD | TBD |
| P2 | Fixed | GT ROI | 1.000000 | 49/49 (100%) | TBD | TBD | TBD |
| P3 | Fixed | bang Detected ROI | 0.661941 | 21/49 (42.86%) | TBD | TBD | TBD |
| P4 | Fixed | taegu Anchor ROI | 0.956120 | 46/49 (93.88%) | TBD | TBD | TBD |

P4 Common10 Raw Exact: 22/49 (44.90%); diagnostic only, not normalized E2E Field Accuracy.

## 3. New Development images (excluding common 10)

Images: 9
Document groups: 3
Text/E2E eligible fields: 45
ROI Coverage eligible fields: 45

| Pipeline | Image correction | ROI source | Mean ROI Coverage | Covered Rate (>=0.90) | E2E Field Accuracy | CER | sec/image |
|---|---|---|---|---|---|---|---|
| P0 | No | Full page | N/A | N/A | TBD | TBD | TBD |
| P1 | Yes | Full page | N/A | N/A | TBD | TBD | TBD |
| P2 | Fixed | GT ROI | 1.000000 | 45/45 (100%) | TBD | TBD | TBD |
| P3 | Fixed | bang Detected ROI | 0.511347 | 15/45 (33.33%) | TBD | TBD | TBD |
| P4 | Fixed | taegu Anchor ROI | N/A (official scope: Common10) | N/A | N/A | N/A | N/A |

P4 Development 19-image submission is preserved as a provisional reference,
not used as an official new-Development comparison result.

## 3A. Historical Common10 field accuracy audit

Read-only verification of `origin/tail` field evaluation outputs.
These values are historical normalized exact-match audit results,
NOT final GT-independent E2E Field Accuracy.

| Pipeline | Exact Match | Accuracy | Evaluation status |
|---|---:|---:|---|
| P0 Full OCR | 29/49 | 59.18% | Historical, GT-assisted field assignment |
| P1 Rectified Full OCR | 31/49 | 63.27% | Historical, GT-assisted field assignment |
| P2 GT ROI OCR | 31/49 | 63.27% | Historical GT ROI reference |
| P3 Detected ROI OCR | 13/49 | 26.53% | Historical, not frozen P3 E2E |

- All four results: 10 images, 49 unique image-field pairs, zero duplicates.
- P0/P2 source: `origin/tail:results/eval/field_results.json`.
- P1 source: `origin/tail:results/h1/eval_rectified/field_results.json`.
- P3 source: `origin/tail:results/eval/detected_bang_pad25/field_results.json`.
- Official five fields only; `deposit_kor` excluded.
- Do not place these values in final E2E Field Accuracy cells without methodology verification.
- P4 Common10 Raw Exact 22/49 is separately recorded and is not normalized Field Accuracy.

### Historical Common10 CER and reported timing

These are read-only historical results from `origin/tail`, not final
same-version P0-P4 CER or end-to-end latency measurements.

| Pipeline | Mean field CER | Reported sec/image | Status |
|---|---:|---:|---|
| P0 Full OCR | 0.140964 | 29.318067 | Historical reference |
| P1 Rectified Full OCR | 0.119981 | 31.126809 | Historical reference |
| P2 GT ROI OCR | 0.116765 | 0.925516 | Historical reference |
| P3 Detected ROI OCR | 0.985010 | 0.951126 | Historical reference |

- Each CER is the arithmetic mean of 49 stored field-level CER values.
- These values are not character-count-weighted corpus CER.
- P3 here refers to historical Detected ROI OCR, not frozen P3.
- Timing values are as recorded by the original evaluations.
- Timing stage boundaries, preprocessing, and cache use are not yet verified.
- Do not populate final CER or sec/image comparison cells from these values.
- P4 comparable CER and timing remain unverified.

## 4. Required separate metrics

| Set | Pipeline | Text/E2E denominator | ROI Coverage denominator | ROI-generated fields | OCR-conditioned correct/denominator | E2E correct/denominator | CER denominator |
|---|---|---|---|---|---|---|---|
| Common | P0-P4 (each separately) | 49 | TBD/N/A | TBD/N/A | TBD/N/A | TBD | TBD |
| New Development | P0-P3 (P4 outside official scope) | 45 | TBD/N/A | TBD/N/A | TBD/N/A | TBD | TBD |

## 5. Failure breakdown

Counts below are submitted diagnostic reason records, not independently
proven root causes or directly comparable failure rates.

| Set | Pipeline | Submitted failure reason | Count |
|---|---|---|---:|
| Common 10 | P3 | COORDINATE_ERROR | 13 |
| Common 10 | P3 | ROW_MERGE | 9 |
| Common 10 | P3 | TABLE_MISSING | 6 |
| New Development 9 | P3 | COORDINATE_ERROR | 10 |
| New Development 9 | P3 | ROW_MERGE | 3 |
| New Development 9 | P3 | TABLE_MISSING | 17 |
| Common 10 | P4 | ANCHOR_NOT_FOUND | 2 |
| Common 10 | P4 | VALUE_SELECTION_FAILED | 11 |
| Common 10 | P4 | OCR_TEXT_MISMATCH_OR_INCOMPLETE_VALUE_UNDETERMINED | 12 |
| Common 10 | P4 | GT_PRESENT_IN_OCR_TOKENS_SELECTION_OR_JOIN_ERROR | 1 |
| Common 10 | P4 | WHITESPACE_ONLY_MISMATCH | 2 |
| Common 10 | P4 | NONE | 22 |

- P3 source: `origin/bang_:output/eval_v1/development/summary.json`.
- P3 New Development counts = Development 19 counts minus Common 10 counts.
- P3 counts represent submitted reason occurrences, not unique failed fields.
- P4 source: `origin/taegu:results/p4_handoff_verified_v1.zip`, `summary.csv`.
- P4 counts cover 50 submitted field rows, including one `not_present` GT field.
- P4 ROI Coverage and Raw Exact denominators exclude that GT field (49).
- `NONE` is not a failure; other labels are diagnostic, not proven causes.
- P3 and P4 differ in evaluation scope and reason definitions.
- P4 New Development is outside the agreed official comparison scope.
- Holdout remains supplementary due to the release-before-freeze exception.

## 6. Evaluation rules

- Canonical fields: address, deposit, contract_amount, lessor_name, lessee_name.
- Preserve missing predictions and execution failures in the E2E denominator.
- ROI Coverage = Area(GT intersection predicted ROI) / Area(GT).
- Covered only if unrounded Coverage >= 0.90.
- Exclude bbox-null, not_present, and unreadable GT from ROI Coverage denominator.
- Missing ROI for a BBox-eligible field has Coverage 0.
- P3 takes maximum Coverage across submitted ROI candidates.
- P4 evaluates the algorithm-selected final ROI only.
- P2 Coverage is 1.0 only for valid GT BBox instances.
- Report OCR-conditioned accuracy separately from E2E accuracy.
- Record image count, document-group count, and field count independently.
- Use one frozen normalization policy for all pipelines.
- Record which stages are included in sec/image and whether caches were used.
- Preserve historical Common 10 results separately from newly recalculated results.
- Do not use this template to introduce any Holdout results before freeze and release.

## 7. Final evaluation status

- [x] Final GT version confirmed: 14f240a
- [x] Development split and document-group counts confirmed
- [ ] Dataset-wide freeze hashes and all pipeline provenance verified
- [ ] Same-version P0-P4 normalization and E2E accuracy verified
- [x] Development denominators finalized: Common 49, New 45
- [x] P3/P4 official-scope ROI Coverage recorded
- [x] P3/P4 diagnostic failure breakdown recorded
- [x] Historical accuracy, CER and timing references separated
- [ ] Final comparable CER and end-to-end timing verified
- [x] Holdout release-before-freeze exception documented; P3 3/30 supplementary only
- [ ] Final paper-ready figures reviewed and approved
