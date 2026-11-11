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
Document groups: TBD
Text/E2E eligible fields: TBD
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
Document groups: TBD
Text/E2E eligible fields: TBD
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

## 4. Required separate metrics

| Set | Pipeline | Text/E2E denominator | ROI Coverage denominator | ROI-generated fields | OCR-conditioned correct/denominator | E2E correct/denominator | CER denominator |
|---|---|---|---|---|---|---|---|
| Common | P0-P4 (each separately) | TBD | TBD/N/A | TBD/N/A | TBD/N/A | TBD | TBD |
| New Development | P0-P4 (each separately) | TBD | TBD/N/A | TBD/N/A | TBD/N/A | TBD | TBD |

## 5. Failure breakdown

| Set | Pipeline | Failure reason | Count | Interpretation |
|---|---|---|---|---|
| Common | P3/P4 | TBD | TBD | TBD |
| New Development | P3/P4 | TBD | TBD | TBD |

Track ROI missing, wrong mapping, OCR error, and execution error separately.

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

- [ ] Dataset and split finalized
- [ ] P0-P4 field keys and normalization verified
- [ ] Development denominators finalized
- [ ] P3/P4 frozen commits recorded
- [ ] Frozen pipeline outputs received
- [ ] Common and new Development comparison tables filled
- [ ] Failure breakdown and timing verified
- [ ] Holdout released and evaluated once after freeze
- [ ] Final paper-ready figures reviewed
