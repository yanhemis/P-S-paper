# 기존 평가 결과 보관 및 버전 관리 기록

## 1. 목적

수정된 Dataset v1.0을 이용한 재평가에 앞서, 기존 실험 코드와 평가 결과의 기준 버전을 기록한다.

기존 결과는 과거 Development 데이터로 수행한 실험의 참고 자료이며, **수정된 Dataset을 기준으로 산출한 최종 평가 결과로 취급하지 않는다.**

이 문서의 목적은 기존 결과를 추적하고, 향후 재평가 과정에서 기존 산출물이 덮어써지거나 새 결과와 혼동되는 것을 방지하는 것이다.

## 2. 기준 커밋 (Reference Commits)

| 구분 | 브랜치 | Commit SHA |
|---|---|---|
| P0~P3 및 H1 평가 코드·결과 | `origin/tail` | `3eb44cb8b452e62838b24860d2af6c68fb103e57` |
| P4 파이프라인 코드 | `origin/taegu` | `90c9c76534638823c984487ad05a0684614e5df3` |
| Gatekeeper 평가 코드·감사 보고서·P4 GT 변환 코드 | `dahye_cell_DetectionSurvey` | `0f58247` |

위 커밋 ID는 현재 확인한 각 브랜치의 기준 버전이다.

향후 브랜치가 업데이트되더라도 해당 커밋을 이용해 당시의 Git 관리 파일을 추적할 수 있다.

## 3. 기존 평가 결과 경로

`origin/tail` 브랜치에서 확인한 기존 평가 결과 경로는 다음과 같다.

- `results/eval/field_results.json`
- `results/eval/common_sample/field_results.json`
- `results/eval/detected_bang_pad0/field_results.json`
- `results/eval/detected_bang_pad25/field_results.json`
- `results/eval/pad_sweep/`
- `results/h1/`

이 경로들은 기존 실험 산출물을 식별하기 위한 기록이다.

**주의:** 이 문서를 작성했다고 해서 기존 결과의 독립적인 백업 사본이 생성되는 것은 아니다. 또한 모든 하위 산출물의 완전성을 검증한 것은 아니다.

## 4. 재평가 시 기존 결과 보호 규칙

1. **Development 데이터만 사용한다.** Holdout은 평가 설정과 코드가 확정되고 필요한 커밋 ID가 기록되기 전까지 접근하거나 평가하지 않는다.
2. 기존 `results/eval/`, `results/h1/` 및 기타 OCR 결과 폴더를 새 평가의 출력 경로로 재사용하지 않는다.
3. 수정 Dataset으로 평가할 때는 Dataset 버전과 파이프라인을 구분할 수 있는 새로운 결과 폴더를 사용한다.
4. `evaluate_fields.py` 실행 시 `--out-dir`를 명시하여 기존 결과 덮어쓰기를 방지한다.
5. `h1_quality.py`는 `results/h1/`에 출력하도록 고정되어 있으므로, 출력 경로를 안전하게 분리하기 전에는 재실행하지 않는다.
6. P4의 `--first-pass-cache`는 단일 이미지 PoC 재현용이다. 최종 end-to-end 실행 시간 측정에는 사용하지 않는다.
7. 공통 평가기의 CER 값은 현재 **DRAFT 기준**이다. 정규화 방식이 다른 과거 CER 수치와 혼용하지 않는다.
8. 수정된 Dataset을 받은 후에는 GT 무결성 검사를 먼저 진행하며, 검사를 통과하기 전까지 신규 OCR 평가를 시작하지 않는다.

## 5. 수정 Dataset 수령 후 확인할 사항

수정된 Dataset을 받으면 다음 항목을 확인한다.

- Development 이미지와 `manifest.csv`의 대응 관계
- 이미지별 `image_id` 및 `document_group_id`의 일관성
- 평가 대상 필드의 `raw_text`와 `normalized` GT 무결성
- P2 및 ROI Coverage 평가에 필요한 `bbox` 존재 여부
- P4 GT 변환 코드의 실제 Dataset 호환성
- 파이프라인별 입력·출력 경로 및 기존 캐시 재사용 여부

검증 후에만 새로운 Development 평가를 진행한다.

## 6. 현재 진행 상태

| 항목 | 상태 |
|---|---|
| 기존 평가 코드·결과 기준 커밋 확인 | 완료 |
| 기존 평가 결과 경로 확인 | 완료 |
| Gatekeeper 공통 평가 코드 및 감사 보고서 | GitHub 보관 완료 |
| P4 GT 변환 코드 | 작성 및 가상 데이터 기반 테스트 통과 |
| 수정된 Dataset v1.0 | 수령 대기 |
| 수정 Dataset 기반 신규 OCR 평가 | 미실행 |
| Holdout 평가 | 미실행 |
| 기존 결과의 별도 백업 사본 생성 | 미진행 |

**최종 원칙:** 수정 Dataset의 품질을 확인하고 평가 환경을 분리한 뒤, 동일한 기준으로 Development 평가를 다시 수행한다. 기존 결과는 비교 및 이력 추적 목적으로만 보존한다.