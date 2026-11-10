"""Evaluate actual final-pipeline ROIs against value-only GT bounding boxes.

Usage:
  python evaluate_roi_coverage.py --results results/p4_e2e --gt data/eval_v1/field_gt.json --expected-images 19

Read-only input. No GT is used to generate ROI or OCR predictions.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

KEY_MAP = {"소재지": "address", "보증금": "deposit", "계약금": "contract_amount", "임대인_성명": "lessor_name", "임차인_성명": "lessee_name"}


def coverage(gt, roi):
    if not isinstance(gt, (list, tuple)) or len(gt) != 4:
        return None
    try:
        gx1, gy1, gx2, gy2 = map(float, gt)
        if gx2 <= gx1 or gy2 <= gy1:
            return None
        if not isinstance(roi, (list, tuple)) or len(roi) != 4:
            return 0.0
        rx1, ry1, rx2, ry2 = map(float, roi)
        intersection = max(0., min(gx2, rx2) - max(gx1, rx1)) * max(0., min(gy2, ry2) - max(gy1, ry1))
        return intersection / ((gx2 - gx1) * (gy2 - gy1))
    except (ValueError, TypeError):
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--results', type=Path, default=Path('results/p4_e2e'))
    p.add_argument('--gt', type=Path, default=Path('field_gt.json'))
    p.add_argument('--expected-images', type=int, default=None)
    p.add_argument('--manifest', type=Path, default=Path('data/eval_v1_packages/development/manifest.csv'))
    p.add_argument('--output', type=Path, default=Path('results/p4_roi_coverage_final.csv'))
    args = p.parse_args()
    if not args.gt.is_file(): p.error(f'GT file not found: {args.gt}')
    gt_data = json.loads(args.gt.read_text(encoding='utf-8-sig'))
    manifest_map = {}
    if args.manifest.is_file():
        with args.manifest.open(encoding='utf-8-sig', newline='') as f:
            for item in csv.DictReader(f):
                if item.get('filename') and item.get('image_id'):
                    manifest_map[Path(item['filename']).name.lower()] = item['image_id']
    paths = sorted(args.results.glob('*/field_rois.json'))
    if not paths:
        p.error(f'No final pipeline field_rois.json found in {args.results}. Run run_p4_pipeline.py first.')
    rows = []
    missing_gt = []
    seen_images = set()
    for path in paths:
        result = json.loads(path.read_text(encoding='utf-8-sig'))
        image = result.get('image_id')
        if not image: p.error(f'Missing image_id: {path}')
        if image in seen_images: p.error(f'Duplicate image_id: {image}')
        seen_images.add(image)
        stem = Path(image).stem
        key = next((k for k in (image, stem, manifest_map.get(image.lower())) if k and k in gt_data), None)
        gt_fields = gt_data[key] if key else {}
        if isinstance(gt_fields, dict): gt_fields = gt_fields.get('fields', gt_fields)
        roi_fields = result.get('fields', {})
        for korean, english in KEY_MAP.items():
            gt_item = gt_fields.get(english, gt_fields.get(korean)) if isinstance(gt_fields, dict) else None
            gt_bbox = gt_item.get('bbox') if isinstance(gt_item, dict) else None
            roi_item = roi_fields.get(english, {})
            roi_bbox = roi_item.get('bbox') if isinstance(roi_item, dict) else None
            cov = coverage(gt_bbox, roi_bbox)
            if cov is None: missing_gt.append(f'{image}:{english}')
            rows.append({'image_id': image, 'field': english, 'gt_bbox': json.dumps(gt_bbox, ensure_ascii=False),
                         'roi_bbox': json.dumps(roi_bbox, ensure_ascii=False), 'coverage': '' if cov is None else f'{cov:.6f}',
                         'pass_0_90': '' if cov is None else str(cov >= 0.90)})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    scored = [float(r['coverage']) for r in rows if r['coverage'] != '']
    passed = sum(v >= 0.90 for v in scored)
    print(f'Images: {len(seen_images)}, fields: {len(rows)}, GT-scored: {len(scored)}')
    print(f'Coverage >= 0.90: {passed}/{len(scored)}')
    print(f'Mean GT coverage: {sum(scored)/len(scored):.4f}' if scored else 'Mean GT coverage: N/A')
    print(f'Missing/invalid GT: {len(missing_gt)}')
    print(f'CSV: {args.output}')
    if args.expected_images is not None and len(seen_images) != args.expected_images:
        print(f'BLOCKED: expected {args.expected_images} images, got {len(seen_images)}')
        return 1
    if not scored:
        print('BLOCKED: no valid GT'); return 1
    if missing_gt: print('NOTE: Missing GT excluded from denominator:', ', '.join(missing_gt[:12]))
    return 0

if __name__ == '__main__':
    sys.exit(main())
