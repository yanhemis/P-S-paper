# 추가 인원 B 전달: End-to-End 통합용 Cell/ROI 입출력 명세 (Task_0930.py)

## 1. 역할
계약서 이미지 1장 → 표 셀(Cell/ROI) bbox 목록(JSON). OCR·Anchor-ROI 앞 단계.

## 2. 환경
- Python 3, `python -m pip install opencv-python numpy pillow matplotlib`
- matplotlib는 그림을 띄울 때(`show=True`)만 사용

## 3. 입력
- 이미지 경로: .jpg .jpeg .png .bmp .tif .tiff (한글 경로 가능, 휴대폰 촬영 회전 정보 자동 반영)
- 선택: `params` dict (`PARAMS`의 키를 덮어씀, 예: `{"line_open_base": 24}`)

## 4. 호출 방법
```python
import Task_0930 as t

# (1) 한 장 처리 + 파일 저장
s = t.run_pipeline("contract.jpg", out_dir="output", show=False, verbose=False)
# s["status"]: "ok" / "check" / "grid_fail",  s["cells"]: 셀 개수,  s["failures"]: 경고 목록

# (2) 폴더 일괄 처리 → output/summary.csv, output/failure_cases.csv
t.run_batch("input_dir", out_dir="output")

# (3) 파일 저장 없이 메모리에서만
img, _ = t.load_image("contract.jpg")
r = t.process(img, t.PARAMS)
r["cells"]             # 셀 목록 (보정본 좌표, cells.json 키 + "irregular"(bool))
r["img"]               # 기울기 보정 이미지 (BGR numpy 배열)
r["skew"]["affine"]    # 원본 → 보정본 좌표 변환 행렬 (2x3), 보정 안 했으면 None
```

## 5. 출력 (`output/<이미지명>/`)
| 파일 | 내용 |
|---|---|
| `cells.json` | 최종 셀, 보정본 좌표 → OCR 크롭용 |
| `cells_original.json` | 같은 셀, 원본 이미지 좌표 → 원본 위 표시·GT 평가용 |
| `cells_primitive.json` / `cells_primitive_original.json` | 병합 전 격자 셀 (비교용) |
| `<이미지명>_aligned.png` | 보정본 이미지 (기울기·회전 보정했을 때만 생성) |
| `report.json` | status, 실패 사례, 파라미터, 처리 시간 |
| `vis/` | 확인용 그림 / `roi/`: 셀 크롭 (`save_roi=True`일 때) |

이 폴더의 `cells.json`, `cells_original.json`, `report.json`은 sample.jpg 실행 예시입니다.

## 6. cells.json 스키마 (고정)
| 키 | 타입 | 설명 |
|---|---|---|
| `image` | str | bbox 기준 이미지 파일명 |
| `source_image` | str | 원본 파일명 |
| `method` | str | `"opencv_grid_merge"` |
| `rotation_deg` | float | 적용한 회전 각도 (`cells_original.json`은 0.0) |
| `cells[].id` | int | 0부터, 표 순서 → 위→아래 → 왼→오른쪽 |
| `cells[].table` | int | 페이지 안 표 번호 (위→아래) |
| `cells[].bbox` | [int x4] | `[x1, y1, x2, y2]`, x1<x2, y1<y2, 이미지 범위 안, 셀끼리 겹치지 않음 |
| `cells[].type` | str | `"general"`(격자 1칸) / `"merged"`(2칸 이상) |
| `cells[].primitive_cells` | [[row, col], ...] | 그 표 안의 격자 좌표 |

## 7. 실패 시 동작
| 상황 | 동작 |
|---|---|
| 표를 못 찾음 | 예외 없음. `status: "grid_fail"`, `cells: []` (빈 목록) 저장 |
| 결과는 나왔지만 자동 검증 경고 | `status: "check"`, 내용은 `report.json`의 `failures` |
| 이미지 파일 없음 / 읽기 실패 | `FileNotFoundError` / `IOError` |
| `run_batch` 중 한 장 오류 | 그 이미지만 `status: "error"`로 기록하고 나머지 계속 진행 |

## 8. 성능 (sample.jpg, 3000x4000 촬영본)
- 처리 약 1.5초, 결과 파일 저장 포함 약 4초

## 9. 주의
- cells.json 키와 형식은 고정. 바뀌면 미리 공지
- 파라미터를 바꾸면 셀 id 순서가 달라질 수 있음
