"""Audit cached P4 v6 second-pass OCR and export a versioned handoff.
Does not run OCR, alter existing outputs, or use GT for predictions.
"""
import csv
import json
import hashlib
import zipfile
from collections import Counter
from pathlib import Path
from run_p4_roi_reocr_v2 import select_field_value, normalize_for_output

SOURCE = Path('results/p4_development_v6')
OUT = Path('results/p4_handoff_verified_v1')
FIELDS = ('address', 'deposit', 'contract_amount', 'lessor_name', 'lessee_name')


def load(path):
    if not path.is_file():
        raise FileNotFoundError(f'필수 파일 없음: {path}')
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def compact(value):
    return ''.join((normalize_for_output(value) or '').split())


def reason(pred, gt, tokens, roi, original_reason):
    if not roi.get('roi_found') or not roi.get('bbox'):
        return original_reason or 'ROI_NOT_FOUND'
    if not tokens:
        return 'SECOND_PASS_OCR_NO_TEXT'
    if not pred:
        return 'VALUE_SELECTION_FAILED'
    if not gt:
        return 'GT_MISSING_NOT_EVALUATED'
    if pred == gt:
        return None
    if compact(pred) == compact(gt):
        return 'WHITESPACE_ONLY_MISMATCH'
    texts = [str(t.get('text', '')) for t in tokens]
    if compact(gt) in compact(' '.join(texts)):
        return 'GT_PRESENT_IN_OCR_TOKENS_SELECTION_OR_JOIN_ERROR'
    return 'OCR_TEXT_MISMATCH_OR_INCOMPLETE_VALUE_UNDETERMINED'


