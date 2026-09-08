# 연구 방향성 · 가설 · 다음 작업 통합 문서

> 마지막 업데이트: 2026-09-08

## 이 문서의 역할

이 파일은 팀 전체가 공통으로 참고하는 **연구 방향, 현재 가설, 실험 우선순위, 공통 평가 기준, 다음 작업 모음**이다.

담당자 개인에 대한 피드백은 이 문서에 적지 않는다. 담당자별 피드백은 별도 `feedback_*.md` 파일에서 관리한다.

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

특히 임대차계약서는 표와 병합 셀이 많고, `보증금`, `계약금`, `임대인`, `임차인`, `소재지`, `계약기간` 등 핵심 필드의 위치 관계가 비교적 정형적이다.

따라서 전체 표를 완벽하게 복원하는 것 자체보다 **핵심 필드 ROI를 얼마나 안정적으로 특정하고, 그 결과가 최종 Field Accuracy 개선으로 이어지는지**를 중심으로 본다.

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
- 잘못 분할된 병합 셀과 누락된 셀 사례 기록

### H4. 표선 기반 ROI 검출은 정형 계약서에서 핵심 필드 영역을 안정적으로 특정할 수 있다

검증:
- OpenCV ROI와 PP-Structure/TATR ROI 비교
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

## 4. 우선 비교할 파이프라인

| 구분 | 방법 | 주요 확인 대상 |
|---|---|---|
| A | PaddleOCR 단독 | Text bbox baseline |
| B | PP-StructureV3 + Korean OCR | 최신 Paddle 구조/셀 좌표 |
| C | TATR + Korean OCR | row/column/span 기반 cell reconstruction |
| D | OpenCV + Korean OCR | 표선 기반 Cell/ROI Detection |
| E | Anchor-ROI + Korean OCR | 전체 표 복원 없는 핵심 필드 추출 |

추가 후보는 1차 실험 후 필요할 때만 확장한다.

- Surya OCR/Table
- Docling TableFormer

---

## 5. 공통 실험 데이터 및 Ground Truth

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

우선 필드:
- 소재지
- 보증금
- 계약금
- 잔금
- 계약기간
- 임대인 성명
- 임차인 성명

---

## 6. 다음 작업 모음

### Priority 1 — 좌표 반환 여부와 baseline 확정

- [ ] PaddleOCR text bbox 저장/시각화
- [ ] PP-StructureV3 `cell_box_list` 등 셀 좌표 재확인
- [ ] TATR row/column/spanning-cell 결과에서 cell bbox 재구성
- [ ] OpenCV 현재 프로토타입의 실제 cell bbox 출력 점검

### Priority 2 — 병합 셀 및 구조 평가

- [ ] 일반 셀 / 병합 셀 성능 분리
- [ ] Cell IoU / Precision / Recall 계산
- [ ] Cell-Text Mapping 정확도 측정
- [ ] 대표 실패 사례 이미지 저장

### Priority 3 — ROI OCR 효과 검증

- [ ] 전체 이미지 OCR 결과 확보
- [ ] 동일 필드에 대해 ROI crop 후 OCR 재실행
- [ ] CER / Exact Match / confidence 비교
- [ ] Field Accuracy 전후 비교

### Priority 4 — Anchor-ROI PoC

- [ ] `보증금`
- [ ] `계약금`
- [ ] `임대인`
- [ ] `임차인`
- [ ] `소재지`

라벨 탐색 성공률, ROI 포함률, Field Exact Match를 기록한다.

---

## 7. 공통 평가 기준

### 좌표
- IoU
- Precision
- Recall
- F1

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

## 8. 결과 저장 형식

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

## 9. 1차 완료 기준

다음 조건을 만족하면 예비 실험 1차 완료로 본다.

- [ ] 동일 계약서 최소 10장 사용
- [ ] PaddleOCR / PP-StructureV3 / TATR / OpenCV 결과 확보
- [ ] 모든 방법의 대표 bbox 시각화 확보
- [ ] 일반 셀 / 병합 셀 평가 분리
- [ ] 핵심 필드 5개 이상 Exact Match 평가
- [ ] ROI 재인식 전/후 정확도 비교
- [ ] 대표 실패 사례 3종 이상 정리

---

## 10. 현재 현황

### 완료/진행된 내용

- [x] 범용 Table Structure 모델 예비 조사
- [x] OpenCV line/cell detection 1차 프로토타입 구현
- [x] 연구 가설 H1~H6 초안 정리
- [x] 공통 비교 파이프라인 후보 선정

### 아직 필요한 내용

- [ ] Ground Truth 구축
- [ ] 최신 PP-StructureV3 재실험
- [ ] TATR 실제 cell reconstruction 평가
- [ ] OpenCV 병합 셀 bbox 재구성
- [ ] 동일 데이터셋 정량 비교
- [ ] ROI OCR 전후 Field Accuracy 비교

---

## 중심 연구 질문

> **한국어 정형 표 문서에서 Text Bounding Box와 Cell Bounding Box는 각각 어느 단계에서 불안정해지며, 공간 구조를 활용한 ROI 재인식이 핵심 필드 추출 정확도를 실제로 향상시키는가?**
