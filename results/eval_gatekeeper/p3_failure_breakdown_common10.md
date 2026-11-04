# P3 Detected ROI Failure Breakdown — Common 10

**Status:** Development-set audit (not holdout evaluation)
**Pipeline:** P3 — bang_ Detected ROI + OCR (pad25)
**Evaluation unit:** Eligible `(image, field)` instance
**Evaluation scope:** 10 images, 49 eligible fields

## 1. Outcome Summary

| Outcome | Count | Rate |
|---|---:|---:|
| Correct prediction | 13 | 26.5% |
| Empty prediction | 27 | 55.1% |
| Non-empty incorrect prediction | 9 | 18.4% |
| **Total** | **49** | **100.0%** |

All 49 eligible fields are included in the denominator.

The separate historical ROI audit recorded:
- ROI record present: 22/49 (44.9%)
- ROI record absent: 27/49 (55.1%)
- Conditional accuracy among fields with recorded ROI: 13/22 (59.1%)

**Important:** Recorded ROI presence is not verified geometric ROI coverage. The 27 empty predictions and 27 absent ROI records have matching aggregate counts, but their one-to-one correspondence should not be inferred without verifying field-level records.

## 2. Outcome by Field

| Field | Eligible | Empty | Correct | Non-empty incorrect |
|---|---:|---:|---:|---:|
| address | 10 | 6 | 0 | 4 |
| deposit | 10 | 7 | 2 | 1 |
| contract_amount | 9 | 6 | 0 | 3 |
| lessor_name | 10 | 3 | 6 | 1 |
| lessee_name | 10 | 5 | 5 | 0 |
| **Total** | **49** | **27** | **13** | **9** |

The missing `contract_amount` GT for `sample_7.JPG` is excluded from evaluation.

## 3. Observed Non-empty Failure Patterns

The following classifications describe **observable output symptoms**, not definitively established root causes.

| Observed pattern | Cases | Evidence |
|---|---:|---|
| Address text mismatch or surrounding-text inclusion | 4 | sample_1, sample_2, sample_4, sample_6 |
| Contract amount mixed with unrelated contract text | 3 | sample_1, sample_2, sample_4 |
| Deposit expression containing corrupted numeric text | 1 | sample_2 |
| Lessor-name value mismatch | 1 | sample_6 |
| **Total** | **9** | |

### Address

- `sample_1.JPG`: The address contains character substitutions and incorrect trailing characters.
- `sample_2.JPG`: The address contains substitutions and omits part of the expected ending.
- `sample_4.JPG`: Several address characters and numbers differ from GT.
- `sample_6.JPG`: The prediction includes substantial surrounding contract text rather than only the intended address.

### Contract Amount

- `sample_1.JPG`: The correct amount expression appears at the beginning, but unrelated payment and receipt text is appended.
- `sample_2.JPG`: The amount expression contains a recognition error and unrelated surrounding text.
- `sample_4.JPG`: The amount expression appears with unrelated contract text.

These cases must not automatically be counted solely as OCR character-recognition failures. Field extraction, ROI extent, and text selection may also contribute, but require separate evidence.

### Deposit

- `sample_2.JPG`: The prediction contains Korean and numeric amount expressions, while the numeric expression contains corrupted characters. The DRAFT parser does not silently repair OCR substitutions or select whichever expression agrees with GT.

### Lessor Name

- `sample_6.JPG`: The recognized name does not match GT. The responsible pipeline stage has not been independently verified.

## 4. Interpretation and Limitations

- The dominant observed outcome is an empty prediction: 27/49.
- Among the 22 non-empty predictions, 13 are correct and 9 are incorrect under the current DRAFT common evaluator.
- A non-empty prediction does not establish correct ROI placement.
- Empty output, missing ROI records, geometric ROI misses, OCR failures, and text-selection failures must remain separate concepts.
- The P3 pipeline used GT-informed ROI-to-field association during historical evaluation. It must not be described as fully GT-independent automatic field assignment.
- These results concern the historical common-10 development set, not Dataset v1.0 or holdout.
- CER and monetary parsing from the new common evaluator remain DRAFT until preprocessing and normalization are versioned and frozen.

## 5. Follow-up

Before final evaluation, verify field-level alignment between ROI presence and empty predictions, preserve stage-specific failure evidence, and report failure categories with clear denominators.

Do not transfer these findings directly to P4 or a future holdout set without separate evaluation.
