# 연구 방향성 · 가설 · 다음 작업 통합 문서

> 마지막 업데이트: 2026-09-14

## 이 문서의 역할

이 파일은 팀 전체가 공통으로 참고하는 **연구 방향, 현재 가설, 실험 우선순위, 공통 평가 기준, 다음 작업 모음, 전체 진행 현황**을 한 곳에서 관리한다.

담당자 개인에 대한 피드백은 이 문서에 적지 않는다. 담당자별 피드백은 `feedback_*.md`, 추가 인원에게 배정한 작업은 `assignment_*.md`에서 관리한다.

새 기능이나 새로운 모델을 추가하기 전에는 `00_scope_guard_prompt.md`로 현재 논문 범위에 해당하는지 먼저 확인한다.

---

## 1. 현재 연구 방향

현재 연구의 핵심은 단순한 한국어 OCR 인식률 비교가 아니라 다음 흐름을 단계별로 검증하는 것이다.

```text
문서 이미지
  -> 전처리
  -> Text Detection
  -> Cell / ROI Detection
  -> 구조 또는 필드 매핑
  -> ROI 재인식
  -> 필드별 후처리
  -> 핵심 정보 추출 정확도 평가
```

임대차계약서는 표와 병합 셀이 많고, `보증금`, `계약금`, `임대인`, `임차인`, `소재지`, `계약기간` 등 핵심 필드의 위치 관계가 비교적 정형적이다.

따라서 전체 표를 완벽하게 복원하는 것 자체보다 **핵심 필드 ROI를 얼마나 안정적으로 특정하고, 그 결과가 최종 Field Accuracy 개선으로 이어지는지**를 중심으로 본다.

현재는 다음 세 층을 분리해서 평가한다.

1. **Text Detection**: OCR이 텍스트 위치를 안정적으로 잡는가?
2. **Structure / ROI Detection**: 텍스트가 어느 셀·필드에 속하는지 공간 구조를 안정적으로 복원하는가?
3. **Field Extraction**: 최종적으로 보증금·주소·성명 등 핵심 값을 정확히 추출하는가?

---

## 2. 현재까지 정리된 핵심 해석

### 2.1 `한국어라서 좌표가 붕괴한다`고 단정하지 않는다

OCR Text Detection과 한국어 Recognition, Table Structure Recognition을 분리해서 본다.

- Text bbox는 한국어 자체보다 저해상도, 기울기, 블러, 표선 겹침, 원근 왜곡 등의 영향을 더 크게 받을 수 있다.
- 텍스트가 검출되어도 읽기 순서와 행/열/병합 셀 복원 과정에서 구조가 무너질 수 있다.
- 핵심 문제는 `텍스트 bbox 검출 실패`와 `셀-텍스트 매핑 실패` 중 어느 쪽인지 실험으로 분리한다.

### 2.2 범용 구조 모델 실패와 실행 환경 실패를 구분한다

- 실행이 되지 않았으면 `성능이 낮다`가 아니라 `현재 환경에서 평가하지 못함`으로 기록한다.
- 특정 버전에서 한국어 설정이 제한되었다고 해서 모델 계열 전체가 한국어를 지원하지 않는다고 일반화하지 않는다.

### 2.3 OpenCV를 미리 최적이라고 결론 내리지 않는다

OpenCV 기반 line/cell detection은 현재 **유망한 비교 대상 또는 proposed 후보**이다.

최종 결론은 동일 Ground Truth에서 구조 모델과 정량 비교한 뒤 결정한다.

### 2.4 단순 검출 개수는 성능 지표가 아니다

모델이 반환한 bbox 개수만으로 성능을 판단하지 않는다.

가능하면 **exhaustive Ground Truth + 1:1 matching 기반 IoU / Precision / Recall / F1**로 비교하고, 마지막에는 Field Accuracy까지 확인한다.

일부 셀만 라벨링한 partial GT를 사용할 경우, 라벨링되지 않은 정상 예측까지 FP로 처리될 수 있으므로 global Precision/FP를 논문 성능 근거로 사용하지 않는다.

