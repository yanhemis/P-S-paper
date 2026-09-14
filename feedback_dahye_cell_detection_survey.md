# 담당자 피드백 — `dahye_cell_DetectionSurvey`

> 마지막 업데이트: 2026-09-14

## 이 문서의 역할

이 파일은 `dahye_cell_DetectionSurvey` 브랜치의 **표 구조 인식 모델 조사, TATR/PP-Structure 실험, Ground Truth, 공통 정량 평가 코드에 대한 피드백만** 기록한다.

OpenCV 구현 세부는 `bang_`/`heewon` 피드백에서 관리하고, 공통 연구 방향과 전체 다음 작업은 `01_research_direction_and_next_steps.md`에서 관리한다.

---

## 1. 현재 작업 상태

이 브랜치는 초기 Survey 단계를 지나 **구조 모델 prediction + Ground Truth + 공통 evaluator를 연결하는 정량 평가 준비 단계**까지 발전했다.

현재 확인된 구현:

- PP-Structure (PaddleOCR 2.8.1) 예비 prediction
- TATR row / column / spanning-cell 검출
- TATR spanning-cell 정보를 반영한 cell bbox reconstruction
- TATR 결과 `tatr_result.json` 저장
- GT 수동 라벨링 도구
- General / Merged GT 구분
- IoU 0.3 / 0.5 / 0.7 민감도 평가
- GT-Pred 1:1 Greedy Matching
- TP / FP / FN 및 Precision / Recall / F1 출력
- PP-Structure 2.x와 PP-StructureV3 명칭 분리

따라서 이전 피드백 중 threshold 불일치, 1:1 matching 부재, TATR spanning-cell 미반영, PP-Structure/V3 명칭 혼용은 **1차적으로 해결된 것으로 본다.**

---

## 2. 잘 반영된 부분

### 2.1 평가 코드 개선

기존 `iou_threshold=0.01` 문제를 없애고 `0.3 / 0.5 / 0.7` 기준을 명시적으로 비교하도록 변경했다.

또한 예측을 중복 사용하지 않는 1:1 Greedy Matching을 도입하고 TP / FP / FN → Precision / Recall / F1까지 계산하도록 확장했다.

이 방향은 공통 evaluator의 기초로 적절하다.

### 2.2 TATR spanning-cell 반영

현재 TATR 코드는 `table row`, `table column`, `table spanning cell`을 각각 수집하고, spanning 영역과 50% 이상 겹치는 기본 셀을 하나로 묶어 최종 bbox를 생성한다.

즉 이전의 단순 `row × column` regular grid 단계에서 실제 **spanning-cell 기반 reconstruction** 단계로 발전했다.

### 2.3 Ground Truth 개선

GT가 기존 5개에서 General 5개 + Merged 5개, 총 10개로 확대되었고 이전에 보였던 거의 중복된 merged bbox도 정리되었다.

GT 포맷도 `image_id`, `cell_id`, `type`, `bbox`를 포함하고 있어 이후 확장하기 좋은 구조다.

### 2.4 보고서 표현 개선

README에서 다음이 구분되고 있다.

- 실행 환경 실패 vs 모델 성능 실패
- PP-Structure 2.8.1 vs PP-StructureV3
- 좌표 반환 가능 여부 vs Ground Truth와의 정확도
- OpenCV를 미리 최적이라고 결론내리지 않음

이 부분은 유지한다.

---

# 3. 현재 가장 중요한 문제 — Partial GT에서 Global Precision을 계산하면 안 됨

현재 `gt_sample.json`은 전체 페이지의 모든 셀을 라벨링한 것이 아니라 **선택된 10개 셀만 라벨링한 partial Ground Truth**이다.

반면 evaluator는 GT와 매칭되지 않은 모든 prediction을 FP로 계산한다.

예를 들어 문서에 실제 정상 셀이 150개 존재하고 모델이 그중 140개를 정확히 검출했더라도, GT에 10개만 라벨되어 있다면 라벨되지 않은 정상 prediction 대부분이 FP로 처리될 수 있다.

따라서 현재 README에 기록된 다음 유형의 수치는 **논문 성능 결과로 확정하면 안 된다.**

- PP-Structure FP 125개
- TATR FP 156개
- Precision / Recall 0%
- 위 결과를 근거로 한 모델 우열 또는 범용 모델 한계 단정

