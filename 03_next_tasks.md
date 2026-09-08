# 추가 작업 및 다음 실험 목록

## 목적

다음 작업은 모델을 많이 추가하는 것보다 **같은 한국어 임대차계약서에서 Text bbox, Cell bbox, 병합 셀, 최종 핵심 필드 추출을 동일 기준으로 비교할 수 있는 실험 틀을 만드는 것**에 우선순위를 둔다.

---

## 1. 공통 실험 데이터 준비

### 필수 작업

- [ ] 동일 양식의 임대차계약서 이미지 10~20장 선정
- [ ] 개인정보가 포함된 경우 비식별화/연구용 샘플 여부 확인
- [ ] 해상도, 촬영 방식, 기울기, 블러 등 이미지 특성 기록
- [ ] 대표 문서 1~3장은 bbox 시각화 비교용으로 고정

### Ground Truth 작성

최소한 다음 항목을 직접 표시한다.

- [ ] 핵심 필드 라벨 bbox
- [ ] 핵심 필드 값 bbox
- [ ] 일반 셀 bbox
- [ ] 병합 셀 bbox
- [ ] 최종 정답 텍스트

우선 대상 필드 예시:

- 소재지
- 보증금
- 계약금
- 잔금
- 계약기간
- 임대인 성명
- 임차인 성명

---

## 2. Baseline: PaddleOCR 단독

### 목표

`한국어라서 좌표가 붕괴하는가?`를 먼저 검증한다.

### 작업

- [ ] 전체 이미지 PaddleOCR 실행
- [ ] text bbox, text, confidence 저장
- [ ] 결과 bbox를 원본 이미지에 시각화
- [ ] 전처리 전/후 결과 비교
- [ ] 라벨과 값의 bbox 검출 성공 여부 기록

### 기록할 결과

- Text bbox 검출 성공률
- OCR CER
- 핵심 필드 라벨 검출률
- 처리 시간

---

## 3. PP-StructureV3 + Korean OCR 재실험

### 목표

기존 PaddleOCR 2.x 기반 조사와 최신 구조 파이프라인을 비교한다.

### 작업

- [ ] PP-StructureV3 설치 환경 구성
- [ ] Korean OCR 모델 연결 여부 확인
- [ ] `cell_box_list` 등 구조 결과 저장
- [ ] 일반 셀 / 병합 셀 결과 시각화
- [ ] 기존 PP-Structure 실험과 버전 차이 기록

### 기록할 결과

- 실행 성공 여부
- Text bbox 반환 여부
- Cell bbox 반환 여부
- 병합 셀 복원 성공률
- Field Mapping 정확도
- 처리 시간

---

## 4. TATR cell reconstruction 재검증

### 목표

TATR가 단순 행/열 검출에 그치는지, 후처리를 통해 실제 cell bbox를 어느 수준까지 복원할 수 있는지 확인한다.

### 작업

- [ ] row bbox 저장
- [ ] column bbox 저장
- [ ] spanning-cell 결과 저장
- [ ] 구조 결과에서 cell bbox 재구성
- [ ] 일반 셀과 병합 셀을 분리하여 비교
- [ ] 별도 Korean OCR을 cell 영역에 적용

### 기록할 결과

- Cell bbox IoU
- 일반 셀 Precision / Recall
- 병합 셀 Precision / Recall
- 잘못 분할된 셀 사례
- 누락된 셀 사례

---

## 5. OpenCV + Korean OCR 구현

### 목표

범용 구조 모델과 비교할 물리적 선 기반 ROI baseline/proposed 후보를 만든다.

### 작업

- [ ] grayscale / threshold 전처리
- [ ] horizontal line 검출
- [ ] vertical line 검출
- [ ] line intersection 계산
- [ ] cell contour 또는 ROI 생성
- [ ] 너무 작은/큰 bbox 필터링
- [ ] ROI별 Korean OCR 실행
- [ ] 결과 시각화

### 주의할 실패 사례

