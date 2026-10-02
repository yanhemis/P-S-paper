# OCR / ROI 재인식 모듈 입출력 규격

> 작성: tail (2026-10-03) · 대상: 추가 인원 B (통합), `bang_` / `heewon` (실험 C용 ROI 전달)
> 코드: `scripts/ocr_baseline.py` (전체 페이지), `scripts/roi_ocr.py` (ROI), `scripts/evaluate_fields.py` (평가)

## 0. 공통 약속

- **좌표계**: 원본 이미지 픽셀 좌표. **EXIF 회전을 적용한 뒤** 기준 (`cv2.imread` 기본 동작).
  스마트폰 사진은 파일상 4032×3024(가로)이지만 회전 후 3024×4032(세로)다. 회전 전 좌표를 주면 칸이 전부 어긋난다.
- **이미지 키**: 파일명 그대로 (예: `"sample_3.JPG"`, 대소문자 구분).
- **필드 키**:

| 키 | 의미 | 비고 |
|---|---|---|
| `address` | 소재지 | |
| `deposit_num` | 보증금 숫자 금액 (`₩` ~ `)` 사이) | 보증금 필드의 대표값 |
| `deposit_kor` | 보증금 한글 금액 (`금` ~ `원정` 사이) | 보조 |
| `down_payment` | 계약금 한글 금액 (`금` ~ `원정은` 사이) | |
| `lessor_name` | 임대인 성명 칸 | |
| `lessee_name` | 임차인 성명 칸 | |

- **OCR 모델** (실험 A/B/C 공통): PaddleOCR 3.x, `PP-OCRv5_mobile_det` + `korean_PP-OCRv5_mobile_rec`,
  `text_det_limit_side_len=1536`, `text_det_limit_type="max"` (서버 모델은 16GB RAM에서 OOM 발생)

## 1. ROI 입력 (실험 C용으로 받을 형식)

```json
{
  "sample_1.JPG": {
    "fields": {
      "address":     { "quad": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]] },
      "deposit_num": { "bbox": [x_min, y_min, x_max, y_max] }
    }
  }
}
```

- 필드마다 `quad`(4점, **좌상 → 우상 → 우하 → 좌하** 순서)나 `bbox` 중 하나를 준다. 둘 다 있으면 `quad`를 쓴다.
- 기울어진 촬영본은 `quad`를 권장한다. `bbox`만 주면 기울어진 행에서 위아래 행이 섞인다.
- 칸 경계(표 선) 기준으로 주면 된다. 손글씨가 선을 넘는 경우를 위해 모듈이 위아래로 칸 높이의 25%를 자동으로 늘린다.
- 검출하지 못한 필드는 키를 빼면 된다. 평가 시 빈 예측으로 처리된다(= 실패).
- 참고 예시: `gt/gt_roi.json` (실험 B의 GT ROI, 같은 형식)

실행:

```bash
python scripts/roi_ocr.py <detected_roi.json> results/roi_detected
python scripts/evaluate_fields.py --detected results/roi_detected
```

## 2. ROI OCR 출력 — `<out_dir>/<image_stem>_roi_ocr.json`

```json
{
  "image_id": "sample_1.JPG",
  "roi_source": "gt/gt_roi.json",
  "runtime_sec": 1.01,
  "fields": {
    "deposit_num": {
      "text": "180,000,000",
      "confidence": 0.98,
      "runtime_sec": 0.12,
      "items": [ { "text": "180,000,000", "confidence": 0.98, "bbox": [x1, y1, x2, y2] } ]
    }
  }
}
```

- `text`: crop 안에서 인식된 박스들을 왼쪽에서 오른쪽 순서로 공백으로 이어 붙인 **원문** (정규화 전)
- `confidence`: crop 안 박스들의 평균 rec score (박스가 없으면 0.0)
- `items[].bbox`: **crop 좌표** (원근 보정 + 위아래 여유 + 흰 여백 32px 기준). 원본 좌표가 아님에 주의
- `runtime_sec`: 필드 하나의 det + rec 시간. 최상위 `runtime_sec`은 한 장의 필드 시간 합
- crop 이미지: `<out_dir>/crops/<image_stem>_<field>.jpg`

## 3. 전체 페이지 OCR 출력 — `results/<image_stem>_ocr.json`

```json
{
  "image_id": "sample_1.JPG",
  "runtime_sec": 32.4,
  "num_text_boxes": 169,
  "items": [
    { "text": "...", "confidence": 0.99, "bbox": [x1, y1, x2, y2], "poly": [[x,y],[x,y],[x,y],[x,y]] }
  ]
}
```

- `bbox`, `poly`는 원본 이미지 좌표다. `poly`는 2026-10-03에 추가했다(기울어진 박스의 글자 위치 추정용).

## 4. 필드 값 정규화 (평가 기준)

`scripts/evaluate_fields.py`의 `normalize()`. 통합할 때도 같은 규칙으로 값을 뽑으면 평가 결과와 일치한다.

| 필드 | 규칙 |
|---|---|
| 공통 | 유니코드 NFC, 모든 공백 제거 |
| `deposit_num` | 숫자만 남김 (`180,000,000` → `180000000`) |
| `deposit_kor`, `down_payment` | 인쇄 글자 `원정`/`원정은`/`금`/`(`/`)`/`₩`/`W` 제거, 끝의 `원` 제거 |
| `lessor_name`, `lessee_name` | `(인)`, `성명`, 괄호·구두점 제거 |
| `address` | `,` `.` `·` 제거 |

- 지표: Exact Match(정규화 후 완전 일치), CER(레벤슈타인 거리 / 정답 길이)
- 정답: `gt/gt_fields.json` (`null` = 미기입이라 평가에서 제외)
