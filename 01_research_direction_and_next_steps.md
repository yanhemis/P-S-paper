# 연구 방향성 · 가설 · 다음 작업 통합 문서

> 마지막 업데이트: 2026-09-11

## 이 문서의 역할

이 파일은 팀 전체가 공통으로 참고하는 **연구 방향, 현재 가설, 실험 우선순위, 공통 평가 기준, 다음 작업 모음, 전체 진행 현황**을 한 곳에서 관리한다.

담당자 개인에 대한 피드백은 이 문서에 적지 않는다. 담당자별 피드백은 `feedback_*.md`, 추가 인원에게 배정한 작업은 `assignment_*.md`에서 관리한다.

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

현재는 다음 세 층을 분리해서 평가하는 방향으로 정리한다.

1. **Text Detection**: OCR이 텍스트 위치를 안정적으로 잡는가?
2. **Structure / ROI Detection**: 텍스트가 어느 셀·필드에 속하는지 공간 구조를 안정적으로 복원하는가?
3. **Field Extraction**: 최종적으로 보증금·주소·성명 등 핵심 값을 정확히 추출하는가?

---

## 2. 현재까지 정리된 핵심 해석

### 2.1 `한국어라서 좌표가 붕괴한다`고 단정하지 않는다

OCR Text Detection과 한국어 Recognition, Table Structure Recognition을 분리해서 본다.

현재 가정은 다음과 같다.

- Text bbox는 한국어 자체보다 저해상도, 기울기, 블러, 표선 겹침, 원근 왜곡 등의 영향을 더 크게 받을 수 있다.
- 텍스트가 검출되어도 읽기 순서와 행/열/병합 셀 복원 과정에서 구조가 무너질 수 있다.
- 핵심 문제는 `텍스트 bbox 검출 실패`와 `셀-텍스트 매핑 실패` 중 어느 쪽인지 실험으로 분리해야 한다.

### 2.2 범용 구조 모델 실패와 실행 환경 실패를 구분한다

- 실행이 되지 않았으면 `성능이 낮다`가 아니라 `현재 환경에서 평가하지 못함`으로 기록한다.
- 특정 버전에서 한국어 설정이 제한되었다고 해서 모델 계열 전체가 한국어를 지원하지 않는다고 일반화하지 않는다.

### 2.3 OpenCV를 미리 최적이라고 결론 내리지 않는다

OpenCV 기반 line/cell detection은 현재 **유망한 비교 대상 또는 proposed 후보**이다.

최종 결론은 동일한 Ground Truth에서 구조 모델과 정량 비교한 뒤 결정한다.

### 2.4 단순 검출 개수는 성능 지표가 아니다

현재 실험에서 모델·방법에 따라 100개 이상 bbox가 반환되지만, 검출 개수가 많거나 적다는 사실만으로 성능을 판단할 수 없다.

앞으로는 동일 Ground Truth에 대해 가능한 한 **1:1 matching 기반 IoU / Precision / Recall / F1**로 비교하고, 마지막에는 Field Accuracy까지 확인한다.

---

## 3. 현재 연구 가설

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
- Cell IoU, Precision, Recall을 각각 측정
- TATR의 spanning-cell 정보를 실제 reconstruction에 반영한 경우와 단순 row×column 교차 방식 비교
- 잘못 분할된 병합 셀과 누락된 셀 사례 기록

### H4. 표선 기반 ROI 검출은 정형 계약서에서 핵심 필드 영역을 안정적으로 특정할 수 있다

검증:
- OpenCV ROI와 PP-Structure/TATR ROI 비교
- Morphological Grid / Contour 기반 방법을 동일 GT에서 비교
- 핵심 필드 ROI IoU 및 검출 성공률 비교
- 끊어진 선, 흐린 선, 짧은 내부 경계 등 실패 조건 분석

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

## 4. 2026-09-11 추가 실험에서 확인된 내용

### 4.1 `dahye_cell_DetectionSurvey` 진행 상황

자료조사 단계에서 정량 평가 준비 단계로 발전했다.

추가된 내용:
- TATR row/column 기반 cell bbox 재구성 코드
- TATR 결과 시각화 이미지
- GT 수동 라벨링 도구
- 일반 셀 / 병합 셀 분리 평가 코드
- PP-Structure 결과를 이용한 IoU 평가 시도

