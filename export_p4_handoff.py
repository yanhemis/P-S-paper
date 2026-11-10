"""Export P4 development handoff using cached OCR, without rerunning OCR.
Run from P-S-paper project root. Does not modify existing results.
"""
import csv
import json
import shutil
import zipfile
from pathlib import Path
from run_p4_roi_reocr_v2 import select_field_value, normalize_for_output

ROOT = Path('results/p4_development_v6')
OUT = Path('results/p4_handoff_development')
FIELDS = ('address', 'deposit', 'contract_amount', 'lessor_name', 'lessee_name')


def read_json(p):
    return json.loads(p.read_text(encoding='utf-8'))


def write_json(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')


def norm_no_spaces(v):
    return ''.join((normalize_for_output(v) or '').split())


def main():
    summary = ROOT / 'summary.csv'
    if not summary.is_file():
        raise SystemExit(f'기존 캐시 없음: {summary}')
    with summary.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit('summary.csv 비어 있음')
    # Validate all input files before writing any output.
    for r in rows:
        folder = ROOT / Path(r['image_id']).stem
        for name in ('field_rois.json', 'final_fields.json'):
            if not (folder / name).is_file():
                raise SystemExit(f'파일 없음: {folder / name}')
    if OUT.exists():
        raise SystemExit(f'출력 폴더가 이미 있습니다. 기존 자료 보호를 위해 중단: {OUT}')
    OUT.mkdir(parents=True)
    results = []
    for r in rows:
        image_id = Path(r['image_id']).stem
        field = r['field']
        folder = ROOT / image_id
        roi = read_json(folder / 'field_rois.json')
        final = read_json(folder / 'final_fields.json')
        original = final['fields'][field]
        geometry = roi['fields'][field]
        prediction, selected, info = select_field_value(
            field, original.get('ocr_tokens') or [],
            geometry.get('anchor_bbox'), geometry.get('bbox')
        )
        gt = (r.get('gt_raw_text') or '').strip()
        record = {
            'image_id': r['image_id'], 'field': field,
            'gt_raw_text': gt, 'old_prediction': original.get('prediction'),
            'prediction': prediction, 'normalized_prediction': normalize_for_output(prediction),
            'raw_exact_match': '' if not gt else prediction == gt,
            'whitespace_insensitive_match_diagnostic_only': '' if not gt else norm_no_spaces(prediction) == norm_no_spaces(gt),
            'roi_found': geometry.get('roi_found'),
            'roi_bbox_original_image': geometry.get('bbox'),
            'anchor_bbox_original_image': geometry.get('anchor_bbox'),
            'failure_reason': geometry.get('failure_reason') or (None if prediction else 'NO_SELECTED_VALUE'),
        }
        results.append(record)
        target = OUT / image_id
        target.mkdir(exist_ok=True)
        if not (target / 'field_rois.json').exists():
            shutil.copy2(folder / 'field_rois.json', target / 'field_rois.json')
        revised = target / 'final_fields.json'
        if revised.exists():
            output_final = read_json(revised)
        else:
            output_final = dict(final)
            output_final['fields'] = {k: dict(v) for k, v in final['fields'].items()}
        entry = output_final['fields'][field]
        entry['prediction'] = prediction
        entry['normalized_prediction'] = normalize_for_output(prediction)
        entry['selected_tokens'] = selected
        entry['selection_info'] = info
        entry['failure_reason'] = record['failure_reason']
        output_final['pipeline_note'] = 'Cached OCR token reselection using field_rois anchor/ROI coordinates; not a fresh OCR run.'
        write_json(revised, output_final)
    headers = ['image_id','field','gt_raw_text','old_prediction','prediction','normalized_prediction','raw_exact_match','whitespace_insensitive_match_diagnostic_only','roi_found','roi_bbox_original_image','anchor_bbox_original_image','failure_reason']
    with (OUT / 'summary.csv').open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(results)
    evaluated = [r for r in results if r['gt_raw_text']]
    raw = sum(r['raw_exact_match'] is True for r in evaluated)
    whitespace = sum(r['whitespace_insensitive_match_diagnostic_only'] is True for r in evaluated)
    manifest = {
        'scope': 'Development cached 10 images, 5 fields each',
        'input': str(ROOT), 'field_count': len(results), 'gt_evaluated': len(evaluated),
        'raw_exact_correct': raw, 'whitespace_insensitive_diagnostic_correct': whitespace,
        'important': [
            'No PaddleOCR rerun. Output is reselected from existing OCR tokens.',
            'Whitespace-insensitive match is diagnostic only, not the official metric.',
            'Do not claim Holdout performance or full Development coverage.',
            'ROI coordinates are in original-image coordinate space.',
            'Check official GT BBox and ROI Coverage rules in 04_data_collection_gt_protocol.md section 7.',
        ],
        'recipients': {'Dahye': 'summary.csv and per-image final_fields.json',
                       'Gaeun': 'per-image field_rois.json and summary.csv; verify GT and coverage independently'}
    }
    write_json(OUT / 'handoff_manifest.json', manifest)
    archive = OUT.with_suffix('.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file():
                z.write(p, p.relative_to(OUT.parent))
    print(f'생성 완료: {archive}')
    print(f'필드: {len(results)} / GT: {len(evaluated)}')
    print(f'Raw exact: {raw}/{len(evaluated)}')
    print(f'공백 무시 참고치: {whitespace}/{len(evaluated)} (공식 지표 아님)')
    print('기존 결과는 변경하지 않았습니다.')

if __name__ == '__main__':
    main()
