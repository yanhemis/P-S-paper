"""Unit tests for P4 prediction adapter."""

import unittest

from prepare_p4_predictions import adapt_p4_predictions


class TestP4PredictionAdapter(unittest.TestCase):

    def setUp(self):
        self.manifest = [{
            "image_id": "common_001",
            "filename": "images/existing/sample_1.JPG",
            "split": "development",
            "usable": "yes",
        }]

    def make_result(self, prediction="test", source="live_paddleocr"):
        return {
            "image_id": "sample_1.JPG",
            "first_pass_source": source,
            "fields": {
                "address": {"prediction": prediction},
                "deposit": {"prediction": "10000"},
            },
        }

    def test_prediction_conversion(self):
        rows = adapt_p4_predictions(
            self.manifest, [self.make_result()]
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], {
            "image": "common_001",
            "field": "address",
            "method": "P4",
            "pred_raw": "test",
        })

    def test_missing_prediction(self):
        rows = adapt_p4_predictions(
            self.manifest,
            [self.make_result(prediction=None)]
        )
        self.assertEqual(rows[0]["pred_raw"], "")

    def test_cached_poc_rejected(self):
        with self.assertRaises(ValueError):
            adapt_p4_predictions(
                self.manifest,
                [self.make_result(source="cached_ocr")]
            )

    def test_duplicate_prediction_rejected(self):
        with self.assertRaises(ValueError):
            adapt_p4_predictions(
                self.manifest,
                [self.make_result(), self.make_result()]
            )

    def test_unknown_image_rejected(self):
        result = self.make_result()
        result["image_id"] = "unknown.JPG"

        with self.assertRaises(ValueError):
            adapt_p4_predictions(self.manifest, [result])

    def test_unknown_field_rejected(self):
        result = self.make_result()
        result["fields"]["unknown_field"] = {
            "prediction": "test"
        }

        with self.assertRaises(ValueError):
            adapt_p4_predictions(self.manifest, [result])

    def test_invalid_prediction_rejected(self):
        result = self.make_result(prediction=123)

        with self.assertRaises(ValueError):
            adapt_p4_predictions(self.manifest, [result])

    def test_invalid_field_structure_rejected(self):
        result = self.make_result()
        result["fields"] = []

        with self.assertRaises(ValueError):
            adapt_p4_predictions(self.manifest, [result])

    def test_non_development_image_rejected(self):
        manifest = [{
            "image_id": "test_001",
            "filename": "images/test.jpg",
            "split": "test",
            "usable": "yes",
        }]

        result = self.make_result()
        result["image_id"] = "test.jpg"

        with self.assertRaises(ValueError):
            adapt_p4_predictions(manifest, [result])

    def test_missing_first_pass_source_rejected(self):
        result = self.make_result()
        del result["first_pass_source"]

        with self.assertRaises(ValueError):
            adapt_p4_predictions(
                self.manifest, [result]
            )

if __name__ == "__main__":
    unittest.main()