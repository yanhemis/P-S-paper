"""Evaluate party-name ROI GT coverage using cached OCR; no PaddleOCR runs."""
import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAPPER = ROOT / 'anchor_field_mapper.py'
BASE = ROOT / 'results' / 'p4_development_v5'
GT_FILE = ROOT / 'data' / 'eval_v1_packages' / 'development' / 'field_gt.json'
MANIFEST = ROOT / 'data' / 'eval_v1_packages' / 'development' / 'manifest.csv'
FIELDS = {'lessor_name': '임대인_성명', 'lessee_name': '임차인_성명'}


def coverage(roi, gt):
    if not roi or not gt:
        return None
    x1, y1, x2, y2 = roi
    a, b, c, d = gt
    area = max(0, c-a) * max(0, d-b)
    if not area:
        return None
    overlap = max(0, min(x2, c)-max(x1, a)) * max(0, min(y2, d)-max(y1, b))
    return overlap / area


def main():
    for p in (MAPPER, BASE, GT_FILE, MANIFEST):
        if not p.exists():
            raise FileNotFoundError(f'필요한 파일 없음: {p}')
    gt = json.loads(GT_FILE.read_text(encoding='utf-8-sig'))
    with MANIFEST.open(encoding='utf-8-sig', newline='') as f:
        manifest = list(csv.DictReader(f))
    if not manifest:
        raise ValueError('manifest.csv에 데이터가 없습니다.')
    print('Manifest 열:', ', '.join(manifest[0]))
    # Match manifest row by image filename and find GT key in the same row.
    samples = sorted(BASE.glob('sample_*/first_pass_ocr.json'))
    if not samples:
        raise ValueError('v5 OCR 캐시를 찾지 못했습니다.')
    rows = []
    with tempfile.TemporaryDirectory(prefix='cached_roi_v6_') as tmp:
        work = Path(tmp)
        (work / 'anchor_field_mapper.py').write_bytes(MAPPER.read_bytes())
        for cache in samples:
            sample = cache.parent.name
            candidates = [r for r in manifest if any(sample.lower() == Path(str(v).replace('\\', '/')).stem.lower() for v in r.values() if v)]
            if len(candidates) != 1:
                print(f'{sample}: manifest 대응 {len(candidates)}건, 건너뜀')
                continue
            ids = [str(v).strip() for v in candidates[0].values() if str(v).strip() in gt]
            if len(set(ids)) != 1:
                print(f'{sample}: GT ID 대응 실패 ({ids}), 건너뜀')
                continue
            gt_fields = gt[ids[0]]['fields']
            (work / 'full_ocr_result.json').write_bytes(cache.read_bytes())
            run = subprocess.run([sys.executable, 'anchor_field_mapper.py'], cwd=work, capture_output=True, text=True, encoding='utf-8', errors='replace')
            if run.returncode:
                print(f'{sample}: 매핑 실패\n{run.stderr[-700:]}')
                continue
            mapped = json.loads((work / 'field_mapping_result.json').read_text(encoding='utf-8'))['fields']
            old_file = cache.parent / 'field_rois.json'
            old = json.loads(old_file.read_text(encoding='utf-8'))['fields'] if old_file.exists() else {}
            for key, label in FIELDS.items():
                roi = mapped.get(label, {}).get('value_roi')
                old_roi = old.get(key, {}).get('bbox')
                gt_bbox = gt_fields.get(key, {}).get('bbox')
                before, after = coverage(old_roi, gt_bbox), coverage(roi, gt_bbox)
                rows.append((sample, key, before, after, roi))
                fmt = lambda v: 'N/A' if v is None else f'{v*100:.2f}%'
                print(f'{sample:10s} {key:12s} v5={fmt(before):>8s} v6={fmt(after):>8s} ROI={roi}')
    print('\n=== 전체 비교 (GT 포함률, OCR 미실행) ===')
    for key in FIELDS:
        group = [r for r in rows if r[1] == key]
        for index, version in ((2, 'v5'), (3, 'v6')):
            vals = [r[index] for r in group if r[index] is not None]
            print(f'{key} {version}: 평균 {sum(vals)/len(vals)*100:.2f}%, 완전 포함 {sum(v >= .999999 for v in vals)}/{len(vals)}' if vals else f'{key} {version}: 측정 불가')
    if not rows:
        raise ValueError('비교 가능한 샘플이 없습니다. manifest 매핑을 확인하세요.')


if __name__ == '__main__':
    main()
