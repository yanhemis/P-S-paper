# tail 작업 — 난이도 촬영 / 이미지 품질 메타데이터

> 기준: `issue/05_current_team_tasks_20261101.md` 6절 (최우선), `issue/04_data_collection_gt_protocol.md` (세부 규칙)
> 마지막 업데이트: 2026-11-01
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

### 남은 일 (사람이 해야 함)
- [ ] **가은 학우에게 전달**: `sample_data_v2/` 폴더 (원본, `oriented/`, manifest, 기입 내용 문서)
  - 알릴 것: docC는 **다른 사람이 기입**(필체 다름), docA 임대인·임차인은 계획과 다르게 기입(종이 기준이 GT), baseline도 3장 포함, `oriented/` 사본 사용 여부 결정 필요
- [ ] **희원과 문서 그룹 맞추기**: docA/docB를 같은 원본으로 찍었는지, `document_group_id`가 일치하는지
- [ ] docA 사선 사진이 가이드(10~20°)보다 강함(추정 25~30°). 그대로 쓸지, 약한 각도로 1장 더 찍을지 결정
- [ ] (선택) 가장자리 누락(crop) 사진 1장 필요 여부 판단
- [ ] dahye에게 인계 문서 전달
- [ ] 이전 커밋에 남은 GPS 원본 사진 처리: 히스토리 재작성이라 팀 합의 필요. 합의 전 push 보류

## 3. 하지 않을 것

- 신규 OCR/구조 모델 추가, 대규모 신규 실험축
- 같은 사진을 resize/compress해 별도 표본으로 세기
- 같은 문서 그룹을 development/holdout에 나누기 (split은 가은 학우가 확정)
- 촬영 후 crop/filter/밝기/원근 보정

## 4. 진행 보고 (팀 형식, `05` 문서 9절)

```text
[tail]
1. 현재 작업: 난이도 촬영 데이터 정리 및 전달 준비
2. 완료한 것: 신규 9장(난이도 6 + baseline 3) 촬영, GPS 제거, manifest·기입 내용 문서, 방향 보정 사본
3. 생성/수정 파일: sample_data_jpg/sample_data_v2/ (이미지, oriented/, manifest_tail.csv, fake_contract_data_v2.md)
4. 막힌 점: docA 사선 각도 판단, 이전 커밋의 GPS 원본 처리(팀 합의 필요)
5. 다음 작업: 가은 학우에게 전달, 희원과 문서 그룹 확인, dahye 인계
```

## 5. 이전 작업 요약 (OCR 실험, 기존 공통 10장)

Full OCR 29/49 → 원근 보정 31/49, GT ROI 31/49, `bang_` Detected ROI 13/49. 병목은 ROI 누락과 소재지 문자 인식. 상세는 [`README.md`](README.md), [`docs/handoff_dahye_E0_E4.md`](docs/handoff_dahye_E0_E4.md), [`results/eval/recognition_errors.md`](results/eval/recognition_errors.md).
