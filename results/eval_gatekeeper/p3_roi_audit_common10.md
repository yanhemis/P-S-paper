# P3 Detected ROI Audit — Common 10 Images

## Scope
- Pipeline: P3 (bang Detected ROI + tail OCR, padding 25%)
- Dataset: existing common 10 images
- Evaluated field instances: 49
- sample_7 has 4 evaluable fields; other images have 5 each.
- Auxiliary field deposit_kor is excluded.

## Verified Results

| Metric | Result |
|---|---|
| Recorded ROI field presence | 22/49 (44.9%) |
| Missing ROI field records | 27/49 |
| Correct predictions with recorded ROI | 13/22 (59.1%) |
| Correct predictions without recorded ROI | 0/27 |
| End-to-end Field Accuracy | 13/49 (26.5%) |

## Per-field Recorded ROI Presence

| Field | Recorded / Expected |
|---|---|
| address | 4/10 |
| deposit (source: deposit_num) | 3/10 |
| contract_amount (source: down_payment) | 3/9 |
| lessor_name | 7/10 |
| lessee_name | 5/10 |
| TOTAL | 22/49 |

## Per-image Recorded ROI Presence

| Image | Recorded / Expected |
|---|---|
| sample_1 | 5/5 |
| sample_2 | 5/5 |
| sample_3 | 1/5 |
| sample_4 | 5/5 |
| sample_5 | 0/5 |
| sample_6 | 3/5 |
| sample_7 | 0/4 |
| sample_8 | 2/5 |
| sample_9 | 1/5 |
| sample_10 | 0/5 |

## Interpretation and Limitations

1. ROI field presence (44.9%) means that a field key exists in the ROI OCR JSON. It does NOT establish geometric overlap with GT or spatial ROI Coverage.
2. Conditional Field Accuracy (59.1%) reflects ROI localization/mapping and OCR together. It is NOT isolated OCR model accuracy.
3. Missing ROI fields count as failures in end-to-end Field Accuracy.
4. Field Exact Match values are taken from tail's existing evaluation results; normalization rules have not yet been independently audited.
5. Results apply only to the existing 10 images and must not be generalized to new data or holdout.
6. P4 Anchor ROI results are not included because comparable common-10 evaluation results have not been verified.

## Source Artifacts

Read-only sources from origin/tail:

- results/eval/detected_bang_pad25/field_results.json
- results/eval/detected_bang_pad25/summary.md
- results/roi_detected_bang_pad25/sample_1_roi_ocr.json through sample_10_roi_ocr.json

Verification: Python subprocess Git JSON reads, UTF-8 decoding, 5-field filter, and cross-check against exact_match.
