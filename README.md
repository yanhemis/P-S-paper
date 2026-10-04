# 계약서 표 셀 검출 + 병합 셀 복원 (bang_)

임대차계약서 이미지에서 표선을 검출해 셀 격자(primitive grid)를 만들고,
경계선이 없는 칸을 Union-Find로 묶어 병합 셀(merged cell)까지 복원하는 OpenCV 기반 파이프라인입니다.
결과는 다른 담당자(평가, OCR, 통합)가 그대로 읽을 수 있는 `cells.json`으로 저장합니다.

- 메인 코드: `Task_0930.py`
- 이전 버전: `TestResult.py` (보관용, 아래 "이전 버전" 참고)

## 처리 흐름
1. 이미지 로드 (휴대폰 회전 정보 자동 반영) → 기울기 보정 (HoughLinesP)
2. 이진화 (CLAHE + adaptive threshold, 해상도 비례 파라미터)
3. 수평/수직선 추출 → 끊어진 선 잇기 → 표 영역 분리 (한 페이지 여러 표 지원)
4. 셀 경계 판정 → Union-Find 병합 → 비직사각형 병합 복구
5. 자동 검증 (실패 유형 분류) → cells.json + 시각화 + 리포트 저장

## 폴더 구조
```
P-S-paper/
├─ Task_0930.py          메인 코드
├─ TestResult.py         이전 버전 (보관용)
├─ Test_image_file/      입력 이미지 (sample.jpg)
├─ output/<이미지명>/    실행 결과
└─ docs/                 성공·실패 사례 문서
```

## 설치
```
python -m pip install opencv-python numpy pillow matplotlib
```
- Anaconda (base)에는 numpy, pillow, matplotlib가 이미 있으므로 `opencv-python`만 설치하면 됨
- venv를 쓰다가 `No module named 'cv2'`가 나오면, venv가 켜진 상태에서 위 명령으로 다시 설치

## 실행
프로젝트 폴더에서 실행합니다.

| 목적 | 명령 |
|---|---|
| 한 장 처리 (`Test_image_file/sample.jpg`, 그림 표시) | `python Task_0930.py` |
| 폴더 전체 일괄 처리 → `output/summary.csv`, `output/failure_cases.csv` | `python -c "import Task_0930 as t; t.run_batch()"` |
| 셀 크롭 이미지까지 저장 (`output/<이미지명>/roi/`) | `python -c "import Task_0930 as t; t.run_pipeline(show=False, save_roi=True)"` |
| 선 추출 커널 비교 (이전 코드 0.4 vs 현재) | `python -c "import Task_0930 as t; t.compare_line_settings()"` |
| 파라미터를 바꿔서 실행 (예: line_open_base 24) | `python -c "import Task_0930 as t; t.run_pipeline(show=False, params={'line_open_base': 24})"` |

`python Task_0930.py` 실행 시 그림 창을 모두 닫아야 결과 요약이 출력됩니다.

## 출력 (`output/<이미지명>/`)
| 파일 | 내용 | 좌표 기준 |
|---|---|---|
| `cells.json` | 최종 셀 (general / merged) | 보정본 `<이미지명>_aligned.png` |
| `cells_primitive.json` | 병합 전 격자 셀 (비교용) | 보정본 |
| `cells_original.json` | `cells.json`과 같은 셀 | 원본 이미지 |
| `cells_primitive_original.json` | `cells_primitive.json`과 같은 셀 | 원본 이미지 |
| `<이미지명>_aligned.png` | 기울기 보정한 이미지 (보정했을 때만 생성) | - |
| `report.json` | 검증 결과, 실패 사례, 경계 점수, 파라미터, 처리 시간 | - |
| `vis/0~4_*.png` | 선 추출 / primitive grid / 경계 판정 / 최종 셀 / 단계 비교 그림 | - |

- GT가 원본 이미지 위에 그려졌다면 `cells_original.json`으로 평가
- OCR용으로 셀을 잘라 쓸 때는 `cells.json` + `<이미지명>_aligned.png` 사용

## cells.json 형식 (고정)
```json
{
  "image": "sample_aligned.png",
  "source_image": "sample.jpg",
  "method": "opencv_grid_merge",
  "rotation_deg": -1.061,
  "cells": [
    {"id": 0, "table": 0, "bbox": [x1, y1, x2, y2], "type": "merged", "primitive_cells": [[0, 0], [0, 1]]}
  ]
}
```
- `bbox`: 정수 픽셀 `[왼쪽, 위, 오른쪽, 아래]`, 셀끼리 겹치지 않음
- `type`: `general`(격자 1칸) / `merged`(격자 2칸 이상)
- `table`: 페이지 안 표 번호 (위→아래), `primitive_cells`의 `[행, 열]`은 그 표 안 좌표
- 정렬: 표 순서 → 위→아래 → 왼→오른쪽, `id`는 그 순서대로 0부터

## 주요 파라미터 (`Task_0930.py`의 `PARAMS`)
| 파라미터 | 값 | 의미 |
|---|---|---|
| `ref_diag` | 2000 | 해상도 스케일 기준 (이미지 대각선 2000px일 때 스케일 1.0) |
| `deskew_min_angle` | 0.3 | 이보다 작은 기울기(도)는 보정하지 않음 |
| `line_open_base` | 30 | 글자 획 제거용 선 추출 커널 (x 스케일). 한 행 높이보다 길면 짧은 세로 경계가 사라짐 |
| `close_ratio` | 0.01 | 끊어진 선을 잇는 길이 (이미지 폭/높이 대비) |
| `anchor_h_ratio` / `anchor_v_ratio` | 0.15 / 0.03 | 표로 인정할 긴 선의 최소 길이 (폭/높이 대비) |
| `gap_thresh_base` | 10 | 같은 선으로 묶는 간격 (x 스케일) |
| `presence_ratio` | 0.5 | 경계선이 이 비율 넘게 이어져 있으면 "경계 있음" |
| `max_merged_area_ratio` | 0.3 | 병합 셀이 표 면적의 이 비율을 넘으면 과다 병합 의심 |
| `hidden_line_ratio` | 0.8 | 셀 안을 이 비율 이상 가로지르는 선이 있으면 선 검출 실패로 기록 |

## 현재 결과 (sample.jpg, IoU 0.5)
| 방법 | Precision | Recall | F1 |
|---|---|---|---|
| Grid only (`cells_primitive_original.json`) | 28.1% | 68.4% | 39.9% |
| Grid + Spanning Recon (`cells_original.json`) | 90.7% | 82.1% | 86.2% |

- 평가: 공통 evaluator `evaluate.py` + `sample.jpg_gt.json` (GT 95셀)
- 사례 정리: `docs/02_success_cases.md`, `docs/03_failure_cases.md`

## 알려진 한계
- 한 행 높이보다 짧은 세로 경계는 선 추출에서 지워져 라벨·값 칸이 합쳐질 수 있음 (`line_open_base` 조정 검토 중)
- 원근 왜곡(사다리꼴 촬영)은 보정하지 않음 → 가장자리 열 bbox가 조금 어긋날 수 있음
- 선이 없는 표(borderless)는 지원하지 않음

## 이전 버전 (`TestResult.py`)
- 기울기 보정 → 이진화 → 표선 검출 → Union-Find 병합 → `cells.json` 저장 (`python TestResult.py`)
- 선 추출 커널이 이미지 높이의 40%라, sample.jpg 같은 촬영본에서는 표선이 모두 지워져 "표선 검출 실패"가 발생
- 현재는 `Task_0930.py`를 사용