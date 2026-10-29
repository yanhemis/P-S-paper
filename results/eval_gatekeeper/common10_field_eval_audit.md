# Common-10 Field Evaluation Consistency Audit

## Scope

- Pipelines: P0 Raw Full OCR, P1 Rectified Full OCR, P2 GT ROI OCR, P3 bang Detected ROI OCR
- Dataset: existing common 10 images
- Core fields: address, deposit, contract_amount, lessor_name, lessee_name
- Source mappings: deposit_num -> deposit; down_payment -> contract_amount
- Auxiliary deposit_kor excluded

## Verified Results

| Pipeline | Exact Match | Field Accuracy |
|---|---|---|
| P0 Raw Full OCR | 29/49 | 59.2% |
| P1 Rectified Full OCR | 31/49 | 63.3% |
| P2 GT ROI OCR | 31/49 | 63.3% |
| P3 Detected ROI OCR | 13/49 | 26.5% |

## Consistency Checks

- All pipelines evaluated 10 images.
- All pipelines evaluated 49 core field instances.
- Each pipeline has 49 unique (image, field) pairs.
- All pipelines have identical (image, field) sets.
- Normalized GT values match for all 49 instances.
- sample_7 has no evaluable contract_amount field.
- Missing P3 ROI field records: 27/49.
- All 27 missing P3 ROI fields were scored incorrect.

## Evaluation Caveats

1. P0/P1 Full OCR field assignment uses GT ROI coordinates. These numbers must not be described as fully GT-independent end-to-end extraction accuracy.
2. The existing evaluation code skips images absent from the prediction dictionary. Final evaluation must explicitly account for missing image-level predictions.
3. Identical normalized GT values do not establish that every normalization rule has been independently verified.
4. P3 recorded ROI presence is 22/49 (44.9%), not verified geometric ROI Coverage.
5. P3 conditional Field Accuracy is 13/22 (59.1%), not isolated OCR recognition accuracy.
6. P4 is currently a separate sample.jpg Anchor ROI PoC, not a comparable common-10 result.
7. New data and untouched holdout results are not included in this audit.

## Source Files

Read-only verification against origin/tail:

- results/eval/field_results.json
- results/h1/eval_rectified/field_results.json
- results/eval/detected_bang_pad25/field_results.json
- scripts/evaluate_fields.py

Verification used UTF-8 JSON parsing and comparisons of image-field keys and normalized GT values.