- 끊어진 표선
- 희미한 선
- 글자와 표선 접촉
- 기울어진 촬영 이미지
- 병합 셀
- 그림자 / 배경 노이즈

---

## 6. Anchor-ROI 방식 PoC

### 목표

전체 표를 복원하지 않고 핵심 라벨의 위치 관계만으로 필드 값을 추출할 수 있는지 확인한다.

### 1차 대상

- [ ] `보증금`
- [ ] `계약금`
- [ ] `임대인`
- [ ] `임차인`
- [ ] `소재지`

### 처리 흐름

```text
전체 OCR
  -> 핵심 라벨 탐색
  -> 라벨 bbox 기준 상대 ROI 생성
  -> ROI 재인식
  -> 필드 형식 후처리
  -> 정답과 비교
```

### 평가

- 라벨 탐색 성공률
- ROI 포함률
- Field Exact Match
- 전체 표 복원 방식 대비 처리 시간

---

## 7. 공통 평가 코드 작성

모델마다 다른 기준으로 평가하지 않도록 공통 스크립트를 만든다.

### 좌표 평가

- [ ] IoU
- [ ] Precision
- [ ] Recall
- [ ] F1

### OCR 평가

- [ ] CER
- [ ] Exact Match

### 필드 추출 평가

- [ ] Field Accuracy
- [ ] 필드별 성공/실패 건수

### 실행 성능

- [ ] sec/image
- [ ] CPU/GPU 여부
- [ ] 메모리 사용량(가능하면)

---

## 8. 비교 결과 저장 형식 통일

각 방법별 폴더에 최소 다음 결과를 저장한다.

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

공통 JSON 예시:

```json
{
  "model": "model_name",
  "image": "sample_01.jpg",
  "runtime_sec": 0.0,
  "text_boxes": [],
  "cell_boxes": [],
  "fields": {
    "보증금": {
      "prediction": "",
      "ground_truth": "",
      "correct": false
    }
  }
}
```

---

## 9. 1차 실험 우선순위

### Priority 1

- [ ] PaddleOCR text bbox baseline
- [ ] TATR cell reconstruction 확인
- [ ] PP-StructureV3 셀 좌표 확인
- [ ] OpenCV cell/ROI baseline

### Priority 2

- [ ] 동일 문서에서 네 방법 bbox 시각화 비교
- [ ] 일반 셀 / 병합 셀 분리 평가
- [ ] ROI 재인식 전/후 Field Accuracy 비교

### Priority 3

- [ ] Anchor-ROI 방식 구현
- [ ] Surya Table 후보 조사
- [ ] Docling TableFormer 후보 조사

---

## 10. 작업 분담 제안

### Cell Detection Survey 담당

- 최신 PP-StructureV3 조사 및 재실험
- TATR cell reconstruction 재검증
- 기존 README 표현 수정
- 각 모델의 bbox 결과 이미지 저장

### OCR / 전처리 담당

- PaddleOCR text bbox baseline
- 전처리 전/후 OCR 비교
- ROI Crop 후 재인식 실험
- CER 및 confidence 기록

### ROI / OpenCV 담당

- 선 검출 기반 cell/ROI 생성
- 병합 셀 및 실패 사례 처리
- Anchor-ROI PoC

### 공통 작업

- Ground Truth 정의
- 평가 지표 확정
- 공통 결과 JSON 형식 작성
- 최종 Field Accuracy 비교

---

## 11. 1차 완료 기준

다음 조건을 만족하면 예비 실험 1차 완료로 본다.

- [ ] 동일 계약서 최소 10장 사용
- [ ] PaddleOCR / PP-StructureV3 / TATR / OpenCV 결과 확보
- [ ] 모든 방법의 bbox 시각화 확보
- [ ] 일반 셀과 병합 셀 성능 분리
- [ ] 핵심 필드 5개 이상 Exact Match 평가
- [ ] ROI 재인식 전/후 정확도 비교
- [ ] 대표 실패 사례 3종 이상 정리

이 결과를 바탕으로 이후 본 실험의 모델 후보와 최종 가설을 축소한다.
