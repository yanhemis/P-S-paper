# tail 전달: 공통 10장 Detected ROI OCR(실험 C) 입력

## 1. 전달 파일 (`output/common10/handoff_tail/`)

| 파일 | 내용 |
|---|---|
| `detected_roi_cells.json` | tail `roi_ocr.py` 입력 형식 그대로 (`docs/ocr_io_spec.md` 1절) |
| `field_cell_match.csv` | 필드별 선택한 셀 id, GT 덮는 비율, 높이 비, IoU, 제외 사유 |

이미지별 전체 셀이 필요하면 `output/common10/<이미지명>/cells_original.json` (원본 좌표)을 쓴다.

## 2. 형식과 좌표

```json
{
  "sample_1.JPG": {
    "source": "bang_ opencv_grid_merge cells.json (GT ROI 기반 셀 선택)",
    "fields": {
      "address": {"quad": [[x,y],[x,y],[x,y],[x,y]], "cell_id": 2}
    }
  }
}
```

- 좌표: **원본 이미지, EXIF 회전 적용 후** (3024x4032). tail 규격과 같음
- `quad`: 좌상 → 우상 → 우하 → 좌하. 보정본(`cells.json`) bbox 네 꼭짓점을 원본 좌표로 정확히 되돌린 것이라 기울어진 촬영본에서도 칸 모양을 따른다
- `cell_id`: 그 이미지 `cells.json` / `cells_original.json` 의 셀 id (추가 키라 `roi_ocr.py` 는 무시)
- quad 는 **표 선 기준 칸 경계**이므로 tail 규격대로 `roi_ocr.py` 기본 `--pad` (위아래 25%) 를 쓰면 된다.
  위아래 행 글자가 섞이면 `--pad 0` 결과와 비교 권장

## 3. 필드 ↔ 셀 대응 방식 (중요)

- Anchor 규칙은 이번 작업 범위가 아니어서, 필드마다 **tail GT ROI(`gt/gt_roi.json`)를 가장 많이 덮는 검출 셀**을 골랐다.
- 즉 이 입력은 "필드 위치는 알 때, 자동 검출된 셀 경계로 잘랐을 때의 OCR 성능"을 보는 것이다.
  필드를 자동으로 찾는 성능(Anchor)은 포함되지 않으므로, 결과를 쓸 때 이 조건을 같이 적어야 한다.
- 다음 경우는 키를 빼서 평가에서 실패로 처리되게 했다 (`field_cell_match.csv` 의 `reason`).
  - `no_cell`: GT ROI 면적의 50% 이상을 덮는 셀이 없음 (표 누락)
  - `over_merged_cell`: 덮는 셀 높이가 GT 칸 높이의 2배 초과 (여러 행이 합쳐진 셀이라 OCR 입력으로 부적합)

## 4. 결과 요약 (필드 60개 중 25개 전달)

| 이미지 | 전달 필드 | 비고 |
|---|---|---|
| sample_1 | 6/6 | |
| sample_2 | 6/6 | |
| sample_4 | 6/6 | |
| sample_6 | 3/6 | address, lessor_name, lessee_name (계약내용 행 누락) |
| sample_8 | 2/6 | lessor_name, lessee_name (상단 표 붕괴) |
| sample_3 | 1/6 | lessor_name |
| sample_9 | 1/6 | lessor_name |
| sample_5 | 0/6 | 상단 표 셀 1개, 하단 표 누락 |
| sample_7 | 0/6 | 상단 표 과다 병합, 하단 표 누락 |
| sample_10 | 0/6 | 원거리 촬영 |

## 5. OCR 할 때 주의

1. **보증금 숫자/한글이 같은 셀**: `deposit_num` 과 `deposit_kor` 는 같은 셀(예: sample_1 id 23)이라 quad 가 같다. 칸 전체(`금 ... 원정 (₩ ... )`)가 들어간다.
2. **계약금 칸도 한 행 전체**: `down_payment` 셀에 `원정은 계약시에 지급하고 영수함. 영수자( ... )` 까지 같이 들어간다.
3. **성명 칸**: 표 선 기준이라 GT ROI 보다 조금 넓거나 좁을 수 있다 (GT 덮는 비율 0.72~0.97).
4. 파라미터를 바꿔 다시 돌리면 셀 id 가 바뀔 수 있다. 바뀌면 이 폴더를 다시 생성해서 전달한다.

## 6. 다시 만들기

```bash
python Task_10_Renewal.py      # output/common10/ 전체 재생성
python tail_roi.py     # handoff_tail/ 재생성 (data/common10/tail_gt_roi.json = tail gt/gt_roi.json 사본)
```

tail 쪽 실행 예:

```bash
python scripts/roi_ocr.py <bang_>/output/common10/handoff_tail/detected_roi_cells.json results/roi_detected_bang
python scripts/evaluate_fields.py --detected results/roi_detected_bang
```
