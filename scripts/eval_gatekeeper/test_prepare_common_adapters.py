"""Tests for Dataset v1.0 GT and legacy prediction adapters."""

import unittest

from prepare_common_gt import adapt_development_gt
from prepare_common_predictions import adapt_legacy_predictions
from common_evaluator import evaluate


class TestCommonAdapters(unittest.TestCase):

    def setUp(self):
        self.manifest = [{
            "image_id": "common_001",
            "filename": "images/existing/sample_1.JPG",
            "split": "development",
        }]

        self.dataset_gt = {
            "common_001": {
                "document_group_id": "common_doc01",
                "fields": {
                    "address": {"raw_text": "서울시"},
                    "deposit": {"raw_text": "10000"},
                    "contract_amount": {"status": "not_present"},
                    "lessor_name": {"raw_text": "홍길동"},
                    "lessee_name": {"raw_text": "김길동"},
                },
            }
        }

    def make_row(
        self,
        image="sample_1.JPG",
        field="address",
        method="Full OCR",
        pred_raw="서울시",
    ):
        return {
            "image": image,
            "field": field,
            "method": method,
            "pred_raw": pred_raw,
        }

    def test_gt_field_mapping(self):
        gt = adapt_development_gt(self.dataset_gt)

        self.assertEqual(len(gt["common_001"]), 4)
        self.assertEqual(gt["common_001"]["deposit_num"], "10000")
        self.assertNotIn("down_payment", gt["common_001"])

    def test_gt_rejects_damaged_text(self):
        self.dataset_gt["common_001"]["fields"]["address"][
            "raw_text"
        ] = "???"

        with self.assertRaises(ValueError):
            adapt_development_gt(self.dataset_gt)

    def test_gt_rejects_missing_field(self):
        del self.dataset_gt["common_001"]["fields"]["address"]

        with self.assertRaises(ValueError):
            adapt_development_gt(self.dataset_gt)

    def test_prediction_method_filter(self):
        rows = [
            self.make_row(),
            self.make_row(method="GT ROI OCR"),
            self.make_row(field="deposit_kor"),
        ]

        converted = adapt_legacy_predictions(
            self.manifest, rows, "Full OCR"
        )

        self.assertEqual(len(converted), 1)
        self.assertEqual(converted[0]["image"], "common_001")

    def test_duplicate_prediction_rejected(self):
        rows = [self.make_row(), self.make_row()]

        with self.assertRaises(ValueError):
            adapt_legacy_predictions(
                self.manifest, rows, "Full OCR"
            )

    def test_unknown_image_rejected(self):
        with self.assertRaises(ValueError):
            adapt_legacy_predictions(
                self.manifest,
                [self.make_row(image="unknown.JPG")],
                "Full OCR",
            )

    def test_unknown_field_rejected(self):
        with self.assertRaises(ValueError):
            adapt_legacy_predictions(
                self.manifest,
                [self.make_row(field="unknown_field")],
                "Full OCR",
            )

    def test_nonstring_prediction_rejected(self):
        with self.assertRaises(ValueError):
            adapt_legacy_predictions(
                self.manifest,
                [self.make_row(pred_raw=123)],
                "Full OCR",
            )

    def test_common_evaluator_integration(self):
        gt = adapt_development_gt(self.dataset_gt)

        rows = adapt_legacy_predictions(
            self.manifest,
            [self.make_row()],
            "Full OCR",
        )

        result = evaluate(gt, rows, "Full OCR")

        self.assertEqual(result["total"], 4)
        self.assertEqual(result["correct"], 1)
        self.assertEqual(result["missing_rows"], 3)
        self.assertEqual(result["empty_predictions"], 3)


if __name__ == "__main__":
    unittest.main()