---

## 3. 현재 연구 범위 결정

### 본 논문에서 유지할 비교축

- PaddleOCR 기반 전체 이미지 OCR baseline
- PP-Structure 계열의 구조/셀 좌표
- TATR row/column/spanning-cell 기반 cell reconstruction
- OpenCV 표선/grid/contour 기반 Cell/ROI Detection
- OpenCV 병합 셀 reconstruction
- ROI crop 후 OCR 재인식
- Anchor-ROI 기반 Field Mapping
- 공통 Ground Truth 기반 좌표/OCR/Field Accuracy 평가

### 현재 본 논문에서 제외하고 후속 연구로 미룬 항목

**셀 자체를 객체로 학습하는 이미지 딥러닝 방법은 현재 논문 범위에서 구현하지 않는다.**

예:
- YOLO / DETR / Faster R-CNN 기반 Cell Object Detection
- Mask R-CNN 등 Instance Segmentation 기반 셀 분할
- 별도 셀 검출 모델 파인튜닝
- 이를 위한 대규모 Cell Detection 학습 데이터셋 구축

이 방법들은 현재 연구와 관련은 있으나 새로운 학습 데이터, 모델 선정, 학습/검증 실험축을 추가해야 하므로 연구 범위가 크게 확장된다.

따라서 현재 OpenCV/구조 모델/Anchor-ROI 비교가 완료된 뒤에도 **Cell/ROI Detection 자체가 최종 Field Accuracy의 주요 병목으로 남는 경우** 후속 연구에서 검토한다.

---

## 4. 현재 연구 가설

### H1. Text bbox는 한국어 자체보다 이미지 품질의 영향을 더 크게 받는다

검증:
- PaddleOCR 전체 이미지 실행
- 원본 / 전처리 이미지 비교
- Text bbox 검출 성공률, OCR CER, confidence 비교

### H2. 주요 오류는 Text Detection보다 Table Structure / Cell-Text Mapping에서 증가한다

검증:
- Text bbox와 Cell bbox를 별도로 시각화
- 각 텍스트가 정답 셀에 포함되는지 평가
- 읽기 순서 및 필드 매핑 오류 유형 기록

### H3. 병합 셀은 범용 Table Structure Recognition의 주요 실패 지점이다

검증:
- 일반 셀과 병합 셀 Ground Truth를 구분
- Cell IoU / Precision / Recall / F1을 각각 측정
- TATR spanning-cell 반영 결과와 단순 row×column 교차 결과 비교
- 잘못 분할된 병합 셀과 누락된 셀 사례 기록

### H4. 표선 기반 ROI 검출은 정형 계약서에서 핵심 필드 영역을 안정적으로 특정할 수 있다

검증:
- OpenCV ROI와 PP-Structure/TATR ROI 비교
- Morphological Grid / Contour 기반 방법을 동일 GT에서 비교
- 핵심 필드 ROI IoU 및 검출 성공률 비교
- 끊어진 선, 흐린 선, 짧은 내부 경계, 기울기 실패 조건 분석

### H5. ROI 재인식은 전체 이미지 OCR 후 좌표 매핑보다 최종 필드 정확도를 높일 수 있다

비교:

```text
Baseline
전체 OCR -> text bbox -> 필드 매핑 -> 핵심 필드 추출

ROI 방식
Cell/Anchor 검출 -> ROI crop -> ROI OCR -> 필드 후처리 -> 핵심 필드 추출
```

평가:
- Field Exact Match
- Field Accuracy
- CER
- confidence
- sec/image

### H6. 전체 표 복원보다 Anchor-ROI 방식이 더 효율적일 수 있다

예:

```text
"보증금" 라벨 검출
  -> 라벨 bbox 기준 상대 위치 탐색
  -> 값 ROI 생성
  -> ROI OCR
  -> 금액 형식 후처리
```

전체 표 복원이 불안정한 경우 핵심 라벨의 위치 관계만 사용하는 방식도 별도 비교한다.

