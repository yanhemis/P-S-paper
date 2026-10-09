# P-S-paper

## 부동산 임대차계약서 정보 추출 과정의 단계별 오류 분석 연구

본 연구는 한국어 부동산 임대차계약서의 정보 추출 과정에서 발생하는 오류를 단계별로 구분하고, 각 단계의 오류가 최종 필드 추출 정확도(Field Accuracy)에 미치는 영향을 정량적으로 분석하는 것을 목적으로 한다. 이를 위해 동일한 문서 데이터와 Ground Truth를 기준으로 이미지 품질, 표 구조 복원, 관심 영역(Region of Interest, ROI) 설정 및 문자 인식 단계를 구분하여 평가한다.

본 연구의 주요 기여는 새로운 구조 인식 알고리즘을 제안하는 데 있지 않다. 기존 문서 분석 및 문자 인식 기법을 공통 평가 조건에서 비교하고, 개별 단계의 성능과 후속 단계의 오류 사이의 관계를 분석할 수 있는 실험적 근거를 확보하는 데 있다.

현재 본 저장소에는 기존 구조 인식 모델의 예비 조사 결과와 RQ2 표 구조 복원 평가 결과가 포함되어 있다. RQ2의 정량 결과는 단일 계약서 이미지의 두 표 영역에 한정되며, 일부 OpenCV 예측값의 좌표계 검증이 완료되지 않아 잠정 결과로 보고한다. 전체 처리 단계의 오류가 최종 Field Accuracy에 미치는 영향은 관련 단계의 정량 평가 결과가 확보된 범위에서만 해석한다.

---

## 🛠 공통 Evaluator 실행 방법 (evaluate.py)

구조 인식 모델 및 OpenCV 파이프라인의 성능 평가는 `evaluate.py`를 통해 통합 진행합니다.

1. **실행 명령어:** `cd 5_Evaluation` ->  `python evaluate.py`
2. **평가 모드 설정:** 현재 RQ2 구조 복원 비교에서는 `evaluate.py`의 `EVAL_MODE = "EXHAUSTIVE"`를 사용한다.
   - `"EXHAUSTIVE"`: 상단·하단 두 표의 95개 GT를 기준으로, 지정된 평가 영역에 포함된 예측에 대해 Precision, Recall, F1 및 GT 유형별 Localization Recall을 산출한다.
   - `"PARTIAL"`: 코드에 남아 있는 예비 평가용 모드로, 전체 Precision·F1을 산출하지 않는다. 모드를 변경해도 GT 파일이 자동으로 변경되지는 않는다.
   - **재현 시 주의:** 평가 코드를 실행하면 `metrics_audit_draft.json`이 다시 저장될 수 있으므로, 입력 파일과 평가 설정을 확인하지 않은 상태에서 실행하지 않는다.
3. **입력 데이터 포맷:** 새로운 모델 추가 시, 예측 결과는 아래 표준 JSON 리스트 형태를 권장합니다.
   - `[{"bbox": [x1, y1, x2, y2], "type": "general" | "merged", "score": 0.99}, ...]`

---

  ### 📊 과거 구조 인식 성능 비교 기록 (IoU 0.5 / 95셀 GT · 재검증 전 수치 — 최종 성능 비교에 사용하지 않음)

| 구조 모델 (Model) | Precision | Recall | F1-Score | General Recall | Merged Recall |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 1. PP-Structure (Paddle 2.8.1) | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2. TATR (Grid Only Ablation) | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 3. TATR (+ Spanning Recon) | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 4. OpenCV (Grid Only Ablation) | 11.7% | 28.4% | 16.6% | 48.0% | 6.7% |
| 5. OpenCV (+ Spanning Recon) | 37.2% | 33.7% | 35.4% | 46.0% | 20.0% |

---

### 📊 구조 복원 성능 재평가 — 감사 초안 (RQ2)

본 표는 동일한 `sample.jpg`와 95개 셀 Ground Truth를 기준으로 계산한 **잠정 평가 결과**이다. GT는 계약서 페이지 전체가 아니라 상단 표 32개 셀과 하단 표 63개 셀을 대상으로 구축되었다.

평가에서는 GT 주석 영역에 중심점이 포함된 예측 BBox만 사용하고, IoU 임계값별 1:1 Greedy Matching으로 F1을 산출하였다.