def main():
    if OUT.exists() or OUT.with_suffix('.zip').exists():
        raise SystemExit(f'기존 출력 보호: {OUT} 또는 ZIP이 이미 존재합니다. 삭제하지 않고 중단합니다.')
    with (SOURCE / 'summary.csv').open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit('v6 summary.csv가 비어 있습니다.')
    ids = sorted({Path(r['image_id']).stem for r in rows})
    if len(rows) != len(ids) * len(FIELDS):
        raise SystemExit(f'필드 개수 불일치: {len(rows)}개 / 이미지 {len(ids)}장')
    grouped = {}
    for image_id in ids:
        grouped[image_id] = (load(SOURCE / image_id / 'field_rois.json'),
                             load(SOURCE / image_id / 'final_fields.json'))
    # No output is written until all required inputs are validated.
    for r in rows:
        image_id = Path(r['image_id']).stem
        field = r['field']
        if field not in FIELDS or field not in grouped[image_id][0]['fields'] or field not in grouped[image_id][1]['fields']:
            raise SystemExit(f'필드 누락: {image_id} {field}')
    audit = []
    results = {}
    for image_id in ids:
        roi, final = grouped[image_id]
        results[image_id] = (roi, json.loads(json.dumps(final, ensure_ascii=False)))
    for r in rows:
        image_id = Path(r['image_id']).stem
        field = r['field']
        roi, final = grouped[image_id]
        geom = roi['fields'][field]
        original = final['fields'][field]
        tokens = original.get('ocr_tokens') or []
        pred, selected, info = select_field_value(field, tokens, geom.get('anchor_bbox'), geom.get('bbox'))
        gt = (r.get('gt_raw_text') or '').strip()
        category = reason(pred, gt, tokens, geom, original.get('failure_reason'))
        item = results[image_id][1]['fields'][field]
        item['prediction'] = pred
        item['normalized_prediction'] = normalize_for_output(pred)
        item['selected_tokens'] = selected
        item['selection_info'] = info
        item['failure_reason'] = category
        item['failure_reason_note'] = 'Diagnostic category inferred from cached OCR and GT comparison; not a proven root cause.' if category else None
        audit.append({
            'image_id': r['image_id'], 'field': field, 'gt_raw_text': gt,
            'v6_original_prediction': original.get('prediction') or '',
            'prediction': pred or '', 'normalized_prediction': normalize_for_output(pred) or '',
            'raw_exact_match': '' if not gt else str(pred == gt),
            'whitespace_ignored_match_diagnostic_only': '' if not gt else str(compact(pred) == compact(gt)),
            'roi_found': str(bool(geom.get('roi_found'))),
            'failure_reason': category or '',
            'ocr_token_count': len(tokens),
        })
    for image_id in ids:
        roi, final = results[image_id]
        final['verification_note'] = 'Cached v6 second-pass OCR tokens; reselection with actual anchor/ROI coordinates; GT used only for evaluation and diagnostic failure categories.'
        save(OUT / image_id / 'field_rois.json', roi)
        save(OUT / image_id / 'final_fields.json', final)
    headers = list(audit[0])
    with (OUT / 'summary.csv').open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(audit)
    evaluated = [r for r in audit if r['gt_raw_text']]
    raw = sum(r['raw_exact_match'] == 'True' for r in evaluated)
    whitespace = sum(r['whitespace_ignored_match_diagnostic_only'] == 'True' for r in evaluated)
    counts = Counter(r['failure_reason'] or 'RAW_EXACT_MATCH' for r in audit)
    manifest = {
        'source': str(SOURCE), 'images': len(ids), 'fields': len(audit), 'gt_evaluated': len(evaluated),
        'raw_exact_correct': raw, 'whitespace_ignored_diagnostic_correct': whitespace,
        'failure_reason_counts': dict(sorted(counts.items())),
        'limits': ['Development subset only; not full Development or Holdout.',
                   'Uses already-run v6 second-pass OCR tokens; does not rerun OCR.',
                   'Prediction never uses GT. Failure categories are diagnostics, not proven root causes.',
                   'Whitespace-ignored metric is NOT official normalization.',
                   'OCR engine-level quality cannot be established from exact-match alone.'],
    }
    save(OUT / 'verification_manifest.json', manifest)
    lines = [
        '# P4 v6 2차 OCR 캐시 검증 결과', '',
        f'- 대상: Development {len(ids)}장, {len(audit)}필드 (GT {len(evaluated)}필드)',
        f'- Raw Exact Match: {raw}/{len(evaluated)} ({raw/len(evaluated)*100:.1f}%)' if evaluated else '- GT 없음',
        f'- 공백 무시 참고치: {whitespace}/{len(evaluated)} (공식 지표 아님)',
        '- 검증 방법: 기존 v6 2차 OCR 토큰에 실제 Anchor/ROI 좌표 기반 선택 규칙 재적용, GT와 비교',
        '- 한계: 2차 OCR 신규 실행 아님, 전체 Development/Holdout 미검증', '',
        '## 실패/상태 분류 (원인 확정 아님)',
    ]
    lines += [f'- {key}: {value}건' for key, value in sorted(counts.items())]
    lines += ['', '## 전달 자료', '- sample_*/field_rois.json: 원본 이미지 좌표 ROI',
              '- sample_*/final_fields.json: 검증된 캐시 재선택 결과와 실패 분류',
              '- summary.csv: GT/예측/일치/실패 분류',
              '- verification_manifest.json: 범위 및 집계', '']
    (OUT / 'README_verification.md').write_text('\n'.join(lines), encoding='utf-8')
    archive = OUT.with_suffix('.zip')
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file():
                z.write(p, p.relative_to(OUT.parent))
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        if bad:
            raise RuntimeError(f'압축 검증 실패: {bad}')
    print('=== P4 v6 2차 OCR 캐시 검증 완료 ===')
    print(f'Development: {len(ids)}장 / {len(audit)}필드 / GT {len(evaluated)}개')
    print(f'Raw Exact Match: {raw}/{len(evaluated)}')
    print(f'공백 무시 참고치: {whitespace}/{len(evaluated)} (공식 지표 아님)')
    print('실패 분류:')
    for key, value in sorted(counts.items()):
        print(f'  {key}: {value}')
    print(f'압축파일: {archive}')
    print('기존 v6 및 이전 전달본은 변경하지 않았습니다.')

if __name__ == '__main__':
    main()
