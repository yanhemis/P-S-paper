# tail 작업 — 난이도 촬영 / 이미지 품질 메타데이터

> 재배정일: 2026-10-21 (기준: `issue/03_team_execution_plan_20261021.md` E절, `issue/04_data_collection_gt_protocol.md`, `issue/assignment_member_A_ocr_roi_field_accuracy.md`)
> 이전 배정(10/08: E0~E5 OCR 비교)은 [`docs/plan_20261008_ocr_experiments.md`](docs/plan_20261008_ocr_experiments.md)에 보관. 최종 수치 확정은 dahye 담당.
> 마지막 업데이트: 2026-10-29

## 1. 담당 목표

기존 H1 이미지 품질 분석 경험을 이용해 **실제 실패를 유발할 수 있는 촬영 조건을 의도적으로 수집하고 조건을 정확히 기록**한다. OCR 모델 개발은 주업무가 아니다.
목표: **신규 usable 이미지 5~8장** (팀 전체 신규 10~15장, 총 20~25장 중 일부).

## 2. 해야 할 일

### 촬영
- [ ] `heewon`과 같은 원본 문서 그룹(`document_group_id`)을 일부 공유해 조건만 다른 비교쌍을 만든다 → **heewon과 그룹 ID·문서 합의가 선행**
- [ ] 우선 조건 4종
  - `perspective`: 좌/우/상단 사선, 약 10~20도 (mild/moderate)
  - `distance`: 글자는 읽히지만 유효 해상도가 떨어지는 거리
  - `lighting`: 낮은 조도 / 한쪽 조명 / 약한 그림자
  - `fold_or_crop`: 약한 접힘·휨 또는 가장자리 소량 누락
- [ ] 현실적인 스마트폰 촬영 수준 유지 (읽을 수 없는 극단 조건, 강한 반사 금지)
- [ ] 촬영 후 crop/filter/밝기/원근 보정 금지, 메신저로 압축된 파일이 아닌 원본
- [ ] 개인정보 없는 가상 계약서 사용
- [ ] 실패할 것 같은 이미지도 삭제하지 말고 `usable` 여부와 이유 기록

### 기록·전달
- [ ] 파일명 `<document_group_id>_<condition>_<index>.jpg` (예: `docA_perspective_left_01.jpg`)
- [ ] 이미지별 manifest 값: `document_group_id, condition, perspective_direction, perspective_level, distance_level, lighting, fold, crop, usable, notes` (`split`은 추가 인원 B만 확정)
- [ ] H1 해석과 연결해 notes를 구체적으로 작성 (기존 근거: #10 거리 유효 dpi 207, #7 접힘, #4 가장자리 — `results/h1/summary.md`)
- [ ] 공유 전 GPS 제거: `exiftool -gps:all= -overwrite_original <파일>` (EXIF 전체 삭제 금지: 회전 정보 필요)
- [ ] 원본 이미지 + 메타데이터 + unusable 사유를 추가 인원 B에게 전달

### 인계 / 정리
- [x] 기존 E0/E1/E3/E4 결과를 dahye에게 인계할 문서 작성 → [`docs/handoff_dahye_E0_E4.md`](docs/handoff_dahye_E0_E4.md) (전달은 사람이 해야 함)
- [ ] 이전 커밋에 남은 GPS 원본 사진 처리: 프로토콜 11절과 관련, 히스토리 재작성이라 팀 합의 필요
- [ ] 촬영 조건 매핑 확인 (`sample_5/6`, `sample_8/9`) → 기존 10장 H1 표에 계획 조건 열 추가 (선택)

### 진행 상황 (2026-11-01)
- [x] 신규 촬영 9장 완료: 난이도 6장 docA(사선·거리), docB(저조도·접힘), docC(사선·저조도) + 기준(baseline) 3장. 무보정 원본, GPS 제거 → `sample_data_jpg/sample_data_v2/`
- [x] 메타데이터 `manifest_tail.csv`, 기입 내용(GT 초안) `fake_contract_data_v2.md`, 방향 보정 사본 `oriented/`
- [ ] 기입자 확인(docA 이름, docB 날짜, docC 이름), docA 사선 각도 재판단, 추가 인원 B 전달

## 3. 하지 않을 것

- 신규 OCR/구조 모델 추가, 대규모 신규 실험축
- 같은 사진을 resize/compress해 별도 표본으로 세기
- 같은 문서 그룹을 development/holdout에 나누기 (split은 추가 인원 B가 그룹 단위로 결정)
- GT 작성·split 확정 (추가 인원 B), 최종 수치 확정 (dahye)

## 4. 완료된 이전 작업 (요약)

기존 공통 10장: Full OCR 29/49 → 원근 보정 31/49, GT ROI 31/49, `bang_` Detected ROI 13/49. 병목은 ROI 누락과 소재지 문자 인식. 상세는 [`README.md`](README.md), [`docs/handoff_dahye_E0_E4.md`](docs/handoff_dahye_E0_E4.md), [`results/eval/recognition_errors.md`](results/eval/recognition_errors.md).

## 5. 연결

- `heewon`: baseline/통제 촬영 5~6장 → 문서 그룹 공유
- 추가 인원 B: 이미지·메타데이터 수령, GT·manifest·split
- `bang_`/`taegu`: development에서 설정 확정 후 동결, holdout은 동결 후 공개
- `dahye`: P0~P4 최종 수치

## 6. 실행 순서

1. heewon과 문서 그룹·조건 분담 합의
2. 촬영 + 즉시 메타데이터 기록 + GPS 제거
3. 추가 인원 B에게 전달
4. dahye에게 인계 문서 전달
5. GPS 이전 커밋 처리 안건 팀 공유