| 평가군 | F1 @ IoU 0.3 | F1 @ IoU 0.5 | F1 @ IoU 0.7 | 검증 상태 |
|---|---:|---:|---:|---|
| PP-Structure | 5.9% | 0.0% | 0.0% | Overlay 확인 |
| TATR Grid Only | 26.0% | 3.0% | 0.0% | 좌표 변환 및 Overlay 확인 |
| TATR + Spanning Reconstruction | 26.0% | 3.0% | 0.0% | 좌표 변환 및 Overlay 확인 |
| OpenCV Primitive Grid | 49.7% | 38.7% | 25.8% | 과거 Affine 적용·정량 재평가 완료 |
| OpenCV + Cell Reconstruction | 88.4% | 77.3% | 65.2% | 과거 Affine 적용·정량 재평가 완료 |

**해석 시 주의사항**
- 위 수치는 단일 이미지의 지정된 두 표 영역에 한정되며, 페이지 전체 또는 전체 데이터셋 성능을 의미하지 않는다.
- PP-Structure와 TATR 결과는 평가 영역 필터링 조건에 종속된다.
- OpenCV의 과거 예측 JSON에는 회전각 `-1.061°`가 기록되어 있으나, 현재 파이프라인에서는 동일한 결과를 재현하지 못했다. 현재 실행은 표선 검출 단계에서 실패했으며, 이는 구조 복원 성능이 0%라는 의미가 아니다.
- OpenCV 좌표 변환의 타당성이 최종 검증되지 않았으므로 **모델 간 최종 순위나 OpenCV의 성능 우위를 확정하지 않는다.**
- General/Merged Localization Recall은 셀 유형 분류 정확도가 아니다.

상세 감사 기록은 `5_Evaluation/coordinate_audit.md`, 입력 파일 해시 기록은 `5_Evaluation/evaluation_input_manifest.txt`, 평가 수치 원본은 `5_Evaluation/metrics_audit_draft.json`을 참고한다.

**상태: 잠정 평가 결과 — 최종 비교표 확정 전 감사 단계**
#### 세부 평가 지표 (IoU 0.5 · 잠정 결과)

| 평가군 | Precision | Recall | F1 | General GT Localization Recall | Merged GT Localization Recall |
|---|---:|---:|---:|---:|---:|
| PP-Structure | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| TATR Grid Only | 2.9% | 3.2% | 3.0% | 4.0% | 2.2% |
| TATR + Spanning Reconstruction | 2.9% | 3.2% | 3.0% | 4.0% | 2.2% |
| OpenCV Primitive Grid | 27.3% | 66.3% | 38.7% | 92.0% | 37.8% |
| OpenCV + Cell Reconstruction | 81.4% | 73.7% | 77.3% | 86.0% | 60.0% |

**지표 해석**
- Precision, Recall, F1은 IoU 0.5에서 예측 BBox와 GT BBox를 1:1 매칭해 산출한 위치 검출 지표이다.
- General GT Localization Recall은 일반 셀 GT 50개 중 위치가 매칭된 비율이다.
- Merged GT Localization Recall은 병합 셀 GT 45개 중 위치가 매칭된 비율이다.
- 두 유형별 Recall은 예측 결과의 `general` / `merged` 유형이 정답인지 평가한 수치가 아니다.
- 모든 수치는 GT로 주석 처리한 두 표 영역을 대상으로 하며, OpenCV 결과는 좌표계 검증 및 재현성 문제가 해결되지 않아 잠정 상태이다.

#### 평가 입력 및 좌표계 검증 현황

본 구조 복원 평가는 동일한 계약서 이미지 `sample.jpg`를 대상으로 수행하였다. 공통 Ground Truth는 EXIF 방향이 반영된 3000×4000 이미지 좌표계를 기준으로 구축되었으며, 상단 표 32개와 하단 표 63개를 포함한다.

