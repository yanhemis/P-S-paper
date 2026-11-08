"""Tests for the official ROI Coverage evaluation rules."""

import unittest

from roi_coverage_evaluator import (
    calculate_coverage,
    evaluate_field_roi,
    summarize_roi_coverage,
)


class TestROICoverageEvaluator(unittest.TestCase):

    def test_rotated_quad_coverage(self):
        gt = {"bbox": [2205, 2908, 2542, 3002]}
        quad = [
            [2218, 2896],
            [2552, 2911],
            [2549, 2987],
            [2214, 2972],
        ]

        result = evaluate_field_roi(gt, [quad], "P3")

        self.assertTrue(result["eligible"])
        self.assertAlmostEqual(result["coverage"], 0.7330122493, places=6)
        self.assertFalse(result["covered"])

    def setUp(self):
        self.gt = {"bbox": [0, 0, 100, 100]}

    def test_p2_gt_roi_coverage(self):
        result = evaluate_field_roi(self.gt, [], "P2")
        self.assertEqual(result["coverage"], 1.0)
        self.assertTrue(result["covered"])

    def test_p3_uses_maximum_coverage(self):
        rois = [
            [0, 0, 50, 100],
            [0, 0, 100, 90],
        ]
        result = evaluate_field_roi(self.gt, rois, "P3")

        self.assertAlmostEqual(result["coverage"], 0.9)
        self.assertTrue(result["covered"])

    def test_p4_uses_single_roi(self):
        result = evaluate_field_roi(
            self.gt, [[0, 0, 50, 100]], "P4"
        )
        self.assertEqual(result["coverage"], 0.5)
        self.assertFalse(result["covered"])

    def test_coverage_below_threshold(self):
        result = evaluate_field_roi(
            self.gt, [[0, 0, 89, 100]], "P4"
        )
        self.assertAlmostEqual(result["coverage"], 0.89)
        self.assertFalse(result["covered"])

    def test_missing_roi_counts_as_failure(self):
        result = evaluate_field_roi(self.gt, [], "P3")

        self.assertTrue(result["eligible"])
        self.assertEqual(result["coverage"], 0.0)
        self.assertFalse(result["covered"])

    def test_null_bbox_excluded(self):
        result = evaluate_field_roi(
            {"bbox": None}, [], "P4"
        )
        self.assertFalse(result["eligible"])
        self.assertIsNone(result["coverage"])

    def test_unreadable_excluded(self):
        result = evaluate_field_roi(
            {"bbox": [0, 0, 10, 10], "status": "unreadable"},
            [],
            "P4",
        )
        self.assertFalse(result["eligible"])

    def test_multiple_p4_rois_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_field_roi(
                self.gt,
                [[0, 0, 50, 50], [0, 0, 100, 100]],
                "P4",
            )

    def test_invalid_bbox_rejected(self):
        with self.assertRaises(ValueError):
            calculate_coverage(
                [0, 0, 0, 100],
                [0, 0, 50, 50],
            )

    def test_summary(self):
        results = [
            evaluate_field_roi(
                self.gt, [[0, 0, 100, 100]], "P4"
            ),
            evaluate_field_roi(
                self.gt, [[0, 0, 90, 100]], "P4"
            ),
            evaluate_field_roi(
                self.gt, [[0, 0, 50, 100]], "P4"
            ),
            evaluate_field_roi(self.gt, [], "P4"),
            evaluate_field_roi({"bbox": None}, [], "P4"),
        ]

        summary = summarize_roi_coverage(results)

        self.assertEqual(summary["eligible_fields"], 4)
        self.assertEqual(summary["excluded_fields"], 1)
        self.assertEqual(summary["covered_fields"], 2)
        self.assertAlmostEqual(summary["mean_coverage"], 0.6)
        self.assertAlmostEqual(summary["covered_rate"], 0.5)

    def test_all_fields_excluded(self):
        results = [
            evaluate_field_roi({"bbox": None}, [], "P3")
        ]

        summary = summarize_roi_coverage(results)

        self.assertEqual(summary["eligible_fields"], 0)
        self.assertEqual(summary["excluded_fields"], 1)
        self.assertIsNone(summary["mean_coverage"])
        self.assertIsNone(summary["covered_rate"])


if __name__ == "__main__":
    unittest.main()