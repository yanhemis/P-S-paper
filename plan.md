# tail 작업 — 난이도 촬영 / 이미지 품질 메타데이터

> 기준: `issue/05_current_team_tasks_20261101.md` 6절, `issue/04_data_collection_gt_protocol.md`
> 마지막 업데이트: 2026-11-11
> 이전 OCR 배정(10/08)은 [`docs/plan_20261008_ocr_experiments.md`](docs/plan_20261008_ocr_experiments.md)에 보관

## 1. 역할

실제 실패를 유발할 수 있는 촬영 조건 데이터를 수집하고 조건을 정확히 기록한다. GT 작성·manifest 통일·development/holdout 분리는 가은 학우, 최종 수치는 dahye 담당이다.

## 2. 완료한 것

- 신규 9장(난이도 6 + baseline 3) 촬영·전달 → `sample_data_jpg/sample_data_v2/` (무보정, GPS 제거, 방향 보정 사본은 `oriented/`)
- 메타데이터 [`manifest_tail.csv`](sample_data_jpg/sample_data_v2/manifest_tail.csv), 기입 내용 [`fake_contract_data_v2.md`](sample_data_jpg/sample_data_v2/fake_contract_data_v2.md)
- 가은 학우 `dataset-v1` 반영 확인: Development에 docA 3장(tail_001·002·007), Holdout에 docB·docC 6장(tail_003·004·005·006·008·009)
- 이전 OCR 결과 인계 문서: [`docs/handoff_dahye_E0_E4.md`](docs/handoff_dahye_E0_E4.md)
- 성명 확정: docC 임대인 허재석 / 임차인 제갈다온 (Holdout GT도 같은 값)

## 3. ROI bbox 현황

파일: [`roi_bbox_docA.json`](sample_data_jpg/sample_data_v2/roi_bbox_docA.json)(tail_001·002·007), [`roi_bbox_docBC.json`](sample_data_jpg/sample_data_v2/roi_bbox_docBC.json)(나머지 6장), 확인용 [`roi_check/`](sample_data_jpg/sample_data_v2/roi_check/). 좌표는 EXIF 회전 후(3024×4032) `[x1,y1,x2,y2]`.

| 기준 | 이미지 |
|---|---|
| **Value-only** (11-08 확정, 값 글자를 감싸는 최소 영역) | tail_001, tail_005 (11-11 재라벨) |
| 입력 칸 기준 (금액 칸은 "원정" 앞까지) | tail_002, 003, 004, 006, 007, 008, 009 |

- tail_001 계약금: Value-only `[1255,930,1430,1008]`이 최종. 입력 칸 값 `[814,781,1445,1010]`과 Dataset GT의 옛 값 `[...,1403,...]`는 폐기
- 사선 사진(tail_001·005)은 축 정렬 박스가 소재지에서 인접 칸 글자를 일부 포함함

## 4. 남은 일

- [ ] 가은 학우에게 tail_001·005 Value-only 좌표 전달 (Dataset GT·Holdout GT의 tail_005는 아직 옛 입력 칸 값)
- [ ] 나머지 7장도 Value-only로 재라벨할지 결정
- [ ] 희원과 문서 그룹 맞추기 (현재 Development manifest는 `heewon_docA`, `tail_docA`로 별개 그룹)
- [ ] dahye에게 인계 문서 전달
- [ ] 이전 커밋에 남은 GPS 원본 사진 처리: 히스토리 재작성이라 팀 합의 필요
- [ ] (선택) docA 사선 사진이 가이드(10~20°)보다 강함(추정 25~30°). 난이도 샘플로 둘지는 가은 학우 판단
- [ ] (선택) 가장자리 누락(crop) 사진 1장 필요 여부

## 5. 하지 않을 것

- 신규 OCR/구조 모델 추가, 대규모 신규 실험축
- 같은 사진을 resize/compress해 별도 표본으로 세기
- 같은 문서 그룹을 development/holdout에 나누기
- 촬영 후 crop/filter/밝기/원근 보정

## 6. 이전 작업 요약 (OCR 실험, 공통 10장)

Full OCR 29/49 → 원근 보정 31/49, GT ROI 31/49, `bang_` Detected ROI 13/49. 병목은 ROI 누락과 소재지 문자 인식. 상세는 [`README.md`](README.md), [`results/eval/recognition_errors.md`](results/eval/recognition_errors.md).
