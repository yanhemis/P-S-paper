# P-S-paper

# 📄 부동산 임대차계약서 표 구조(Table Structure) 정밀 추출 모델 비교 분석 보고서

본 프로젝트는 딥러닝 기반의 문서 레이아웃 분석 및 표 구조 인식 모델 4종을 테스트하여, **한국어 임대차계약서 이미지 내의 복잡한 표(병합 셀 포함) 구조와 셀 단위 Bounding Box 좌표를 정밀하게 추출할 수 있는지 검증**한 결과입니다.

---

## 🛠 공통 Evaluator 실행 방법 (evaluate.py)

구조 인식 모델 및 OpenCV 파이프라인의 성능 평가는 `evaluate.py`를 통해 통합 진행합니다.

1. **실행 명령어:** `cd 5_Evaluation` ->  `python evaluate.py`
2. **평가 모드 설정:** 코드 내 `EVAL_MODE` 변수를 수정하여 진행
   - `"PARTIAL"`: 일부 셀만 라벨링된 예비 GT용 (전체 Precision/FP 산출 안 함)
   - `"EXHAUSTIVE"`: 페이지 내 모든 셀이 라벨링된 전체 GT용 (전체 P/R/F1 산출)
3. **입력 데이터 포맷:** 새로운 모델 추가 시, 예측 결과는 아래 표준 JSON 리스트 형태를 권장합니다.
   - `[{"bbox": [x1, y1, x2, y2], "type": "general" | "merged", "score": 0.99}, ...]`
---

## 💻 1. 실행 환경 (Environment)
* **OS:** Windows 11 (Local PC)
* **CPU:** AMD Ryzen 5 5600X (GPU 비활성화, 순수 CPU 추론 연산)
* **RAM:** 16GB
* **Language:** Python 3.11 (가상환경 `venv` 권장)
* **Core Libraries (과제별 핵심 종속성):** 
  * **[과제 1: PP-Structure & 과제 4: SLANet]**
    * `paddlepaddle==2.6.2` (CPU 버전)
    * `paddleocr==2.8.1`
    * `openpyxl`, `premailer` (SLANet 엑셀 파일 변환 및 저장용)
  * **[과제 2: TATR (Table Transformer)]**
    * `torch` (PyTorch)
    * `transformers` (Hugging Face)
  * **[과제 3: LayoutParser]**
    * `layoutparser` (단, Windows 환경 내 Detectron2 C++ 빌드 충돌로 실제 추론은 불가했음)
  * **[공통 및 GT 채점용]**
    * `opencv-python` (정답지 좌표 추출 GUI 및 이미지 전처리용)

---

## 📊 2. 라이브러리 및 모델 비교표 (필수 확인 사항 종합)

| 모델 | 실행 성공 | Text bbox | Cell bbox | 병합 셀 | 한국어 OCR | 한계/제외 사유 |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **PaddleOCR** | O | O | - | - | O | 구조 정보 없음 |
| **PP-Structure (PaddleOCR 2.8.1)** | 확인 | O | 확인 | 확인 | O | 본 예비 검증 대상 |
| **PP-StructureV3** | - | - | - | - | - | 향후 별도 환경에서 검증 예정 |
| **TATR** | O | OCR 별도 | 재구성 | 검증 필요 | 별도 OCR | 복잡 구조 평가 필요 |
| **LayoutParser** | 환경 의존 | 평가 불가 | 평가 불가 | 평가 불가 | - | 환경 문제 |

---

## 📂 3. 폴더별 테스트 상세 내역 및 검출 결과

각 폴더별로 독립적인 테스트 코드가 구성되어 있습니다. 각 폴더로 이동하여 `python test.py`를 실행하면 결과를 확인할 수 있습니다.

### 1_PP-Structure (PaddleOCR 2.8.1 내장 레이아웃 엔진)
* **테스트 방법:** 폴더 내 `test.py` 실행 (표 구조 분석 검증을 위해 영어 모드 우회 실행 포함)
* **검출 결과:** 표 구조 분할 시 병합 셀 과분할(Over-segmentation) 현상 발생
* **사유 및 한계 분석:**
  1. **실행 제약과 성능 한계의 분리:** 특정 버전 환경에서 `lang='korean'` 설정 시 레이아웃 모델의 런타임 제약으로 인해 직접적인 한국어 평가가 제한되었습니다. 이는 Paddle 계열 전체의 한국어 지원 여부로 일반화할 수 없으며, 영어 모드(`lang='en'`) 우회 테스트를 통해 표 구조 인식(Table Structure Recognition) 성능을 별도로 검증하였습니다.
  2. **구조 분석 성능:** 우회 테스트 결과, 복잡한 병합 셀(Spanning Cell) 영역에서 셀 좌표가 과도하게 쪼개지는 현상이 확인되었습니다.
  3. **시사점:** Text Detection, Recognition, Table Structure 분석 단계를 분리하여 해석할 필요가 있으며, 향후 정량적 비교 및 파이프라인 설계를 고도화할 예정입니다.

