# 공통 10장 자동 구조 복원 결과 (opencv_grid_merge)

- 입력: tail 브랜치 `sample_data_jpg/sample_1~10.JPG` → `data/common10/` (같은 파일, sample_empty 제외)
- 코드: `Task_0930.py` 그대로 (PARAMS 변경 없음, 검출·병합 알고리즘 수정 없음)
- 실행: `python Task_10_Renewal.py` → 내부에서 `Task_0930.run_batch()` 호출
- 결과: `output/common10/<이미지명>/` + `output/common10/manifest.json`

## 1. 이미지별 결과

자동 status 는 `report.json` 값 그대로이고, "눈으로 확인"은 `output/common10/_preview/<이미지명>_final.jpg` 를 보고 정리한 것이다.
계약서 양식은 표 2개(상단: 부동산 표시·계약내용 / 하단: 임대인·임차인·공인중개사)이다.

| 이미지 | 자동 status | 표 | grid (행x열) | 셀 (merged) | 회전 보정 | 눈으로 확인 |
|---|---|---|---|---|---|---|
| sample_1 | ok | 2 | 11x11 / 11x13 | 92 (48) | 0° | **성공** — 상·하단 표 모두 복원 |
| sample_2 | check | 2 | 11x11 / 11x15 | 95 (53) | 0° | **성공** — 상·하단 표 모두 복원 (경계 누락 오판 의심 1건) |
| sample_4 | check | 2 | 11x11 / 8x9 | 73 (31) | 0° | **부분** — 상단 표 성공, 하단 공인중개사 영역 일부가 큰 셀로 합쳐짐 |
| sample_6 | check | 2 | 3x11 / 10x14 | 64 (35) | 0.40° | **부분** — 상단 표는 위 3행만 복원(계약내용 행 누락), 하단 표 대부분 복원 |
| sample_8 | check | 2 | 1x11 / 11x14 | 65 (37) | 1.07° | **부분** — 상단 표가 1행으로 붕괴, 하단 표 복원 |
| sample_3 | check | 2 | 4x10 / 3x11 | 18 (10) | 2.59° | **실패** — 두 표 모두 여러 행이 큰 셀로 합쳐짐 |
| sample_9 | check | 2 | 2x11 / 3x15 | 19 (11) | 0° | **실패** — 두 표 모두 여러 행이 큰 셀로 합쳐짐 |
| sample_5 | check | 1 | 1x10 | 1 (1) | 0.62° | **실패** — 상단 표 전체가 셀 1개, 하단 표 누락 |
| sample_7 | check | 1 | 4x11 | 6 (4) | -1.38° | **실패** — 상단 표 큰 셀 6개, 하단 표 누락 |
| sample_10 | check | 1 | 2x5 | 3 (2) | 2.32° | **실패** — 원거리 촬영, 상단 표 일부만 검출, 하단 표 누락 |

- 요약: 성공 2 / 부분 3 / 실패 5. 자동 status 는 ok 1 / check 9 / grid_fail 0 / error 0
- 처리 시간: 이미지당 0.8~1.4초 (`report.json` 의 `process_sec`)
- 실패 상세(유형·셀 id·근거)는 `output/common10/failure_cases.csv` 와 각 `report.json` 의 `failures` 에 그대로 기록됨

## 2. 자동 status 해석 시 주의

- `grid_fail` 은 **표를 하나도 못 만들었을 때만** 나온다. sample_5·7·10 처럼 하단 표만 빠진 경우는 `check` 로 나오고,
  빠진 표는 `failures` 에 따로 기록되지 않는다.
- 따라서 받는 쪽은 status 와 함께 `manifest.json` 의 `tables` 를 확인한다. **이 양식에서 `tables < 2` 이면 표 누락**이다.
- `check` 라도 sample_2 처럼 결과가 정상인 경우가 있다 (자동 검증은 의심 항목을 넓게 잡음).

## 3. 좌표계 (가장 중요)

| 파일 | 좌표 기준 | 크기 | 용도 |
|---|---|---|---|
| `cells_original.json` | 원본 이미지 (EXIF 회전 적용 후) | 3024 x 4032 | GT 비교, 원본 위 표시, tail ROI OCR |
| `cells.json` | 보정본 `<이미지명>_aligned.png` | 장마다 다름 (`report.json` 의 `image_size`) | 보정본에서 셀 자르기 |
| `cells_primitive*.json` | 위와 같음 | | 병합 전 격자 (비교용) |

- 10장 모두 휴대폰 EXIF 회전 정보가 있어 `<이미지명>_aligned.png` 가 생성된다 (회전 0° 인 장도 EXIF 회전은 적용됨).
- 원본 → 보정본 변환 행렬: `manifest.json` 의 `aligned.affine_original_to_aligned` (2x3, 회전 0° 이면 `null` = 좌표 동일)
- `cells_original.json` 의 bbox 는 셀 중심만 원본으로 되돌린 축 정렬 박스라, 원본에서 기울어진 셀과는 회전량만큼 모서리가 어긋난다
  (예: 폭 1000px 셀, 2.5° 회전 → 양 끝 높이 차 약 44px). 정확한 4점이 필요하면 `tail_roi.py` 의 `aligned_to_original_quad()` 를 쓴다.
- aligned 이미지와 `vis/` 는 용량(장당 약 90MB)이 커서 git 에 올리지 않았다. `python Task_10_Renewal.py` 를 실행하면 같은 파일이 다시 생성된다.

## 4. 폴더 구조

```
output/common10/
├─ manifest.json            10장 status, 표 수, 좌표 파일, 변환 행렬
├─ summary.csv              run_batch 요약 (이미지당 1줄)
├─ failure_cases.csv        실패 유형별 상세 (자동 검증 결과 그대로)
├─ _preview/                3_final.png 축소본 (하늘=general, 빨강=merged, 주황=검토 필요, 자홍=비직사각형 복구)
├─ handoff_tail/            tail 실험 C 입력 (docs/08_handoff_tail_common10.md)
└─ sample_N/
   ├─ cells_original.json   원본 좌표
   ├─ cells.json            보정본 좌표
   ├─ cells_primitive.json / cells_primitive_original.json
   ├─ report.json
   ├─ sample_N_aligned.png  (git 제외, 재실행 시 생성)
   └─ vis/                  (git 제외, 재실행 시 생성)
```
