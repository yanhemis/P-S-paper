# P0-P4 Final Evaluation Comparison Template

Status: TEMPLATE - waiting for frozen pipeline outputs
Owner: dahye_cell_DetectionSurvey

References:
- 04_data_collection_gt_protocol.md, sections 7 and 10
- 05_current_team_tasks_20261101.md, section 4

## 1. Evaluation versions

| Item | Version / Commit |
|---|---|
| Dataset v1.0 | TBD |
| GT / manifest hashes | TBD |
| Evaluation code commit | TBD |
| Normalization policy version | TBD |
| P0-P2 code and parameters | TBD |
| P3 frozen commit and parameters | TBD |
| P4 frozen commit and parameters | TBD |

TBD means not yet verified. Historical scores must not be treated as final scores.

## 2. Common 10 images

Images: TBD
Document groups: TBD
Text/E2E eligible fields: TBD
ROI Coverage eligible fields: TBD

| Pipeline | Image correction | ROI source | Mean ROI Coverage | Covered Rate (>=0.90) | E2E Field Accuracy | CER | sec/image |
|---|---|---|---|---|---|---|---|
| P0 | No | Full page | N/A | N/A | TBD | TBD | TBD |
| P1 | Yes | Full page | N/A | N/A | TBD | TBD | TBD |
| P2 | Fixed | GT ROI | 100% of eligible GT BBoxes | 100% of eligible GT BBoxes | TBD | TBD | TBD |
| P3 | Fixed | bang Detected ROI | TBD | TBD | TBD | TBD | TBD |
| P4 | Fixed | taegu Anchor ROI | TBD | TBD | TBD | TBD | TBD |

## 3. New Development images (excluding common 10)

Images: TBD
Document groups: TBD
Text/E2E eligible fields: TBD
ROI Coverage eligible fields: TBD

| Pipeline | Image correction | ROI source | Mean ROI Coverage | Covered Rate (>=0.90) | E2E Field Accuracy | CER | sec/image |
|---|---|---|---|---|---|---|---|
| P0 | No | Full page | N/A | N/A | TBD | TBD | TBD |
| P1 | Yes | Full page | N/A | N/A | TBD | TBD | TBD |
| P2 | Fixed | GT ROI | 100% of eligible GT BBoxes | 100% of eligible GT BBoxes | TBD | TBD | TBD |
| P3 | Fixed | bang Detected ROI | TBD | TBD | TBD | TBD | TBD |
| P4 | Fixed | taegu Anchor ROI | TBD | TBD | TBD | TBD | TBD |

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
