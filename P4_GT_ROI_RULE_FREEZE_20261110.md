# P4 GT BBox / ROI Coverage 규칙 동결 (2026-11-10)

## 동결 대상과 기준
- 적용 범위: Development 19장 P4 평가의 GT BBox 정의 및 ROI Coverage 산식. 모델 성능·GT 좌표 검수 완료 선언과는 별개.
- 공식 상위 기준: 팀 공지에서 최종 기준으로 지정한 `04_data_collection_gt_protocol.md` §7 「ROI Coverage용 GT BBox 정의」「ROI Coverage 계산 규칙」. **해당 원본 파일은 현재 접근 가능한 GitHub 브랜치에 없어 문장 단위 대조는 미실시.** 상위 문서와 충돌하면 상위 문서를 우선하고 이 기록을 수정해야 한다.
- GT BBox: 원본 이미지 좌표계 `[x1,y1,x2,y2]`, x2>x1, y2>y1; 각 필드의 **실제 Value 영역만** 표시. 라벨·여백·`(인)`·도장·인감·서명 제외. 임대인·임차인 성명은 이름 문자열만 포함.
- ROI Coverage: `intersection_area(GT_BBox, ROI_BBox) / area(GT_BBox)`. 성공은 `coverage >= 0.90` (경계값 포함).
- GT BBox 유효 + ROI 미검출: coverage=0, 실패. GT BBox 부재·무효: coverage 미측정(N/A), 분모에서 제외. 이 두 경우를 혼동하지 않는다.
- Coverage는 ROI가 GT를 얼마나 포함하는지의 지표이며 OCR 텍스트 일치 여부와 독립적으로 판정한다. ROI Coverage 실패와 OCR_FAILURE가 함께 발생할 수 있으므로 상호배타적 실패 사유 집계만으로 Coverage 실패 건수를 대체하지 않는다.
- GT 원문 부재 시 Field Exact Match는 미측정(N/A)으로 표기하고 분모에서 제외한다. GT 텍스트 존재 시 예측 문자열과 원문 일치 여부를 평가한다. 공통 정규화 평가는 팀 공통 평가기를 우선한다.
- 필드 5종: address, deposit, contract_amount, lessor_name, lessee_name.
- GT는 평가에만 사용하며 ROI 생성, OCR 추론 또는 후보 선택에 사용하지 않는다.

## 코드 확인
- `evaluate_roi_coverage.py`: 유효 GT + ROI 없음 → 0.0; 유효 GT 없음 → N/A; ≥0.90 판정. 상기 규칙과 부합.
- `run_p4_pipeline.py`: OCR_FAILURE가 먼저 지정되면 Coverage 미달이 실패 사유로 별도 표기되지 않을 수 있음. Coverage 수치와 실패 사유를 독립적으로 집계해야 함.
- `run_p4_roi_reocr_v2.py`의 보조 `gt_coverage()`는 ROI 없음 → N/A로 처리하므로 공식 Coverage 집계에는 사용하지 않는다. 공식 집계는 `evaluate_roi_coverage.py` 기준.

## Development 19장 검증 결과 (기존 사용자 실행 결과)
- 19장, 95필드. ROI Coverage 측정 73건, 통과 66건, 미달 7건; 측정 불가 22건.
- 22건은 ROI 부재만을 의미하지 않음. GT가 없거나 무효인 경우와 ROI 부재를 구별해야 함.
- Raw Exact Match 29/95는 기존 출력값으로 기록하며 GT 텍스트 유효성 및 분모 검증 전에는 최종 논문 수치로 확정하지 않는다.

## 동결 범위 및 변경 관리
- **동결된 것:** 이 문서에 적힌 BBox 작성 및 Coverage 판정 규칙.
- **동결되지 않은 것:** 원본 상위 프로토콜과의 문장 단위 대조, 개별 GT 좌표 검수, 성능 합격 판정, 실패 사유 다중 라벨링 코드 개선.
- 이후 규칙 변경 시 변경 사유, 영향받는 평가 결과, 새 커밋을 남기고 재평가한다.
