"""Re-evaluate cached P4 OCR tokens using actual ROI/anchor coordinates.

No PaddleOCR invocation, no ground-truth-guided selection, no output mutation.
"""
import csv
import json
from pathlib import Path

from run_p4_roi_reocr_v2 import select_field_value

ROOT = Path('results/p4_development_v6')
SUMMARY = ROOT / 'summary.csv'


def load_json(path):
    if not path.is_file():
        raise FileNotFoundError(f'필수 파일 없음: {path}')
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    if not SUMMARY.is_file():
        raise FileNotFoundError(f'요약 파일 없음: {SUMMARY}')

    with SUMMARY.open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))

    evaluated = old_ok = new_ok = improved = regressed = 0
    changed = 0
    for row in rows:
        image_id = Path(row['image_id']).stem
        field = row['field']
        folder = ROOT / image_id
        final = load_json(folder / 'final_fields.json')
        roi = load_json(folder / 'field_rois.json')
        item = final['fields'][field]
        roi_item = roi['fields'][field]
        old = item.get('prediction')
        new, _, _ = select_field_value(
            field,
            item.get('ocr_tokens') or [],
            roi_item.get('anchor_bbox'),
            roi_item.get('bbox'),
        )
        if old != new:
            changed += 1
            print(f'[변경] {image_id} {field}: {old!r} -> {new!r}')
        gt = (row.get('gt_raw_text') or '').strip()
        if not gt:
            continue
        evaluated += 1
        before = isinstance(old, str) and old.strip() == gt
        after = isinstance(new, str) and new.strip() == gt
        old_ok += int(before)
        new_ok += int(after)
        if before and not after:
            regressed += 1
            print(f'  [악화] {image_id} {field} | GT: {gt!r}')
        if after and not before:
            improved += 1
            print(f'  [개선] {image_id} {field} | GT: {gt!r}')

    print('\n=== 실제 좌표 기반 캐시 재선택 검증 ===')
    print(f'전체 필드: {len(rows)}')
    print(f'GT 평가 대상: {evaluated}')
    print(f'기존 정답: {old_ok}')
    print(f'수정 후 정답: {new_ok}')
    print(f'개선: {improved}')
    print(f'악화: {regressed}')
    print(f'예측 변경: {changed}')
    print('주의: 개발 데이터 캐시 재선택 결과이며 최종 Holdout 성능은 아닙니다.')


if __name__ == '__main__':
    main()
