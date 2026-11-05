# Dataset v1.0 — Development

## 1. Overview

본 데이터셋은 정형 임대차계약서의 핵심정보 추출 파이프라인에서
단계별 오류 전파를 분석하기 위한 평가 데이터셋입니다.

현재 Development 데이터는 총 19장, 13개 문서 그룹으로 구성됩니다.

전체 Dataset v1.0은 25장, 15개 문서 그룹이며,
나머지 6장은 Holdout 후보로 별도 관리합니다.

## 2. Dataset Structure

- manifest.csv: 이미지 메타데이터 및 분할 정보
- field_gt.json: 이미지별 핵심 5개 필드의 정답(GT)
- images/: 계약서 이미지

이미지 경로는 본 README가 위치한 폴더를 기준으로 합니다.

## 3. Ground Truth Fields

| Field | Description |
|---|---|
| address | 부동산 소재지 |
| deposit | 보증금 |
| contract_amount | 계약금 |
| lessor_name | 임대인 성명 |
| lessee_name | 임차인 성명 |

각 필드는 raw_text, normalized, bbox 등의 정보를 포함합니다.

원본 문서에 값이 없는 경우에는
status: not_present를 사용합니다.

## 4. Manifest

manifest.csv에는 다음 정보가 포함됩니다.

- image_id
- document_group_id
- filename
- condition
- perspective_direction
- perspective_level
- distance_level
- lighting
- fold
- crop
- usable
- split
- notes

동일한 document_group_id를 가진 이미지는
서로 다른 데이터 분할에 배치하지 않습니다.

## 5. Validation

2026-11-05 기준 검증 결과:

- 전체 이미지: 25장
- 전체 GT: 25개
- 전체 문서 그룹: 15개
- Development: 19장 / 13개 그룹
- Holdout 후보: 6장 / 2개 그룹
- 이미지 SHA-256 복사 검증: 불일치 0건
- 이미지 사용 가능 여부: 25장 yes
- 데이터 구조 검증: 오류 0건
- 패키지 분리 검증: PASS

본 검증은 파일 및 구조의 정합성을 확인한 것이며,
모든 GT 값의 의미적 정확성을 자동 보증하지는 않습니다.

## 6. Special Cases

common_007의 contract_amount는 원본 문서에 기재되지 않아
status: not_present로 표시했습니다.

평가 시 해당 필드를 일반적인 OCR 인식 실패와
구분하여 처리해야 합니다.

## 7. Holdout Policy

Holdout 후보 데이터는 Development와 분리하여 관리합니다.

최종 Holdout 확정 조건:

1. 개발 및 규칙 조정에 사용되지 않았는지 확인
2. 평가 규칙과 코드 확정
3. Commit SHA 기록
4. Holdout 동결
5. 최종 평가 1회 수행

Holdout 후보 이미지는 본 Development 패키지에 포함하지 않습니다.