## 해결 방법

### 권장: Exhaustive GT

대표 페이지에서는 해당 평가 범위의 **모든 실제 셀을 빠짐없이 라벨링**한다.

그 후에만 다음을 계산한다.

- TP
- FP
- FN
- Precision
- Recall
- F1

최소 순서:

1. 대표 문서 1장 전체 셀 GT 완성
2. evaluator 검증
3. 3~5장으로 확대
4. 최종적으로 가능한 범위에서 10장 이상 확보

### Partial GT를 계속 사용할 경우

Partial GT에서는 global Precision / FP를 쓰지 않고 다음 수준만 사용한다.

- GT별 best IoU
- Localization Success Rate
- 선택 GT에 대한 Recall
- General / Merged GT subset별 detection success

즉 **partial GT와 exhaustive GT의 평가 목적을 구분한다.**

---

## 4. General / Merged 평가의 의미를 더 명확히 할 것

현재 prediction JSON은 기본적으로 bbox 리스트이며, 예측 bbox 자체에 `type=general/merged`가 없다.

현재 evaluator는 매칭된 prediction의 유형을 GT 유형으로 간주하고, 미매칭 prediction은 가장 많이 겹치는 GT의 유형에 귀속한다.

따라서 현재 출력되는 `General Precision`, `Merged Precision`은 엄밀하게 말하면 **모델이 General/Merged를 분류한 결과의 Precision이 아니다.**

### 두 가지 평가 방식 중 하나를 명확히 선택

#### A. 구조 위치 정확도만 평가

모델이 cell type을 직접 반환하지 않는 경우:

- 전체 Cell Detection Precision / Recall / F1
- General GT subset Recall / IoU
- Merged GT subset Recall / IoU

처럼 표현한다.

이 경우 `General Precision`, `Merged Precision`이라는 표현은 피한다.

#### B. General / Merged classification까지 평가

prediction 결과를 다음처럼 표준화한다.

```json
{
  "bbox": [x1, y1, x2, y2],
  "type": "general"
}
```

또는

```json
{
  "bbox": [x1, y1, x2, y2],
  "type": "merged"
}
```

TATR의 경우 spanning-cell reconstruction 결과를 `merged`, 나머지를 `general`로 저장할 수 있다.

OpenCV `bang_` 결과도 같은 구조를 사용하므로 이후 동일 evaluator에서 직접 비교할 수 있다.

PP-Structure처럼 명시적 type이 없는 방법은 구조 localization과 type classification을 분리해서 평가한다.

---

## 5. `evaluate.py` 중복 실행 블록 정리

현재 `evaluate.py`에는 `if __name__ == "__main__":` 블록이 두 번 존재한다.

첫 블록에서 PP-Structure를 한 번 평가한 뒤, 두 번째 블록에서 PP-Structure와 TATR를 다시 순회하므로 실행 결과가 중복될 수 있다.

다음 형태로 하나만 남기는 것이 좋다.

```text
GT load
  ↓
models_to_evaluate 정의
  ↓
모델별 prediction loader
  ↓
공통 evaluate_model()
  ↓
metrics 저장
```

가능하면 콘솔 출력만 하지 말고 `metrics.json` 또는 CSV에도 저장한다.

---

## 6. GT 라벨링 도구는 자동 저장까지 연결

현재 `gt_labeling.py`는 라벨링 결과를 터미널에 JSON으로 출력한다.

실험 데이터가 10장 이상으로 늘어나면 복사/붙여넣기 방식은 실수 가능성이 높다.

추가 권장:

- [ ] `q` 종료 시 `{image_id}_gt.json` 자동 저장
- [ ] 기존 GT 파일이 있으면 이어서 수정할 수 있게 load 기능 추가
- [ ] 저장 전 cell 수 / General / Merged 수 출력
- [ ] 이미지별 GT 파일 분리 또는 dataset-level JSON 형식 결정

이 작업은 새로운 연구 기능이 아니라 **Ground Truth 신뢰성을 위한 최소 도구 보완**에 해당한다.

---

## 7. TATR reconstruction에서 다음으로 확인할 것

spanning-cell을 실제 reconstruction에 반영한 것은 완료됐지만, 현재는 기본 셀 면적의 `50%` 이상 겹치면 병합 대상으로 판단하는 heuristic을 사용한다.