| 평가군 | Evaluator 입력 파일 | 좌표계 처리 | 검증 상태 |
|---|---|---|---|
| PP-Structure | `1_PaddleOCR-PP-Structure/output/sample/res_0.txt` | 원본 이미지 좌표계 | Overlay 점검 완료 |
| TATR Grid Only | `2_TATR/tatr_result_grid.json` | 원본 이미지 방향으로 90° 좌표 변환 | 좌표 변환 및 Overlay 점검 완료 |
| TATR + Spanning Reconstruction | `2_TATR/tatr_result_spanning.json` | 원본 이미지 방향으로 90° 좌표 변환 | 좌표 변환 및 Overlay 점검 완료 |
| OpenCV Primitive Grid | `5_Evaluation/cells_primitive_original.json` | 과거 실행 기록의 Affine Matrix 역변환 | 좌표 변환 및 정량 재평가 완료 |
| OpenCV + Cell Reconstruction | `5_Evaluation/cells_original.json` | 과거 실행 기록의 Affine Matrix 역변환 | 좌표 변환, Overlay 점검 및 정량 재평가 완료 |

평가는 공통 GT로 정의한 두 표 영역에 예측 BBox의 중심점이 포함되는 경우를 대상으로 수행하였다. 따라서 보고된 Precision, Recall 및 F1은 페이지 전체에 대한 성능이 아니라 지정된 평가 영역과 필터링 조건에 따른 결과이다.

**OpenCV Prediction 출처 및 좌표 변환 검증**

Git 이력 검토 결과, `f352da0` 커밋에서 원본 OpenCV 구조 복원 예측 파일 `output/sample/cells.json`, 정렬 이미지 `output/sample/sample_aligned.png` 및 실행 보고서 `output/sample/report.json`을 확인하였다. 해당 커밋의 `cells.json`과 현재 평가에 사용한 원본 `5_Evaluation/cells.json`의 Git Blob 해시가 일치하여 파일 동일성을 검증하였다.

과거 실행 보고서에 따르면 원본 이미지 크기는 3000×4000, 정렬 이미지 크기는 3074×4055이며, 기록된 회전각은 -1.061°이다. 또한 캔버스 확장에 따른 이동 보정을 포함한 Affine Matrix가 저장되어 있음을 확인하였다.

기존 좌표 변환에서는 회전각만 이용하여 역변환 행렬을 생성하였으나, 과거 파이프라인은 회전 과정에서 이미지 캔버스를 확장하고 이동 보정을 적용한 것으로 확인되었다. 이에 따라 기존 변환의 한계를 확인하고, 과거 실행 보고서에 기록된 Affine Matrix를 역변환하여 OpenCV 예측 BBox를 공통 GT 좌표계로 복원하였다.

변환 후 OpenCV Restored 86개와 Primitive 231개의 BBox가 원본 이미지 좌표 범위에 포함됨을 확인하였다. OpenCV Restored 결과는 원본 이미지 Overlay를 통해 위치 정합성을 시각적으로 점검하였다. 이후 정식 평가 입력 파일을 이용해 동일한 Evaluator에서 IoU 0.3, 0.5 및 0.7에 대한 정량 평가를 재실행하였으며, 별도 Affine 감사 평가와 동일한 지표가 산출됨을 확인하였다.

**평가 재현성 및 해석 제한**

과거 실행 기록의 Affine Matrix를 이용한 좌표 복원과 정량 재평가는 완료하였으나, 현재 OpenCV 파이프라인에서는 과거 구조 복원 Prediction을 처음부터 동일하게 생성하지 못하였다. 따라서 과거 Prediction의 좌표 변환 및 평가 재현과 현재 파이프라인의 전체 실행 재현성은 구분하여 해석한다.

또한 본 평가 결과는 단일 계약서 이미지의 두 표 영역에 한정된다. 해당 조건에서 관찰된 모델별 지표 차이를 다른 문서나 데이터셋에 대한 일반적인 성능 우위로 확대 해석하지 않는다.

좌표계 감사 기록은 `5_Evaluation/coordinate_audit.md`, 과거 실행 보고서는 `5_Evaluation/opencv_historical_report.json`, Affine 기반 재평가 결과는 `5_Evaluation/metrics_affine_audit.json`을 참고한다. 기존 `evaluation_input_manifest.txt`는 수정 전 입력 파일의 해시 기록을 포함하므로, 최종 파일 해시는 별도로 갱신해야 한다.

#### 논문 Results 초안 — 표 구조 복원 성능 (RQ2)

