# tail 작업 — 난이도 촬영 / 이미지 품질 메타데이터

> 기준: `issue/05_current_team_tasks_20261101.md` 6절 (최우선), `issue/04_data_collection_gt_protocol.md` (세부 규칙)
> 마지막 업데이트: 2026-11-09
> 이전 OCR 배정(10/08)은 [`docs/plan_20261008_ocr_experiments.md`](docs/plan_20261008_ocr_experiments.md)에 보관

## 1. 역할과 완료 기준

기존 OCR 실험 확장이 아니라, **실제 실패를 유발할 수 있는 현실적인 촬영 조건 데이터를 수집하고 조건을 정확히 기록**한다.

**완료 기준: 난이도 조건 원본 5~8장과 조건 메타데이터가 가은 학우(GT / Dataset Manager)에게 전달되면 완료.**

GT 작성·manifest 통일·development/holdout 분리는 가은 학우, 최종 수치는 dahye 담당이다.

## 2. 체크리스트

### 촬영·기록 (완료)
- [x] 신규 usable 원본 9장 (난이도 6 + baseline 3, 목표 5~8장 초과) → `sample_data_jpg/sample_data_v2/`
  - docA: perspective, distance, baseline / docB: lighting, fold, baseline / docC: perspective, lighting, baseline
- [x] 조건: perspective, distance, lighting, fold (crop은 없음)
- [x] 무보정 원본, GPS 제거 (회전 EXIF 유지), 방향만 바로잡은 사본은 `oriented/`
- [x] 이미지별 `usable`·이유·notes 기록: [`manifest_tail.csv`](sample_data_jpg/sample_data_v2/manifest_tail.csv)
- [x] 기입 내용(GT 초안, 종이에 쓴 대로, 기입자 확인 완료): [`fake_contract_data_v2.md`](sample_data_jpg/sample_data_v2/fake_contract_data_v2.md)
- [x] 개인정보 없는 가상 문서 사용
- [x] 이전 OCR 결과를 dahye에게 넘길 인계 문서 작성: [`docs/handoff_dahye_E0_E4.md`](docs/handoff_dahye_E0_E4.md)

### 가은 학우 전달·bbox (완료)
- [x] 신규 촬영본 전달 확인: 가은 학우 `dataset-v1`(Development 19장)에 docA 3장(tail_001 perspective, tail_002 distance, tail_007 baseline)이 반영됨. docB·docC 6장은 holdout 후보라 Development에 없음
- [x] docA 3장 필드별 ROI bbox 15개 라벨링: [`roi_bbox_docA.json`](sample_data_jpg/sample_data_v2/roi_bbox_docA.json), 확인용 [`roi_check/`](sample_data_jpg/sample_data_v2/roi_check/)
  - 기준: 공통 10장과 같이 **값이 기재되는 입력 칸을 감쌈**, 좌표는 EXIF 회전 후(3024×4032) `[x1,y1,x2,y2]`. 팀장 가이드(`roi_coverage_gt_bbox_guide.md`)의 "값 영역" 정의와 칸 기준이 다르다는 점은 가은 학우가 샘플 1~10 기준으로 정리하라고 답함
  - tail_001(사선 강함)은 칸이 비스듬해 박스가 옆 칸 일부를 포함. 눈으로 지정한 값이라 검수 필요
  - 희원 라벨(`heewon/field_gt_heewon_labeled (2).json`)에도 같은 3장이 있으나 "두 벌 라벨은 신경 쓰지 않아도 됨"(가은 학우 답)

### 남은 일 (사람이 해야 함)
- [ ] 라벨 수정본(`f908c2b`)을 `tail` 브랜치에 push하고 가은 학우에게 알리기
- [ ] **희원과 문서 그룹 맞추기**: docA/docB를 같은 원본으로 찍었는지, `document_group_id` 일치 여부 (현재 Development manifest는 `heewon_docA`, `tail_docA`로 별개 그룹)
- [ ] (선택) docB·docC(holdout) bbox: 가은 학우가 요청하면 진행. 공개 전 holdout이라 요청 전에는 하지 않음
- [ ] (선택) docA 사선 사진은 가이드(10~20°)보다 강함(추정 25~30°). 자동 구조 복원이 tail_001에서 표를 못 찾음(`bang_` 결과 TABLE_MISSING). 난이도 샘플로 그대로 둘지는 가은 학우 판단
- [ ] (선택) 가장자리 누락(crop) 사진 1장 필요 여부
- [ ] dahye에게 인계 문서 전달
- [ ] 이전 커밋에 남은 GPS 원본 사진 처리: 히스토리 재작성이라 팀 합의 필요. 합의 전 push 보류 (현재 `tail` 브랜치는 origin보다 1커밋 앞섬)

## 3. 하지 않을 것

- 신규 OCR/구조 모델 추가, 대규모 신규 실험축
- 같은 사진을 resize/compress해 별도 표본으로 세기
- 같은 문서 그룹을 development/holdout에 나누기 (split은 가은 학우가 확정)
- 촬영 후 crop/filter/밝기/원근 보정

## 4. 진행 보고 (팀 형식, `05` 문서 9절)

```text
[tail]
1. 현재 작업: 난이도 촬영 데이터 정리 및 전달 준비
2. 완료한 것: 신규 9장(난이도 6 + baseline 3) 촬영·전달, GPS 제거, manifest·기입 내용 문서, 방향 보정 사본, docA 3장 ROI bbox 15개
3. 생성/수정 파일: sample_data_jpg/sample_data_v2/ (이미지, oriented/, manifest_tail.csv, fake_contract_data_v2.md, roi_bbox_docA.json, roi_check/)
4. 막힌 점: 이전 커밋의 GPS 원본 처리(팀 합의 필요)
5. 다음 작업: 희원과 문서 그룹 확인, dahye 인계, holdout bbox는 요청 시
```

## 5. 이전 작업 요약 (OCR 실험, 기존 공통 10장)

Full OCR 29/49 → 원근 보정 31/49, GT ROI 31/49, `bang_` Detected ROI 13/49. 병목은 ROI 누락과 소재지 문자 인식. 상세는 [`README.md`](README.md), [`docs/handoff_dahye_E0_E4.md`](docs/handoff_dahye_E0_E4.md), [`results/eval/recognition_errors.md`](results/eval/recognition_errors.md).
