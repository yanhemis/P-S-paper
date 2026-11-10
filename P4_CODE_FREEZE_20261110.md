# P4 코드 기준 동결 기록 (2026-11-10)

## 동결 범위
- Anchor 매퍼 기준 파일 SHA256: `4dac6d87841bcd2e3fd5dd228f892b78f29e7da2f1d764cd4c2900b1458cc1ae`
- 19장 × 5필드 = 95개 Anchor 회귀 결과: `UNCHANGED 95`, 변경 및 회귀 0건 (사용자가 실행한 검증 로그 기준)
- P4 파이프라인 및 ROI 재OCR 코드: 정적 검사 통과 (사용자가 실행한 검사 로그 기준)
- Coverage 평가기는 기존 `field_mapping_result.json` 대신 최종 파이프라인 `field_rois.json`을 평가하도록 교체
- 공식 GT BBox 규칙: `04_data_collection_gt_protocol.md` 7절, 원본 이미지의 실제 Value 영역만 포함
- ROI Coverage 정의: `area(intersection(GT_BBox, ROI_BBox)) / area(GT_BBox)`, 성공 기준 ≥ 0.90

## 동결에 포함되지 않는 항목
- 19장 전체 신규 OCR 실행, 최종 Field Exact Match 정확도, 전체 ROI Coverage 성능은 **미검증**
- 19장 혼합 캐시의 30/94는 버전이 섞인 참고값으로 최종 성능이 아님
- 정적 검사 및 Anchor 회귀 통과는 성능 목표 달성을 의미하지 않음
- ROI 재OCR 선택 로직 수정 후 전체 동적 회귀 검증은 미실시

## 협업 기준
- 가은 학우는 공식 프로토콜 7절에 따라 `field_gt.json`의 Value-only BBox를 작성 가능
- OCR 성능 보고 및 논문용 최종 수치는 신규 E2E 실행 후 별도 확정
- 코드 동결 이후 수정은 별도 커밋으로 추적