동일한 부동산 임대차계약서 이미지(`sample.jpg`)와 Ground Truth를 기준으로 PP-Structure, TATR 및 OpenCV 기반 표 구조 복원 결과를 비교하였다. 평가 대상은 상단 표 32개 셀과 하단 표 63개 셀로 구성된 총 95개 Ground Truth 셀이며, IoU 임계값 0.3, 0.5 및 0.7에서 예측 Bounding Box와 정답 간 1:1 Greedy Matching을 수행하였다. Precision, Recall 및 F1은 지정된 두 표 영역에 중심점이 포함된 예측을 대상으로 산출하였다.

IoU 0.3에서 PP-Structure, TATR Grid, TATR Spanning, OpenCV Primitive 및 OpenCV Restored의 F1은 각각 5.9%, 26.0%, 26.0%, 49.7% 및 88.4%로 산출되었다. IoU 0.5에서는 각각 0.0%, 3.0%, 3.0%, 38.7% 및 77.3%였으며, IoU 0.7에서는 각각 0.0%, 0.0%, 0.0%, 25.8% 및 65.2%로 나타났다.

IoU 0.5 기준 OpenCV Primitive의 Precision, Recall 및 F1은 각각 27.3%, 66.3%, 38.7%였으며, OpenCV Restored는 각각 81.4%, 73.7%, 77.3%였다. 같은 임계값에서 OpenCV Primitive의 General GT Localization Recall과 Merged GT Localization Recall은 각각 92.0%(46/50), 37.8%(17/45)였고, OpenCV Restored는 각각 86.0%(43/50), 60.0%(27/45)였다. 이 두 유형별 재현율은 Ground Truth 셀의 위치 매칭 비율로, 예측 셀 유형의 분류 정확도를 의미하지 않는다.

OpenCV 평가에서는 과거 실행 보고서에 기록된 Affine Matrix를 이용하여 정렬 이미지 좌표를 원본 이미지 좌표로 역변환하였다. 변환된 정식 Prediction 파일로 수행한 평가 결과는 별도의 Affine 감사 평가 결과와 일치하였으며, 5개 평가군과 3개 IoU 임계값으로 구성된 15개 평가 조합에서 TP와 FN의 합은 모두 95개였다. 다만 현재 OpenCV 파이프라인의 재실행에서는 표선 검출 단계에서 실패하여 과거 Prediction의 생성 과정을 완전히 재현하지 못하였다.

이상의 정량 결과는 단일 계약서 이미지의 두 표 영역 및 지정된 예측 필터링 조건에서 관찰된 결과이며, 다른 문서나 데이터셋에서의 일반적인 성능을 의미하지 않는다.

#### 논문 Discussion 초안 — 구조 복원 오류 및 평가 한계 (RQ2)

본 실험에서 관찰된 구조 복원 성능은 IoU 임계값에 따라 차이를 보였다. PP-Structure와 TATR는 IoU 0.3에서 일부 셀이 매칭되었으나, IoU 0.5와 0.7에서 F1이 크게 감소하였다. 이는 낮은 IoU 임계값에서 위치 매칭이 성립하더라도, 보다 엄격한 경계 일치 조건에서는 해당 매칭이 유지되지 않을 수 있음을 보여준다. 반면 OpenCV 기반 평가군에서는 상대적으로 높은 임계값에서도 매칭된 셀이 관찰되었다. 다만 이러한 차이가 셀 경계 검출, 병합 영역 재구성 또는 모델별 예측 방식 중 어느 요인에 주로 기인하는지는 현재 실험만으로 구분하기 어렵다.

TATR Grid와 Spanning Reconstruction은 지정된 평가 영역에서 동일한 위치 검출 지표를 보였다. 따라서 본 실험 조건에서는 Spanning Reconstruction 적용에 따른 정량적 개선이 확인되지 않았다. 그러나 이러한 관찰을 근거로 해당 처리 방식이 일반적으로 효과가 없다고 판단할 수는 없다. 구조 복원 효과를 해석할 때에는 원본 예측 결과의 구성과 평가 대상 영역을 함께 고려해야 한다.

