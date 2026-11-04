import unittest

from common_evaluator import (
    evaluate,
    load_tail_json,
    parse_ocr_amount,
)


class CommonEvaluatorTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gt = load_tail_json("gt/gt_fields.json")
        cls.rows = load_tail_json(
            "results/eval/field_results.json"
        )["rows"]

    def test_common10_denominator_and_p0(self):
        result = evaluate(self.gt, self.rows, "Full OCR")
        self.assertEqual(result["total"], 49)
        self.assertEqual(result["correct"], 29)

    def test_missing_field(self):
        filtered = [
            r for r in self.rows
            if not (
                r["method"] == "Full OCR"
                and r["image"] == "sample_2.JPG"
                and r["field"] == "deposit_num"
            )
        ]

        result = evaluate(self.gt, filtered, "Full OCR")

        self.assertEqual(result["total"], 49)
        self.assertEqual(result["correct"], 28)
        self.assertEqual(result["missing_rows"], 1)
        self.assertEqual(result["empty_predictions"], 1)

    def test_missing_image(self):
        filtered = [
            r for r in self.rows
            if not (
                r["method"] == "Full OCR"
                and r["image"] == "sample_2.JPG"
            )
        ]

        result = evaluate(self.gt, filtered, "Full OCR")

        self.assertEqual(result["total"], 49)
        self.assertEqual(result["correct"], 25)
        self.assertEqual(result["missing_rows"], 5)
        self.assertEqual(result["empty_predictions"], 5)

    def test_monetary_form_parsing(self):
        cases = {
            "원정(W30,000,000": "30000000",
            "20,000000": "20000000",
            "10.000,000": "10000000",
            "원정(W180,000.OㅇO": None,
            "410, 000,0O0": None,
            "": None,
        }

        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(
                    parse_ocr_amount(raw), expected
                )

    def test_duplicate_prediction_rejected(self):
        duplicated = self.rows + [self.rows[0]]

        with self.assertRaises(ValueError):
            evaluate(self.gt, duplicated, "Full OCR")


if __name__ == "__main__":
    unittest.main()