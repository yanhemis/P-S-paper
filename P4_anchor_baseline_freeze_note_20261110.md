# P4 Anchor 매퍼 기준 버전 검증 기록 (2026-11-10)

## 확정된 사실
- `anchor_field_mapper.py`는 실패한 신규 fallback을 제거하고 기존 기준 버전으로 복원함.
- 기준 파일 SHA256: `4dac6d87841bcd2e3fd5dd228f892b78f29e7da2f1d764cd4c2900b1458cc1ae`.
- 기존 19개 이미지 × 5개 필드 = 95개 Anchor 결과를 백업본과 비교함.
- 결과: UNCHANGED 95, REGRESSION 0, GAIN 0, BBOX_CHANGED 0.
- 실패한 후보: `docB_perspective.jpg` 계약금 `[1017,852,1166,938]`. 이미지 검토에서 빈 표 영역을 가리켜 불채택. 실패 패치는 별도 백업 보존.

## 이 검증으로 확정할 수 없는 것
- 95개 결과가 GT 기준으로 모두 정확하다는 뜻이 아님. 동일한 결과를 재현했다는 뜻임.
- 19장 전체에 대해 신규 v6 OCR을 수행한 결과가 아님.
- ROI Coverage ≥0.90 달성이나 2차 OCR 정확도 개선을 증명하지 않음.
- `results/p4_development_v6`의 10장과 `results/p4_development`의 나머지 9장은 버전이 다른 캐시임. 혼합 집계를 v6 전체 성능으로 발표하면 안 됨.

## 팀원에게 전달할 상태
- Anchor 매퍼: 기존 기준 버전 유지 / 실패한 보완 규칙 미채택.
- GT BBox 규칙: `04_data_collection_gt_protocol.md` 7절의 `ROI Coverage용 GT BBox 정의`, `ROI Coverage 계산 규칙`을 공식 기준으로 사용. GT는 원본 이미지의 실제 Value 영역만 지정하고 `(인)`, 도장, 서명 등은 제외.
- ROI Coverage: `area(intersection(GT_BBox, ROI_BBox))/area(GT_BBox)`; 성공 기준 0.90 이상. OCR 문자열 정확도와 별도 보고.
- OCR 성능: v6 캐시 10장 49개 유효 GT 기준 raw exact 22/49 (44.9%), 공백 무시 24/49 (49.0%). 19장 혼합 캐시 raw exact 30/94 (31.9%)는 버전 혼합 참고값이며 최종 v6 성능이 아님.

## 최종 전달 전 체크
1. `git status --short`로 미추적 임시 파일 및 수정 파일 확인.
2. `python -m py_compile anchor_field_mapper.py` 실행.
3. `python regress_p4_anchor_patch_fixed.py`로 95 UNCHANGED 확인.
4. GT BBox 프로토콜과 평가 스크립트 일치 여부 별도 확인; ROI Coverage 수치를 확인하지 않았다면 미검증으로 표기.
5. 전달할 코드/결과만 선별해 커밋하고 `git rev-parse --short HEAD`로 실제 커밋 해시 확인. 미확인 해시를 전달하지 말 것.

## 전달 문구 초안
P4 Anchor 탐지 코드는 기존 검증 버전으로 유지하기로 했습니다. 19장·95필드 기준 회귀 비교에서 95건 모두 동일했고 신규 오검출 후보는 제외했습니다. 따라서 Anchor 매퍼 기준 버전은 고정 가능하지만, ROI Coverage 및 19장 전체 v6 OCR 정확도는 별도 검증 항목입니다. GT BBox는 공식 프로토콜 7절 기준으로 작성해 주세요. 검증 완료한 코드의 커밋 해시는 커밋·푸시 후 별도 공유하겠습니다.
