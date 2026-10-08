# bang_ 최종 작업 — 자동 구조 복원 결과 공급

> 재설정일: 2026-10-08
> 내부 마감: 2026-10-09

## 담당 목표

새 알고리즘을 더 만드는 것이 아니라, 현재 OpenCV 구조 복원 파이프라인을 **공통 10장 데이터에 적용해 다음 단계가 바로 사용할 수 있는 원본 좌표 결과를 공급**한다.

## 해야 할 일

- [ ] `tail` 공통 10장에 `run_batch()` 실행
- [ ] 각 이미지별 `cells_original.json` 저장
- [ ] 필요 시 `cells.json`, `report.json`, aligned image 함께 저장
- [ ] 원본 좌표와 보정본 좌표를 명확히 구분
- [ ] 실패 상태(`check`, `grid_fail`)도 그대로 기록
- [ ] 대표 성공/실패 사례 최소 3개씩 정리
- [ ] `tail`에게 Detected ROI OCR용 결과 전달
- [ ] 추가 인원 B에게 End-to-End용 입출력 규격 전달

## 최종 산출물

```text
image
 -> cells_original.json
 -> report.json
 -> optional aligned/cells.json
```

## 하지 않을 것

- 새 Cell Detector 추가
- 새로운 병합 알고리즘 대규모 수정
- OCR 정확도 연구
- Anchor 규칙 개발

## 완료 기준

10장 입력 각각에 대해 자동 구조 복원 결과가 생성되고, 다른 담당자가 좌표계 혼동 없이 바로 사용할 수 있어야 한다.
