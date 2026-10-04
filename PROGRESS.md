# tail 작업 진행 기록

> 배정: [plan.md](plan.md) · 결과·요청사항 전체: [README.md](README.md) · 상세 이력: git `492916d` 이전 PROGRESS.md
> 규칙: tail 밖 폴더는 읽기만 한다.

## 현재 상태 (2026-10-05)

- ✅ 조기 체크, 데이터 10장, 정답(텍스트·ROI), 실험 A·B, 평가, 사례, 입출력 규격, requirements
- ✅ H1 1차 분석 (인쇄 글자 비교 + 원본/전처리 비교), 사진 GPS 제거, 결과 json에 실행 환경 기록
- 🔶 실험 C: sample.jpg 1장으로 파이프라인만 연결. 10장은 팀원 ROI 대기
- H5 결과: Full OCR **29/49**, GT ROI OCR **31/49** (CER 0.141 → 0.117)
- H1 결과: 품질이 좋은 7장은 인쇄 한글 재현율 0.97~0.99. 떨어진 3장은 거리(#10), 접힘(#7), 가장자리(#4)로 설명됨. **원근 보정만으로 손글씨 Field Accuracy도 31/49** (ROI 재인식과 같음) → ROI 이득의 일부는 해상도 효과일 수 있음

## 남은 작업

- [ ] 팀원 요청 전달 (README 5절: bang_·taegu·dahye·heewon·추가 인원 B, 기한 10-05~07)
- [ ] 실험 C 10장: `convert_teammate.py` → `roi_ocr.py --pad 0` → `evaluate_fields.py --detected`
- [ ] 이전 커밋에 남은 GPS 원본 사진 처리 결정 (히스토리 재작성은 팀 합의 필요, README 2-6절)
- [ ] 촬영 조건 매핑 확인 (`sample_5/6`, `sample_8/9`) → H1 표에 계획 조건 열 추가
- [ ] (선택) ROI 후처리, 잔금·계약기간 필드

## 타임라인

- **09-23** Full OCR baseline + 조기 체크 완료
- **10-02** 데이터 3장, 실험 A
- **10-03** 10장 완료, 정답 구축, 실험 B, 평가, README·규격 문서, 팀원 결과 확인, 여유 비율 민감도(영향 없음), 실험 C 연결
- **10-04** 팀 담당 정리 (taegu ≠ 추가 인원 B, 공통 evaluator = dahye), requirements.txt
- **10-05** issue 문서 대조 → GPS 제거, 실행 환경 기록, H1 분석 (`scripts/h1_quality.py`, `results/h1/`)

## 기억할 것

- **OOM**: 기본 서버 모델은 54GB까지 올라감 → `PP-OCRv5_mobile_det` + `korean_PP-OCRv5_mobile_rec` + `limit_side_len=1536` 고정. 모델명을 지정하면 `lang`이 무시되므로 rec 모델도 한국어로 같이 지정할 것
- **1536 제한의 부작용**: 검출은 사진 긴 변을 1536px로 줄여서 보므로, 문서가 작게 찍히면(#10) 글자가 너무 작아진다. 문서만 잘라 원근 보정하면 회복됨
- **사진 추가 시**: 커밋 전에 `exiftool -gps:all= -overwrite_original <파일>`. EXIF 전체 삭제는 금지(회전 정보가 사라져 좌표가 틀어짐)
- **파일 ≠ 세트 번호**: `sample_5`=#6, `sample_6`=#5, `sample_8`=#9, `sample_9`=#8 (정답은 이미지 내용 기준)
- **#7**: 계약금 미기입(평가 제외). 인쇄 글자와 표 선이 어긋나 있어 정답 ROI 상단 4칸은 직접 지정
- **정답 메모**: 필체가 모호하면(`권4연`) 의도한 값을 정답으로 함. taegu sample.jpg 정답 `401` → 이미지는 `401호` (tail 변환본만 수정)