### `2_TATR` (Table Transformer)
* **테스트 방법:** 폴더 내 `test.py` 실행 및 결과 시각화
* **검출 결과:** row, column, spanning-cell 구조 결과로부터 cell bbox 재구성 완료 및 시각화 저장
* **사유 및 한계 분석:**
  1. TATR은 자체적으로 셀 좌표를 반환하는 것이 아니라, 검출된 선(row/column/spanning-cell)의 교차 연산을 통해 cell bbox를 재구성하는 방식을 취합니다.
  2. 본 임대차계약서 실험에서는 추출된 구조 결과로부터 목표 병합 셀을 안정적으로 재구성하는 데 한계가 있었습니다.
  3. **핵심 평가:** 본 과제의 핵심 질문은 "셀 좌표를 반환할 수 있는가"가 아니라, **"재구성된 cell bbox가 Ground Truth와 얼마나 일치하는가(정확도)"**에 있습니다. 예비 조사에서 OpenCV 기반 ROI 접근의 적용 가능성을 확인했으며, 이를 후속 정량 비교 대상으로 선정하여 추가 검증을 진행합니다.

### `3_LayoutParser` (Detectron2 기반 레이아웃 분할)
* **테스트 방법:** `pip install layoutparser` 후 `test.py` 실행
* **검출 결과:** 현재 환경 의존성 문제로 평가 불가
* **사유:** 핵심 백본인 Detectron2가 Windows/CPU 환경에서 C++ 컴파일러 및 PyTorch 의존성 충돌을 일으켜 실행되지 않았습니다. 이는 모델의 성능이 낮은 것이 아니라, 현재 로컬 환경적 요인으로 인해 본 예비 실험 단계에서 평가를 진행하지 못한 것입니다.

### `4_SLANet` (PaddleOCR 표 구조 특화 모델)
* **테스트 방법:** `pip install premailer openpyxl` 후 `test.py` 실행
* **검출 결과:** 174개 Bbox 검출 후 엑셀 변환 (결과물: `output_table/contract_table_result.xlsx`)
* **한계점:** Text Detection 모듈을 강제로 영어(`lang='en'`)로 구동 시, 텍스트 정보의 부재가 Table Structure 인식 과정에 영향을 미쳐 엑셀 병합(Colspan) 등 목표하는 셀 구조가 온전히 재구성되지 않는 현상을 확인했습니다. Text 인식과 Table Structure 구조 인식을 명확히 분리하여 해석할 필요가 있습니다.

---

## 🎯 4. 예비 조사 결론 및 향후 연구 방향

범용 딥러닝 구조 모델 4종을 검토한 결과, 현재의 실행 환경(Windows/CPU) 및 라이브러리 버전 제약 등으로 인해 즉각적인 적용보다는 셀 좌표 재구성 및 파인튜닝 등 추가적인 검증 단계가 필요함을 확인했습니다.

이에 대한 다음 보완 작업으로, **예비 조사에서 적용 가능성을 확인한 'OpenCV 기반 ROI 접근법'을 후속 정량 비교 대상으로 선정**합니다. 

다음 단계에서는 특정 모델의 지원 여부를 단정하기보다, 동일한 임대차계약서 샘플(Ground Truth)을 기준으로 **TATR 등에서 재구성한 Cell Bbox 결과와 OpenCV 기반 물리적 셀 분할 결과를 비교하여 IoU, Precision, Recall 등의 정량 지표를 통해 성능을 평가**하는 방향으로 발전시킬 예정입니다.

---

### 5_Evaluation (정량 평가 시스템 구축 및 예비 검증)
* **목적:** 수동으로 라벨링한 Ground Truth(GT) 좌표와 모델 예측 BBox 간의 일치율을 정량적으로 평가하기 위한 파이프라인 구축.
* **평가 방법 (팀장 피드백 반영):** 
  * 단순 중복 매칭을 방지하기 위해 **1:1 Greedy Matching** 알고리즘을 도입.
  * 셀 속성을 **일반 셀(General)**과 **병합 셀(Merged)**로 분리하여 평가.
  * IoU Threshold(0.3, 0.5, 0.7)별로 **TP, FP, FN**을 산출하고 Precision, Recall, F1-Score를 측정.
* **예비 검증 결과 및 소결:**
  현재 10개 선택 셀(Partial GT)을 이용한 예비 localization 테스트에서는 PP-Structure와 TATR 모두 일부 목표 셀과의 좌표 불일치 및 과분할 양상이 관찰되었습니다. 
  다만, 현재의 Ground Truth가 페이지 전체 셀을 포함하지 않는 부분적 라벨링(Partial Annotation) 상태이므로, 이 단계에서 산출된 미매칭 예측(FP) 및 Precision 수치는 최종 성능 비교의 근거로 사용하지 않습니다. 
  향후 대표 페이지의 모든 셀을 포함하는 Exhaustive Ground Truth를 구축한 후, 공통 evaluator를 통해 동일한 기준으로 재측정 및 추가 검증할 계획입니다.

---

  ### 📊 모델별 구조 인식 성능 비교 (IoU 0.5 / 전체 95셀 기준)

| 구조 모델 (Model) | Precision | Recall | F1-Score | General Recall | Merged Recall |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 1. PP-Structure (Paddle 2.8.1) | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2. TATR (Grid Only Ablation) | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 3. TATR (+ Spanning Recon) | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 4. OpenCV (Rule-based) | - | - | - | - | - |