다만 평가 코드 검증이 먼저 필요하다.

현재 확인된 점:
- 평가 함수 기본 `iou_threshold`가 `0.01`인데 출력 문구는 `0.5`로 되어 있어 실제 평가 기준과 표시가 불일치함
- 현재 평가는 각 GT별 best IoU만 확인하여 false positive가 많은 과분할 모델을 충분히 벌점 주지 못함
- GT 샘플 수가 아직 매우 적고 거의 동일한 좌표가 중복되어 있을 가능성이 있음
- TATR reconstruction 코드가 현재 row×column 교차 중심이며 `spanning-cell`을 실제 병합 셀 재구성에 반영하지 않음
- 저장된 실행 코드는 PaddleOCR 2.8.1의 `PPStructure`인데 README 일부에서 `PP-StructureV3` 결과처럼 표현되어 버전 명칭 정리가 필요함

따라서 **현재 수치는 예비 코드 검증 결과로 보고, 논문 성능 근거로 확정하지 않는다.**

### 4.2 `heewon` OpenCV 비교 실험 진행 상황

새로 다음 실험이 추가되었다.

- Morphological Opening 기반 수평/수직선 및 bbox 검출
- Contour 기반 bbox 검출
- 두 방식의 결과 이미지
- Pipeline / Sequence Diagram

의미 있는 변화:
- Morphology 실제 실행에서 `h_ratio=0.05`, `v_ratio=0.05`를 사용하여 이전 0.4 수준보다 짧은 내부 경계 검출을 시도함

현재 결과에서 확인할 점:
- Morphological Grid 결과에서 검출 셀 148개가 모두 병합 셀 후보로 판정되어 merged 판정 로직 검증이 필요함
- Contour 방식은 동일 샘플에서 263개의 bbox를 반환했으나 실제 정답 셀과의 일치율은 아직 평가되지 않음
- 따라서 `148 vs 263` 같은 bbox 개수 비교가 아니라 동일 GT 기반 정량 비교가 필요함

### 4.3 연구 방향상 의미

현재 연구는 다음 단계로 넘어갔다.

```text
1단계: 방법 가능성 조사
  ↓
2단계: Cell/ROI 검출 프로토타입 구현
  ↓
3단계: 평가 체계의 신뢰성 검증  ← 현재 최우선
  ↓
4단계: 구조 모델 vs OpenCV 정량 비교
  ↓
5단계: ROI OCR 효과 검증
  ↓
6단계: Anchor-ROI와 최종 Field Accuracy 비교
```

---

## 5. 우선 비교할 파이프라인

| 구분 | 방법 | 주요 확인 대상 |
|---|---|---|
| A | PaddleOCR 단독 | Text bbox / OCR baseline |
| B | PP-Structure 계열 | 구조/셀 좌표 및 병합 셀 |
| C | TATR + Korean OCR | row/column/span 기반 cell reconstruction |
| D1 | OpenCV Morphological Grid | 표선 기반 Cell/ROI Detection |
| D2 | OpenCV Contour | contour 기반 Cell/ROI Detection |
| E | Anchor-ROI + Korean OCR | 전체 표 복원 없는 핵심 필드 추출 |

추가 후보는 1차 정량 비교 후 필요할 때만 확장한다.

- Surya OCR/Table
- Docling TableFormer

---

## 6. 공통 실험 데이터 및 Ground Truth

### 데이터

- [ ] 동일 기준의 임대차계약서 이미지 10~20장 선정
- [ ] 개인정보 포함 여부 및 비식별화 확인
- [ ] 해상도, 기울기, 블러, 촬영/스캔 방식 기록
- [ ] 대표 bbox 시각화 문서 1~3장 고정

### Ground Truth

최소 다음 항목을 준비한다.

- [ ] 핵심 필드 라벨 bbox
- [ ] 핵심 필드 값 bbox
- [ ] 일반 셀 bbox
- [ ] 병합 셀 bbox
- [ ] 필드별 정답 텍스트
- [ ] GT 중복 좌표 검수