---

## 5. 2026-09-14 최신 진행 상황

### 5.1 `dahye_cell_DetectionSurvey`

이전 피드백 중 주요 항목이 반영되었다.

완료/개선:
- IoU threshold를 `0.3 / 0.5 / 0.7`로 명시
- GT-Pred 1:1 Greedy Matching 구현
- TP / FP / FN 기반 Precision / Recall / F1 계산 구현
- GT를 general 5개 + merged 5개까지 확대
- TATR에서 `table spanning cell`을 읽어 실제 cell reconstruction에 반영
- TATR prediction을 `tatr_result.json`으로 저장
- PP-Structure 2.8.1과 PP-StructureV3 명칭 분리

남은 핵심 문제:
- 현재 GT가 페이지 전체 셀이 아니라 일부 선택 셀만 라벨된 상태라면, 나머지 정상 예측이 모두 FP로 계산될 수 있음
- 따라서 현재 README의 대량 FP/Precision 수치는 exhaustive GT가 확보되기 전 논문 성능 결과로 확정하지 않음
- `evaluate.py`의 중복 `__main__` 실행 블록 정리 필요
- prediction에도 general/merged 타입을 명시하면 클래스별 평가가 더 명확해짐

### 5.2 `bang_`

이전의 `병합 후보 탐지` 단계에서 **실제 병합 셀 구조 복원 구현 단계**로 발전했다.

추가 구현:
- HoughLinesP 기반 deskew
- 해상도 비례 parameter scaling
- 수평/수직 closing 길이 분리
- shared boundary 판정
- Union-Find 기반 primitive cell 병합
- general / merged bbox 생성
- `primitive_cells` 정보 저장
- 표준 `cells.json` 출력 코드
- 3단계 시각화 코드

현재 확인할 점:
- 실제 실행부의 line extraction 기본값은 여전히 `h_ratio=0.4`, `v_ratio=0.4`이므로 짧은 내부 경계선 누락 가능성 검증 필요
- boundary 누락이 곧 union으로 이어지기 때문에 선 검출 실패가 오병합으로 연결되는지 확인 필요
- L자 형태 등 비직사각형 primitive component가 생길 경우 bbox가 불필요한 영역까지 포함할 수 있으므로 rectangularity 검증 권장
- 현재 브랜치에는 코드가 추가됐지만 실제 생성된 `cells.json`과 최종 시각화 결과를 공통 결과물로 남기는 단계가 필요

### 5.3 `heewon`

현재 역할은 그대로 유지한다.

- Morphological Opening 기반 검출
- Contour 기반 검출
- kernel/filter sensitivity
- 동일 Ground Truth에서 두 방식 비교

`bang_`은 최종 구조 복원, `heewon`은 입력 검출 방식 비교로 역할을 구분한다.

### 5.4 연구 단계

```text
1단계: 방법 가능성 조사
  ↓
2단계: Cell/ROI 검출 프로토타입 구현
  ↓
3단계: 평가 체계의 신뢰성 확보  ← 현재 최우선
  ↓
4단계: 구조 모델 vs OpenCV 정량 비교
  ↓
5단계: ROI OCR 효과 검증
  ↓
6단계: Anchor-ROI와 최종 Field Accuracy 비교
```

---

## 6. 우선 비교할 파이프라인

| 구분 | 방법 | 주요 확인 대상 |
|---|---|---|
| A | PaddleOCR 단독 | Text bbox / OCR baseline |
| B | PP-Structure 계열 | 구조/셀 좌표 및 병합 셀 |
| C | TATR + Korean OCR | row/column/span 기반 cell reconstruction |
| D1 | OpenCV Morphological Grid | 표선 기반 Cell/ROI Detection |
| D2 | OpenCV Contour | contour 기반 Cell/ROI Detection |
| D3 | OpenCV Grid + Merged Reconstruction | 병합 전/후 구조 복원 효과 |
| E | Anchor-ROI + Korean OCR | 전체 표 복원 없는 핵심 필드 추출 |

