# P4 Anchor ROI — Single-Image PoC Audit

## Scope

- Source: origin/taegu
- Pipeline: P4 Anchor ROI / Field Mapping
- Evaluated image: sample.jpg
- Evaluated field instances: 5
- Evaluation: raw string Exact Match against taegu GT

## Verified Results

| Field | Common Key | Anchor Found | Raw Exact Match |
|---|---|---|---|
| 소재지 | address | True | True |
| 보증금 | deposit | True | True |
| 계약금 | contract_amount | True | True |
| 임대인_성명 | lessor_name | True | True |
| 임차인_성명 | lessee_name | True | True |
| TOTAL | 5 fields | 5/5 | 5/5 |

## Interpretation and Limitations

1. All five anchors were recorded as found on sample.jpg.
2. All five predicted values exactly matched taegu's GT strings.
3. This is a single-image PoC, not a common-10 evaluation.
4. Raw Exact Match does not establish compliance with the common normalization rules.
5. Geometric ROI Coverage, CER, and end-to-end latency were not verified.
6. P4 must not be directly compared with P0-P3 common-10 Field Accuracy.
7. No new-data or untouched holdout performance is established.

## Sources

- origin/taegu:field_gt.json
- origin/taegu:field_mapping_result.json
- origin/taegu:evaluate_fields.py
