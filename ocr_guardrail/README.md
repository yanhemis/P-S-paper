# OCR Guardrail

OCR로 추출된 계약서 정보의 신뢰성을 검증하기 위한  
경량 규칙 기반 Guardrail 모듈입니다.

## 1. 개발 목적

OCR은 문서의 텍스트를 자동으로 추출할 수 있지만,  
숫자, 날짜, 금액 등의 정보를 잘못 인식할 가능성이 있습니다.

특히 임대차계약서의 보증금이나 월세와 같은 중요 정보에서  
OCR 오류가 발생하면 구조화된 데이터의 신뢰성이 크게 저하될 수 있습니다.

본 모듈은 OCR 결과를 그대로 사용하는 대신,  
**OCR Confidence, 필드의 중요도, 형식 유효성**을 이용하여  
추가 검증이 필요한 결과를 탐지하는 것을 목적으로 합니다.

---

## 2. 동작 구조

```text
OCR Result
    ↓
Field Risk Classification
    ↓
Confidence Validation
    ↓
Format Validation
    ↓
Guardrail Decision
    ↓
PASS / RECHECK / BLOCK
```

---

## 3. 주요 기능

### 3.1 필드 위험도 분류

각 필드의 중요도에 따라 `LOW`, `MEDIUM`, `HIGH`로 분류합니다.

- `name` → LOW
- `address` → MEDIUM
- `contract_date` → MEDIUM
- `deposit` → HIGH
- `monthly_rent` → HIGH

정의되지 않은 필드는 기본적으로 `MEDIUM` 위험도로 처리합니다.

### 3.2 동적 Confidence Threshold

모든 OCR 결과에 동일한 기준을 적용하지 않고,  
필드 위험도에 따라 서로 다른 OCR Confidence 기준을 적용합니다.

| Risk | Threshold |
|---|---:|
| LOW | 0.70 |
| MEDIUM | 0.80 |
| HIGH | 0.90 |

따라서 동일한 Confidence를 가진 OCR 결과라도  
필드의 중요도에 따라 다른 검증 결과가 발생할 수 있습니다.

예를 들어 Confidence가 `0.85`인 경우,  
일반적인 이름 정보는 통과할 수 있지만 보증금과 같은  
HIGH 위험도 필드는 재검증 대상으로 분류될 수 있습니다.

### 3.3 Format Validation

OCR Confidence뿐만 아니라 추출된 텍스트의 형식도 검사합니다.

현재 다음 필드에 대한 기본적인 형식 검증을 지원합니다.

#### 금액 필드

`deposit`, `monthly_rent`

- 숫자 형식 검사
- 쉼표(`,`) 및 `원` 표현 허용
- OCR 과정에서 숫자와 혼동될 가능성이 있는 문자 탐지
  - `O`, `o`
  - `I`, `l`

예:

```text
50,000,000원  → Valid
5O,OOO,OOO원  → Invalid
```

#### 날짜 필드

`contract_date`

다음과 같은 날짜 형식을 지원합니다.

```text
2026-10-06
2026.10.06
2026/10/06
```

### 3.4 결과 상태

Guardrail의 최종 결과는 세 가지 상태로 구분됩니다.

- `PASS`: 현재 OCR 결과 사용 가능
- `RECHECK`: OCR 결과의 재검증 필요
- `BLOCK`: 신뢰하기 어려운 결과로 사용 차단

현재 다음과 같은 경우 `RECHECK` 대상으로 판단합니다.

- OCR Confidence가 해당 필드의 Threshold보다 낮은 경우
- 필드의 형식 검증에 실패한 경우

다음과 같은 경우 `BLOCK` 처리합니다.

- OCR Confidence가 `0.50` 미만인 경우
- OCR 결과가 빈 문자열인 경우

---

## 4. 파일 구조

```text
ocr_guardrail/
├── __init__.py
├── rules.py
├── guardrail.py
├── test_guardrail.py
└── README.md
```

- `rules.py`: 필드 위험도 및 Confidence 기준 정의
- `guardrail.py`: OCR 결과의 형식 검증 및 상태 판정
- `test_guardrail.py`: Guardrail 테스트
- `__init__.py`: Python package 설정
- `README.md`: OCR Guardrail 설명 문서

---

## 5. 실행 방법

프로젝트 루트 디렉터리에서 다음 명령을 실행합니다.

```bash
python -m ocr_guardrail.test_guardrail
```

---

## 6. 테스트 예시

### 정상적인 보증금 OCR 결과

```text
Field      : deposit
Text       : 50,000,000원
Confidence : 0.96
Risk       : HIGH
Threshold  : 0.9
Format     : True
Status     : PASS
Reasons    : []
```

### OCR 오인식이 포함된 보증금

숫자 `0`이 영문자 `O`로 잘못 인식된 경우입니다.

```text
Field      : deposit
Text       : 5O,OOO,OOO원
Confidence : 0.76
Risk       : HIGH
Threshold  : 0.9
Format     : False
Status     : RECHECK
Reasons    : ['Low OCR confidence (0.76 < 0.90)', 'Invalid field format']
```

### 신뢰도가 매우 낮고 값이 없는 경우

```text
Field      : monthly_rent
Text       :
Confidence : 0.32
Risk       : HIGH
Threshold  : 0.9
Format     : False
Status     : BLOCK
Reasons    : ['Low OCR confidence (0.32 < 0.90)', 'Invalid field format']
```

---

## 7. 향후 확장

현재 버전은 규칙 기반의 경량 OCR Guardrail입니다.

향후 다음 기능으로 확장할 수 있습니다.

- 실제 OCR 엔진과 직접 연동
- 계약서 필드 간 일관성 검사
- 금액 한글/숫자 교차 검증
- `RECHECK` 발생 시 재-OCR 자동 수행
- 정적/동적 Guardrail 성능 비교