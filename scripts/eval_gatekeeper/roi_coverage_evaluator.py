"""ROI Coverage evaluation based on the official Dataset GT protocol."""

import math


COVERED_THRESHOLD = 0.90


def validate_bbox(bbox):
    """Validate original-image [x1, y1, x2, y2] coordinates."""
    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
        raise ValueError(f"Invalid bbox structure: {bbox}")

    if any(
        isinstance(v, bool)
        or not isinstance(v, (int, float))
        or not math.isfinite(v)
        for v in bbox
    ):
        raise ValueError(f"Invalid bbox coordinates: {bbox}")

    x1, y1, x2, y2 = bbox

    if x1 >= x2 or y1 >= y2:
        raise ValueError(f"Invalid bbox area: {bbox}")

    return x1, y1, x2, y2


def calculate_coverage(gt_bbox, predicted_roi):
    """Calculate GT area covered by an ROI bbox or quadrilateral."""
    gx1, gy1, gx2, gy2 = validate_bbox(gt_bbox)

    if predicted_roi is None:
        return 0.0

    is_quad = (
        isinstance(predicted_roi, (list, tuple))
        and len(predicted_roi) == 4
        and all(
            isinstance(point, (list, tuple)) and len(point) == 2
            for point in predicted_roi
        )
    )

    if is_quad:
        polygon = [tuple(point) for point in predicted_roi]

        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            for point in polygon
            for value in point
        ):
            raise ValueError(f"Invalid ROI quad: {predicted_roi}")

        turns = []
        for i in range(4):
            a = polygon[i]
            b = polygon[(i + 1) % 4]
            c = polygon[(i + 2) % 4]
            turns.append(
                (b[0] - a[0]) * (c[1] - b[1])
                - (b[1] - a[1]) * (c[0] - b[0])
            )

        if not (
            all(turn > 0 for turn in turns)
            or all(turn < 0 for turn in turns)
        ):
            raise ValueError(f"Invalid non-convex ROI quad: {predicted_roi}")

    else:
        rx1, ry1, rx2, ry2 = validate_bbox(predicted_roi)
        polygon = [
            (rx1, ry1),
            (rx2, ry1),
            (rx2, ry2),
            (rx1, ry2),
        ]

    def polygon_area(points):
        if len(points) < 3:
            return 0.0

        return abs(sum(
            a[0] * b[1] - b[0] * a[1]
            for a, b in zip(points, points[1:] + points[:1])
        )) / 2.0

    def clip_polygon(points, axis, boundary, keep_greater):
        if not points:
            return []

        output = []
        previous = points[-1]

        for current in points:
            previous_inside = (
                previous[axis] >= boundary
                if keep_greater else previous[axis] <= boundary
            )
            current_inside = (
                current[axis] >= boundary
                if keep_greater else current[axis] <= boundary
            )

            if previous_inside != current_inside:
                t = (
                    (boundary - previous[axis])
                    / (current[axis] - previous[axis])
                )
                intersection = (
                    previous[0] + t * (current[0] - previous[0]),
                    previous[1] + t * (current[1] - previous[1]),
                )
                output.append(intersection)

            if current_inside:
                output.append(current)

            previous = current

        return output

    for axis, boundary, keep_greater in (
        (0, gx1, True),
        (0, gx2, False),
        (1, gy1, True),
        (1, gy2, False),
    ):
        polygon = clip_polygon(
            polygon, axis, boundary, keep_greater
        )

    gt_area = (gx2 - gx1) * (gy2 - gy1)
    return min(1.0, polygon_area(polygon) / gt_area)


def evaluate_field_roi(gt_item, predicted_rois, pipeline):
    """Evaluate one field's ROI against its GT bbox.

    predicted_rois:
        P2: ignored; GT bbox itself is the ROI
        P3: list of candidate ROIs
        P4: list containing zero or one final selected ROI

    Input coordinates must use the original image coordinate system.
    """
    if pipeline not in {"P2", "P3", "P4"}:
        raise ValueError(f"Unsupported pipeline: {pipeline}")

    if not isinstance(gt_item, dict):
        raise ValueError("Invalid GT field")

    status = gt_item.get("status")

    if (
        status in {"not_present", "unreadable"}
        or gt_item.get("unreadable") is True
        or gt_item.get("bbox") is None
    ):
        return {
            "eligible": False,
            "coverage": None,
            "covered": None,
        }

    gt_bbox = gt_item["bbox"]
    validate_bbox(gt_bbox)

    if pipeline == "P2":
        value = 1.0

    elif pipeline == "P3":
        value = max(
            (
                calculate_coverage(gt_bbox, roi)
                for roi in predicted_rois
            ),
            default=0.0,
        )

    else:
        if len(predicted_rois) > 1:
            raise ValueError("P4 must use only one final selected ROI")

        value = (
            calculate_coverage(gt_bbox, predicted_rois[0])
            if predicted_rois
            else 0.0
        )

    return {
        "eligible": True,
        "coverage": value,
        "covered": value >= COVERED_THRESHOLD,
    }

def summarize_roi_coverage(field_results):
    """Summarize mean Coverage and Covered Rate.

    field_results: list of evaluate_field_roi() results.
    Ineligible fields are excluded from both denominators.
    """
    eligible = [
        result
        for result in field_results
        if result["eligible"]
    ]

    total = len(eligible)
    covered = sum(result["covered"] is True for result in eligible)
    excluded = len(field_results) - total

    return {
        "eligible_fields": total,
        "excluded_fields": excluded,
        "covered_fields": covered,
        "mean_coverage": (
            sum(result["coverage"] for result in eligible) / total
            if total else None
        ),
        "covered_rate": covered / total if total else None,
    }