OpenCV 기반 평가에서는 Primitive Grid와 Restored Cell 사이에 뚜렷한 정량 지표 차이가 관찰되었다. IoU 0.5에서 Primitive Grid의 Precision, Recall 및 F1은 각각 27.3%, 66.3%, 38.7%였으며, Restored Cell은 각각 81.4%, 73.7%, 77.3%였다. Primitive Grid는 평가 영역에서 231개의 BBox를 예측한 반면, Restored Cell은 86개를 예측하였다. 이러한 결과는 본 이미지의 평가 조건에서 두 출력 방식의 예측 개수 및 위치 매칭 특성이 달랐음을 보여준다. 그러나 이를 병합 셀 재구성 처리만의 독립적인 성능 향상 효과로 확정하기는 어렵다.

OpenCV의 좌표계 검증 과정에서는 과거 실행 기록에 포함된 Affine Matrix를 확인하였고, 해당 행렬을 역변환하여 공통 Ground Truth 좌표계에서 정량 평가를 재실행하였다. 초기 평가에서 사용한 단순 회전각 기반 역변환은 과거 정렬 과정의 캔버스 확장 및 이동 보정을 반영하지 못하였으며, 보정 후 평가 지표가 크게 변경되었다. 이는 구조 복원 성능 비교에서 예측 BBox의 좌표계 정합성이 중요한 평가 전제임을 보여준다. 다만 과거 Prediction을 현재 OpenCV 파이프라인에서 처음부터 동일하게 생성하는 데에는 실패하였다. 따라서 좌표 변환 및 정량 평가의 재현과 전체 구조 복원 파이프라인의 실행 재현성은 구분하여 해석해야 한다.

또한 본 평가의 Ground Truth는 단일 계약서 이미지 내 두 표 영역의 95개 셀로 제한되며, 예측 BBox의 중심점을 기준으로 평가 대상을 선택하였다. 따라서 측정된 Precision, Recall 및 F1은 해당 이미지와 영역 선택 규칙에 조건부로 적용된다. 특히 표 영역을 크게 벗어나거나 영역 경계와 중첩되는 예측의 처리 방식은 평가 결과에 영향을 줄 수 있으므로, 이를 전체 문서 또는 다른 계약서 유형에 대한 일반적 성능으로 확대 해석하지 않는다.

General GT Localization Recall과 Merged GT Localization Recall은 각각의 Ground Truth 부분집합에 속한 셀 중 IoU 기준으로 위치 매칭된 비율이다. 따라서 이 지표를 예측 셀의 유형 분류 정확도나 병합 관계 자체의 정확한 복원율로 해석할 수 없다. 병합 관계의 정확성을 별도로 판단하려면 해당 관계를 직접 평가하는 기준이 추가로 필요하다.

본 연구의 전체 분석 체계에서 표 구조 복원 오류는 후속 ROI 설정 및 문자 인식 단계의 입력에 영향을 줄 수 있는 잠재적 요인이다. 그러나 본 RQ2의 위치 검출 지표만으로 구조 복원 오류가 최종 Field Accuracy에 미친 영향의 크기나 인과관계를 확정할 수는 없다. 해당 관계는 동일한 데이터와 Ground Truth를 기준으로 수행하는 ROI, 문자 인식 및 필드 추출 단계의 평가 결과와 연계하여 분석해야 한다.

따라서 본 실험의 의의는 특정 구조 복원 방식의 일반적인 우수성을 주장하는 데 있지 않으며, 동일한 평가 기준에서 관찰된 구조 복원 결과와 좌표계 처리, 재현성 및 평가 범위의 한계를 구분함으로써 단계별 오류 분석에 필요한 근거를 확보하는 데 있다.

#### RQ2 구조 복원 평가의 최종 감사 판정

동일 계약서 이미지의 두 표 영역에 구축한 95개 셀 Ground Truth를 기준으로, 5개 구조 복원 평가군에 대해 IoU 임계값 0.3, 0.5 및 0.7에서 정량 지표를 산출하였다. 총 15개 평가 조합에서 TP와 FN의 합은 모두 95개로 일치하였으며, TP·FP·FN에 기반한 Precision, Recall 및 F1 계산의 내부 일관성을 확인하였다.