우선 필드:
- 소재지
- 보증금
- 계약금
- 잔금
- 계약기간
- 임대인 성명
- 임차인 성명

---

## 7. 다음 작업 모음

### Priority 0 — 평가 코드 신뢰성 확보

- [ ] IoU threshold 실제값과 출력 문구 일치
- [ ] GT-Pred 1:1 matching 방식 결정
- [ ] Precision / Recall / F1 계산
- [ ] 과분할 false positive 반영
- [ ] GT 중복 및 라벨 오류 검수
- [ ] 일반/병합 셀을 분리해서 평가

### Priority 1 — 구조 모델 / OpenCV 동일 기준 비교

- [ ] PP-Structure 버전 명칭과 실제 실행 코드 정리
- [ ] 실제 PP-StructureV3 재실험 여부 구분
- [ ] TATR spanning-cell 기반 병합 reconstruction 구현
- [ ] Morphological Grid 결과를 공통 evaluator에 연결
- [ ] Contour 결과를 공통 evaluator에 연결
- [ ] 동일 샘플에서 Cell IoU / Precision / Recall / F1 비교

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

## 8. 현재 역할 분담

기존 작업과 추가 인력의 역할을 겹치지 않게 다음처럼 분리한다.

| 역할 | 담당 범위 | 겹치지 않도록 제외할 범위 |
|---|---|---|
| `dahye_cell_DetectionSurvey` | 구조 모델 조사, TATR/PP-Structure, 공통 evaluator 기초 | OpenCV 알고리즘 개발 자체 |
| `bang_` | OpenCV grid, 경계선, 병합 셀 bbox 재구성 | 구조 모델 조사, OCR 성능 비교 |
| `heewon` | Morphology vs Contour 방식 비교 및 파라미터 실험 | 병합 셀 최종 재구성 로직, OCR 후처리 |
| 추가 인원 A | 전체 OCR vs ROI OCR, CER/Exact Match/Field Accuracy | Cell Detection 알고리즘 개발 |
| 추가 인원 B | Anchor-ROI 및 label-to-value Field Mapping | 구조 모델/셀 검출 모델 비교 |

추가 인원 A/B의 상세 체크리스트는 별도 `assignment_*.md`에서 관리한다.

---

## 9. 공통 평가 기준

### 좌표
- IoU
- Precision
- Recall
- F1
- GT-Pred 1:1 matching 여부 명시

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

## 10. 결과 저장 형식

가능하면 방법별로 동일한 구조를 사용한다.

```text
results/
  sample_01/
    original.jpg
    text_bbox.jpg
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
- OCR text/confidence
- runtime
- 핵심 필드 prediction / ground truth / correct 여부

---

## 11. 현재 현황

### 완료/진행된 내용

- [x] 범용 Table Structure 모델 예비 조사
- [x] OpenCV line/cell detection 1차 프로토타입 구현
- [x] Morphological / Contour 기반 OpenCV 비교 실험 시작
- [x] GT 라벨링 도구 초안 구현
- [x] IoU 평가 코드 초안 구현
- [x] TATR cell bbox 재구성 1차 구현
- [x] 연구 가설 H1~H6 정리
- [x] 추가 인원 2명 역할 분리

### 수정/검증이 필요한 내용

- [ ] evaluator threshold 오류 수정
- [ ] 1:1 matching + Precision/F1 추가
- [ ] GT 샘플 확대 및 중복 검수
- [ ] TATR spanning-cell 반영
- [ ] PP-Structure / PP-StructureV3 실험 명칭 분리
- [ ] OpenCV merged 판정 로직 검증

### 이후 핵심 단계

- [ ] 동일 데이터셋에서 구조 모델 / OpenCV 정량 비교
- [ ] 전체 OCR vs ROI OCR Field Accuracy 비교
- [ ] Anchor-ROI PoC
- [ ] 대표 실패 사례 유형화

---

## 중심 연구 질문

> **한국어 정형 표 문서에서 Text Bounding Box와 Cell Bounding Box는 각각 어느 단계에서 불안정해지며, 공간 구조를 활용한 ROI 재인식 또는 Anchor-ROI 방식이 핵심 필드 추출 정확도를 실제로 향상시키는가?**
