# Common-10 Normalization Reproducibility Audit

## Scope

- Source: origin/tail
- Dataset: existing common 10 images
- Core fields: address, deposit, contract_amount, lessor_name, lessee_name
- Field mappings: deposit_num -> deposit; down_payment -> contract_amount
- Auxiliary deposit_kor excluded

## Verification Results

| Source | Checked records | Mismatches |
|---|---:|---:|
| P0/P2 field_results.json | 98 | 0 |
| P1 Rectified field_results.json | 49 | 0 |
| P3 evaluation field_results.json (P0/P2/P3 rows) | 147 | 0 |
| TOTAL | 294 | 0 |

Both pred_norm and gt_norm were recomputed using the normalize()
function extracted from origin/tail:scripts/evaluate_fields.py.

All stored normalized values matched the recomputed values.

## Normalization Rules

- All fields: Unicode NFC and whitespace removal.
- deposit: retain digits only.
- contract_amount: remove form-related tokens, selected symbols,
  the prefix "금", and a trailing "원".
- lessor_name / lessee_name: remove stamp/name labels and
  selected punctuation.
- address: remove comma, period, and middle dot.

## Limitations

1. This confirms consistency with the existing normalization code,
   not correctness of the normalization policy.
2. Some money normalization rules assume the existing contract form.
   They require review before application to new data.
3. The same source results appear in multiple evaluation files.
   Therefore, 294 records are not 294 independent field instances.
4. Common-10 evaluation uses 49 unique core field instances.
5. The audit does not establish GT-independent end-to-end evaluation.
6. New dataset and untouched holdout evaluation remain pending.

## Sources

- origin/tail:scripts/evaluate_fields.py
- origin/tail:results/eval/field_results.json
- origin/tail:results/h1/eval_rectified/field_results.json
- origin/tail:results/eval/detected_bang_pad25/field_results.json
