# P-S-paper

# 📄 부동산 임대차계약서 표 구조(Table Structure) 정밀 추출 모델 비교 분석 보고서

본 프로젝트는 딥러닝 기반의 문서 레이아웃 분석 및 표 구조 인식 모델 4종을 테스트하여, **한국어 임대차계약서 이미지 내의 복잡한 표(병합 셀 포함) 구조와 셀 단위 Bounding Box 좌표를 정밀하게 추출할 수 있는지 검증**한 결과입니다.

---

## 💻 1. 실행 환경 (Environment)
* **OS:** Windows 11 (Local PC)
* **Language:** Python 3.11 (venv 권장)
* **Hardware:** AMD Ryzen 5 5600X / 16GB RAM (GPU 비활성화, 순수 CPU 추론 연산)
* **Core Libraries:** `paddlepaddle==2.6.2`, `paddleocr==2.8.1`, `transformers`, `torch`, `opencv-python`

---

## 2. 라이브러리 및 모델 비교표 (필수 확인 사항 종합)

| 모델 | 실행 성공 | Text bbox | Cell bbox | 병합 셀 | 한국어 OCR | 한계/제외 사유 |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **PaddleOCR** | O | O | - | - | O | 구조 정보 없음 |
| **PP-StructureV3** | 확인 | O | 확인 | 확인 | O | 최신 버전 재검증 |
| **TATR** | O | OCR 별도 | 재구성 | 검증 필요 | 별도 OCR | 복잡 구조 평가 필요 |
| **LayoutParser** | 환경 의존 | 평가 불가 | 평가 불가 | 평가 불가 | - | 환경 문제 |

---

## 3. 폴더별 테스트 상세 내역 및 검출 결과
​각 폴더별로 독립적인 테스트 코드가 구성되어 있습니다. 각 폴더로 이동하여 python test.py를 실행하면 결과를 확인할 수 있습니다.

​### 1_PP-Structure (PaddleOCR 내장 레이아웃 엔진)
​간단한 테스트 방법: 폴더 내 test.py 실행
​검출 결과: 현재 테스트한 특정 버전에서 실행 제한
​사유 및 추후 과제: 테스트에 사용된 해당 PP-Structure 버전에서는 lang='korean' 설정 시 런타임 에러가 발생하여 평가하지 못했습니다. (Paddle 계열 전체의 미지원이 아니며, 추후 최신 버전인 PP-StructureV3와 Korean OCR 조합으로 재검증이 필요합니다.)

### ​2_TATR (Microsoft Table Transformer)
​간단한 테스트 방법: pip install transformers timm 후 test.py 실행
​검출 결과: tatr_result.jpg (행/열/병합 셀 등 구조 검출 확인)
​한계점 및 추후 과제: 모델 자체는 row / column / spanning-cell 등의 구조 결과를 반환하나, 본 임대차계약서 실험에서는 이 구조 결과로부터 목표 병합 셀(cell bbox)을 안정적으로 재구성하지 못하였습니다. 향후 재구성된 cell bbox가 Ground Truth와 얼마나 일치하는지 정량적 검증이 필요하며, 텍스트 인식을 위한 별도의 OCR 결합이 요구됩니다.

### ​3_LayoutParser (Detectron2 기반 레이아웃 분할)
​간단한 테스트 방법: pip install layoutparser 후 test.py 실행
​검출 결과: 현재 환경 의존성 문제로 평가 불가
​사유: 핵심 백본인 Detectron2가 Windows/CPU 환경에서 C++ 컴파일러 및 PyTorch 의존성 충돌을 일으켜 실행되지 않았습니다. 이는 모델의 성능이 낮은 것이 아니라, 현재 로컬 환경적 요인으로 인해 본 예비 실험 단계에서 평가를 진행하지 못한 것입니다.

### ​4_SLANet (PaddleOCR 표 구조 특화 모델)
​간단한 테스트 방법: pip install premailer openpyxl 후 test.py 실행
​검출 결과: 174개 Bbox 검출 후 엑셀 변환 (결과물: output_table/contract_table_result.xlsx)
​한계점: Text Detection 모듈을 강제로 영어(lang='en')로 구동 시, 텍스트 정보의 부재가 Table Structure 인식 과정에 영향을 미쳐 엑셀 병합(Colspan) 등 목표하는 셀 구조가 온전히 재구성되지 않는 현상을 확인했습니다. Text 인식과 Table Structure 구조 인식을 분리하여 해석할 필요가 있습니다.

### 4. 예비 조사 결론 및 향후 연구 방향
​본 브랜치의 실험은 최종 성능 비교라기보다는 후속 정량 비교를 위한 모델 후보 선별용 예비 탐색 목적으로 진행되었습니다.
​범용 딥러닝 구조 모델 4종을 검토한 결과, 현재의 실행 환경(Windows/CPU) 및 라이브러리 버전 제약 등으로 인해 즉각적인 적용보다는 셀 좌표 재구성 및 파인튜닝 등 추가적인 검증 단계가 필요함을 확인했습니다.
​이에 대한 다음 보완 작업으로, 예비 조사에서 적용 가능성을 확인한 'OpenCV 기반 ROI 접근법'을 후속 정량 비교 대상으로 선정합니다.
​다음 단계에서는 특정 모델의 지원 여부를 단정하기보다, 동일한 임대차계약서 샘플(Ground Truth)을 기준으로 TATR 등에서 재구성한 Cell Bbox 결과와 OpenCV 기반 물리적 셀 분할 결과를 비교하여 IoU, Precision, Recall 등의 정량 지표를 통해 성능을 평가하는 방향으로 발전시킬 예정입니다.