현재 본 논문에서는 위 파이프라인을 우선하며, 새로운 Cell Detection 딥러닝 모델은 추가하지 않는다.

---

## 7. 공통 실험 데이터 및 Ground Truth

### 데이터

- [ ] 동일 기준의 임대차계약서 이미지 10~20장 선정
- [ ] 개인정보 포함 여부 및 비식별화 확인
- [ ] 해상도, 기울기, 블러, 촬영/스캔 방식 기록
- [ ] 대표 bbox 시각화 문서 1~3장 고정

**주의:** 10~20장의 실험 이미지를 확보하는 것과 `서로 다른 계약서 양식 10종`을 확보하는 것은 다르다.

현재 연구는 정형 문서의 공간 구조 활용 가능성을 검증하는 것이므로, 우선 동일 또는 유사한 정형 양식 안에서 이미지 품질과 내용이 다른 샘플을 확보한다. 서로 크게 다른 양식으로 일반화하는 실험은 1차 결과 이후 별도 범위로 판단한다.

### Ground Truth

최소 다음 항목을 준비한다.

- [ ] 핵심 필드 라벨 bbox
- [ ] 핵심 필드 값 bbox
- [ ] 일반 셀 bbox
- [ ] 병합 셀 bbox
- [ ] 필드별 정답 텍스트
- [ ] GT 중복 좌표 검수

Cell Detection의 Precision / Recall / F1을 계산할 대표 페이지는 **페이지 내 평가 대상 셀을 모두 라벨링하는 exhaustive GT**를 우선 구축한다.

우선 필드:
- 소재지
- 보증금
- 계약금
- 잔금
- 계약기간
- 임대인 성명
- 임차인 성명

---

## 8. 다음 작업 모음

### Priority 0 — 평가 신뢰성 확보

- [x] IoU threshold 실제값과 출력 문구 일치
- [x] GT-Pred 1:1 matching 구현
- [x] Precision / Recall / F1 계산 구현
- [ ] 대표 페이지 exhaustive GT 구축
- [ ] partial GT와 exhaustive GT 평가를 구분
- [ ] GT 라벨 검수
- [ ] evaluator 중복 실행 블록 정리
- [ ] prediction type(general/merged) 표현 방식 통일

### Priority 1 — 구조 모델 / OpenCV 동일 기준 비교

- [x] PP-Structure 2.x / PP-StructureV3 명칭 분리
- [x] TATR spanning-cell 기반 reconstruction 1차 구현
- [x] `bang_` Union-Find 기반 merged reconstruction 1차 구현
- [ ] `bang_` 실제 `cells.json` / 시각화 결과 저장
- [ ] `bang_` rectangularity / 오병합 검증
- [ ] Morphological Grid 결과를 공통 evaluator에 연결
- [ ] Contour 결과를 공통 evaluator에 연결
- [ ] PP-Structure / TATR / OpenCV를 동일 exhaustive GT에서 비교

### Priority 2 — OCR / ROI 재인식 효과 검증

- [ ] PaddleOCR 전체 페이지 baseline
- [ ] GT ROI에서 OCR 수행하여 이상적 ROI 상한선 측정
- [ ] 실제 검출 ROI에서 OCR 수행
- [ ] CER / Exact Match / confidence 비교
- [ ] Field Accuracy 비교

### Priority 3 — Anchor-ROI PoC

- [ ] `보증금`
- [ ] `계약금`
- [ ] `임대인`
- [ ] `임차인`
- [ ] `소재지`
- [ ] 라벨 탐색 성공률
- [ ] ROI 포함률
- [ ] Field Exact Match
- [ ] Cell 기반 방식과 처리 시간/정확도 비교

---

## 9. 현재 역할 분담