다음 사항만 추가 확인한다.

- [ ] overlap threshold 0.5가 결과에 얼마나 민감한지 최소 범위 확인
- [ ] 여러 spanning prediction이 겹칠 경우 처리 순서에 따라 결과가 달라지는지 확인
- [ ] raw spanning bbox와 reconstructed merged bbox를 함께 저장
- [ ] prediction confidence도 가능하면 저장
- [ ] `row×column only` vs `+ spanning reconstruction` ablation 결과 비교

중요한 것은 새로운 TATR 알고리즘을 개발하는 것이 아니라 **spanning 정보를 반영했을 때 H3의 merged-cell 성능이 실제로 개선되는지 검증**하는 것이다.

---

## 8. README 결과 표현 수정

현재 README의 `Precision/Recall 0%`, 대량 FP 수치는 partial GT 상태에서는 해석이 왜곡될 수 있으므로 다음처럼 변경하는 것이 안전하다.

권장 표현:

> 현재 10개 선택 셀을 이용한 예비 localization 테스트에서는 PP-Structure와 TATR 모두 일부 목표 셀과의 좌표 불일치 및 과분할 양상이 관찰되었다. 다만 Ground Truth가 페이지 전체 셀을 포함하지 않는 partial annotation이므로, 현재 FP/Precision 수치는 최종 성능 비교에 사용하지 않는다. Exhaustive Ground Truth 구축 후 동일 evaluator로 재측정한다.

즉, 현재 결과는 **실패 사례 발견 및 evaluator 디버깅 근거**로 사용하고 최종 모델 성능표에는 아직 넣지 않는다.

---

## 9. 이 담당자의 다음 작업 우선순위

### Priority 0 — 평가 신뢰성 확보

- [ ] 대표 문서 1장 exhaustive cell GT 완성
- [ ] partial GT / exhaustive GT 평가 모드 구분
- [ ] `evaluate.py` 중복 main 제거
- [ ] prediction type이 없는 모델의 General/Merged 지표 명칭 수정
- [ ] 현재 README의 FP / Precision / Recall 결과를 예비 결과로 하향 표기

### Priority 1 — 공통 evaluator 완성

- [ ] PP-Structure / TATR / OpenCV prediction을 같은 loader에서 처리
- [ ] 가능한 경우 표준 prediction JSON 사용
- [ ] IoU 0.3 / 0.5 / 0.7 유지
- [ ] 1:1 matching 유지
- [ ] 전체 Cell P/R/F1 + merged GT 성능 분리
- [ ] 결과를 `metrics.json` 또는 CSV로 저장

### Priority 2 — TATR H3 검증

- [ ] `row×column only` 결과 저장
- [ ] `row×column + spanning` 결과 저장
- [ ] 동일 exhaustive GT에서 비교
- [ ] merged cell 성능이 실제 개선되는지 확인

이후 새로운 구조 모델을 계속 추가하기보다, `bang_`/`heewon`의 OpenCV prediction을 받아 같은 evaluator에서 비교하는 단계로 넘어간다.

---

## 10. 완료 조건

다음이 충족되면 `dahye_cell_DetectionSurvey`의 1차 역할을 완료한 것으로 본다.

- [ ] 적어도 대표 페이지 1장은 exhaustive GT
- [ ] partial/exhaustive 평가 구분
- [ ] 공통 evaluator 단일 실행 구조
- [ ] PP-Structure / TATR / OpenCV prediction 입력 가능
- [ ] 전체 Cell IoU / Precision / Recall / F1 출력
- [ ] merged-cell 성능을 별도 확인 가능
- [ ] TATR spanning ablation 완료
- [ ] metrics 파일 저장
- [ ] README에 최종값과 예비값을 구분하여 기록

---

## 한 줄 피드백

> 이전 피드백의 핵심이 상당 부분 잘 반영되었다. 이제 가장 중요한 것은 모델을 더 추가하는 것이 아니라, **partial GT에서 발생하는 FP/Precision 왜곡을 제거하고 exhaustive GT 기반 공통 evaluator를 완성해 PP-Structure / TATR / OpenCV를 같은 기준으로 비교할 수 있게 만드는 것**이다.