PP-Structure와 TATR의 예측 결과는 공통 GT 좌표계에서 시각적으로 점검하였다. OpenCV의 경우 `f352da0` 커밋에서 과거 정렬 이미지와 예측 파일의 존재를 확인하였으며, 현재 평가에 사용한 원본 `cells.json`과 과거 예측 파일의 Git Blob 해시가 일치함을 검증하였다. 다만 해당 정렬 이미지의 실제 회전 변환 행렬은 확인되지 않았으므로, 기록된 회전각 `-1.061°`를 이용한 역변환이 공통 GT 좌표계와 완전히 정합한다고 단정할 수 없다. 또한 현재 파이프라인의 재실행에서는 과거 예측 결과를 재현하지 못하였다.

이에 따라 본 연구의 구조 복원 정량 결과는 단일 이미지, 지정된 두 표 영역 및 예측 영역 필터링 규칙에 종속된 잠정 평가 결과로 분류한다. 특히 OpenCV의 정량 수치는 좌표계 검증 미완료 상태에서 계산된 값으로, 다른 평가군에 대한 확정적 성능 우위의 근거로 사용하지 않는다.

**최종 판정:** 정량 평가 계산 및 감사 기록 작성 완료. 전체 평가군의 좌표계 검증과 최종 성능 순위 확정은 보류.

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

## 🎯 4. 예비 조사 결과 및 구조 복원 평가와의 연계

본 연구의 예비 조사에서는 PP-Structure, TATR, LayoutParser 및 SLANet을 대상으로 한국어 부동산 임대차계약서의 표 구조 인식 가능성과 실행 환경의 제약을 검토하였다. 검토 과정에서 구조 복원 결과의 좌표 불일치, 병합 셀 처리의 한계 및 일부 모델의 실행 환경 문제가 관찰되었다. 이러한 결과는 개별 모델의 일반적인 성능을 판단하기 위한 근거가 아니라, 후속 정량 평가에서 구분하여 검토해야 할 요인을 확인한 예비 관찰로 해석하였다.

후속 RQ2 평가에서는 동일한 계약서 이미지와 상단·하단 두 표 영역의 95개 Exhaustive Ground Truth를 사용하여 PP-Structure, TATR 및 OpenCV 기반 구조 복원 결과를 비교하였다. IoU 임계값 0.3, 0.5 및 0.7에서 Precision, Recall, F1과 Ground Truth 셀 유형별 Localization Recall을 산출하고, 예측 결과의 좌표 변환 및 평가 영역 설정을 검토하였다.

정량 평가 결과는 본 README의 「구조 복원 성능 재평가 — 감사 초안(RQ2)」에 제시하였다. 평가 지표의 내부 계산 일관성은 확인되었으나, OpenCV의 과거 예측 생성 과정과 좌표 변환의 전제 조건이 독립적으로 검증되지 않아 전체 평가군의 최종 성능 순위는 확정하지 않았다.

이러한 검토는 구조 복원 단계에서 발생하는 위치 검출 오류와 평가 재현성 문제를 구분하기 위한 근거를 제공한다. 다만 구조 복원 결과가 후속 ROI 설정, 문자 인식 및 최종 Field Accuracy에 미치는 영향은 해당 단계의 정량 평가 결과와 연계하여 해석해야 하며, 본 RQ2 결과만으로 그 영향의 크기를 단정하지 않는다.

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
  상단·하단 두 표 영역에 대해 총 95개 셀의 Exhaustive Ground Truth를 구축하고, PP-Structure, TATR 및 OpenCV 기반 구조 복원 결과를 동일한 평가 기준에서 비교하였다. IoU 임계값 0.3, 0.5 및 0.7에 따른 Precision, Recall, F1과 Ground Truth 셀 유형별 Localization Recall을 산출하였으며, 평가군별 입력 파일과 좌표 변환 과정을 기록하였다. 정량 지표의 내부 계산 일관성은 확인되었으나, OpenCV의 과거 예측 생성 과정이 재현되지 않아 좌표계 정합성을 최종 입증하지 못하였다. 따라서 본 평가 결과는 단일 이미지의 지정된 두 표 영역에 대한 조건부 결과로 제시하며, 모델 간 최종 성능 우위는 확정하지 않는다. 세부 수치와 검증 상태는 본 README의 「구조 복원 성능 재평가 — 감사 초안(RQ2)」에 제시하였다.