| 역할 | 담당 범위 | 겹치지 않도록 제외할 범위 |
|---|---|---|
| `dahye_cell_DetectionSurvey` | 구조 모델 조사, TATR/PP-Structure, 공통 evaluator | OpenCV 알고리즘 개발 자체 |
| `bang_` | OpenCV grid, shared boundary, 병합 셀 bbox 재구성, `cells.json` | 구조 모델 조사, OCR 성능 비교, 딥러닝 Cell Detector 학습 |
| `heewon` | Morphology vs Contour 방식 비교 및 파라미터 실험 | 병합 셀 최종 재구성 로직, OCR 후처리 |
| 추가 인원 A | 전체 OCR vs ROI OCR, CER/Exact Match/Field Accuracy | Cell Detection 알고리즘 개발 |
| 추가 인원 B | Anchor-ROI 및 label-to-value Field Mapping | 구조 모델/셀 검출 모델 비교 |

추가 인원 A/B의 상세 체크리스트는 별도 `assignment_*.md`에서 관리한다.

---

## 10. 공통 평가 기준

### 좌표
- IoU
- Precision
- Recall
- F1
- GT-Pred 1:1 matching 여부 명시
- partial / exhaustive GT 여부 명시

### OCR
- CER
- Exact Match
- confidence

### 필드 추출
- Field Accuracy
- 필드별 성공/실패 건수

### 실행 성능
- sec/image
- CPU/GPU 여부
- 메모리 사용량(가능한 경우)

---

## 11. 결과 저장 형식

가능하면 방법별로 동일한 구조를 사용한다.

```text
results/
  sample_01/
    original.jpg
    text_bbox.jpg
    primitive_grid.jpg
    boundary.jpg
    cell_bbox.jpg
    roi.jpg
    ocr.json
    cells.json
    metrics.json
```

모델별 결과는 최소한 다음 정보를 남긴다.

- 사용 모델/버전
- 실행 환경
- text bbox
- cell bbox
- general / merged type(가능한 경우)
- OCR text/confidence
- runtime
- 핵심 필드 prediction / ground truth / correct 여부

---

## 12. 현재 현황

### 완료/진행된 내용

- [x] 범용 Table Structure 모델 예비 조사
- [x] OpenCV line/cell detection 1차 프로토타입 구현
- [x] Morphological / Contour 기반 OpenCV 비교 실험 시작
- [x] GT 라벨링 도구 구현
- [x] 1:1 Greedy Matching 기반 evaluator 1차 구현
- [x] TATR spanning-cell 기반 reconstruction 1차 구현
- [x] `bang_` Union-Find 기반 merged reconstruction 1차 구현
- [x] 연구 가설 H1~H6 정리
- [x] 추가 인원 2명 역할 분리
- [x] 이미지 딥러닝 Cell Detection을 Future Work로 범위 고정

### 가장 먼저 필요한 내용

- [ ] 대표 페이지 exhaustive GT 구축
- [ ] 현재 partial GT 기반 FP/Precision 해석 수정
- [ ] `bang_` 실제 결과 파일 생성 및 공통 evaluator 연결
- [ ] OpenCV 0.4 line kernel의 짧은 경계 누락 여부 검증
- [ ] Union-Find component rectangularity 검증
- [ ] 동일 데이터셋에서 구조 모델 / OpenCV 정량 비교

### 이후 핵심 단계

- [ ] 전체 OCR vs ROI OCR Field Accuracy 비교
- [ ] Anchor-ROI PoC
- [ ] 대표 실패 사례 유형화

---

## 13. Future Work 후보

현재 논문의 결론을 낸 뒤 다음 연구로 확장할 수 있다.

- Object Detection 기반 Cell Detector 학습
- Instance Segmentation 기반 셀 단위 분할
- 다양한 계약서 양식 간 일반화 성능 평가
- 더 다양한 정형 행정/금융 문서로의 적용 가능성 검토

이 항목들은 현재 논문의 필수 구현 범위가 아니다.

---

## 중심 연구 질문

> **한국어 정형 표 문서에서 Text Bounding Box와 Cell Bounding Box는 각각 어느 단계에서 불안정해지며, 공간 구조를 활용한 ROI 재인식 또는 Anchor-ROI 방식이 핵심 필드 추출 정확도를 실제로 향상시키는가?**
