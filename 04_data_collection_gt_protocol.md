# 데이터 수집 · GT 구축 프로토콜

> 적용 시작: 2026-10-21
> 목적: 단순히 사진 수를 늘리는 것이 아니라, 논문 평가에 사용할 수 있는 재현 가능한 Dataset v1.0을 만든다.

## 1. 핵심 원칙

이 프로젝트의 신규 데이터는 다음 조건을 모두 만족해야 한다.

1. **개인정보 안전**: 실제 개인정보가 있는 계약서 원본을 공개 저장소에 올리지 않는다.
2. **원본 보존**: 촬영 후 crop, filter, 밝기 조정, 원근 보정 등을 하지 않는다.
3. **조건 기록**: 모든 이미지는 촬영 조건과 문서 그룹 정보를 가진다.
4. **GT 필수**: 최소 핵심 5필드 text GT가 있어야 평가 데이터로 인정한다.
5. **그룹 단위 분할**: 동일 원본 문서의 반복 촬영은 같은 `document_group_id`로 묶고 development/test를 가르지 않는다.
6. **hold-out 보호**: 최종 test는 모델/규칙 튜닝 전에 분리하고 마지막까지 보지 않는다.

---

## 2. 권장 데이터 규모

현재 공통 10장은 이미 개발과 분석에 사용되었다. 신규로 10~15장을 추가해 총 20~25장 수준을 목표로 한다.

권장 신규 구성:

- 정상/통제 촬영: 5~6장
- 난이도 촬영: 5~8장
- 최소 2~3개의 서로 다른 원본 문서 그룹

예시:

```text
docA: baseline / perspective / distance / lighting
docB: baseline / perspective / fold / crop
docC: baseline / distance / lighting / perspective
```

동일 문서 반복 촬영은 이미지 품질 영향 분석에 유용하지만, 논문에서는 이미지 수와 독립 원본 문서 그룹 수를 구분한다.

---

## 3. 허용 데이터

우선순위:

1. 가상의 이름/주소/금액이 들어간 연구용 임대차계약서
2. 개인정보가 완전히 제거된 샘플 계약서
3. 공개 사용이 명확히 허용된 샘플 문서

금지:

- 실제 주민등록번호, 전화번호, 상세 주소, 서명 등이 포함된 원본 계약서를 그대로 공개 저장소에 업로드
- 임의 모자이크 처리 전 원본을 GitHub history에 먼저 올리는 것

가능하면 처음부터 가상 정보 문서를 사용한다.

---

## 4. 촬영 공통 규칙

모든 촬영에서:

- 스마트폰 기본 카메라 사용 가능
- 문서 전체 또는 의도한 crop 조건이 명확히 보이게 촬영
- 초점이 완전히 나간 사진은 제외 또는 `usable=false`
- 촬영 후 자동 보정 앱 사용 금지
- 메신저로 전송해 강제 압축된 파일보다 원본 파일 우선
- 같은 사진을 resize/compress해서 별도 데이터로 세지 않음

### 파일명

```text
<document_group_id>_<condition>_<index>.jpg
```

예:

```text
docA_baseline_01.jpg
docA_perspective_left_01.jpg
docA_distance_far_01.jpg
docB_fold_01.jpg
```

---

## 5. 촬영 조건 정의

### 5.1 baseline

목적: 정상적인 촬영에서 얻을 수 있는 기준 성능 확인.

조건:
- 정면에 가깝게 촬영
- 문서 전체 포함
- 초점 양호
- 밝기 양호
- 큰 그림자 없음
- 가장자리 잘림 없음

### 5.2 perspective

목적: 원근 왜곡 영향 확인.

조건:
- 좌/우/상단 사선 중 하나
- 사람이 실제 스마트폰으로 비스듬히 찍는 수준
- 지나치게 극단적인 각도는 피함

권장 기록:
```text
perspective_direction = left/right/top
perspective_level = mild/moderate
```

### 5.3 distance

목적: 유효 해상도 감소 영향 확인.

조건:
- 문서 전체가 더 작게 보이도록 촬영
- 사람이 확대하면 내용을 읽을 수 있는 수준 유지

권장 기록:
```text
distance_level = normal/far
```

### 5.4 lighting

목적: 밝기와 그림자 영향 확인.

예:
- 낮은 실내 조도
- 한쪽에서만 빛이 들어오는 상태
- 약한 그림자

금지:
- 강한 반사로 글자가 대부분 사라지는 비현실적 상태

### 5.5 fold_or_crop

목적: 접힘/종이 휨/가장자리 누락 영향 확인.

예:
- 종이가 약하게 휘어진 상태
- 접힌 선이 일부 표 영역을 지나는 상태
- 문서 가장자리 일부가 화면 밖으로 나감

crop은 문서의 대부분이 사라질 정도가 아니라 경미한 누락을 우선한다.

---

## 6. manifest.csv 규격

필수 컬럼:

```text
image_id
document_group_id
filename
condition
perspective_direction
perspective_level
distance_level
lighting
fold
crop
usable
split
notes
```

예:

```csv
image_id,document_group_id,filename,condition,perspective_direction,perspective_level,distance_level,lighting,fold,crop,usable,split,notes
new_001,docA,docA_baseline_01.jpg,baseline,none,none,normal,bright,no,no,yes,development,정상 기준
new_002,docA,docA_perspective_left_01.jpg,perspective,left,mild,normal,bright,no,no,yes,development,좌측 사선
new_003,docC,docC_distance_far_01.jpg,distance,none,none,far,normal,no,no,yes,holdout_test,최종 테스트 그룹
```

`split`은 Dataset Manager만 최종 확정한다.

---

## 7. field_gt.json 규격

최소 핵심 5필드:

- `address`
- `deposit`
- `contract_amount`
- `lessor_name`
- `lessee_name`

권장 구조:

```json
{
  "new_001": {
    "document_group_id": "docA",
    "fields": {
      "address": {
        "raw_text": "경기도 수원시 ...",
        "normalized": "경기도 수원시 ...",
        "bbox": null
      },
      "deposit": {
        "raw_text": "금 오천만원정",
        "normalized": "50000000",
        "bbox": null
      },
      "contract_amount": {
        "raw_text": "금 오백만원정",
        "normalized": "5000000",
        "bbox": null
      },
      "lessor_name": {
        "raw_text": "홍길동",
        "normalized": "홍길동",
        "bbox": null
      },
      "lessee_name": {
        "raw_text": "김철수",
        "normalized": "김철수",
        "bbox": null
      }
    }
  }
}
```

### GT 작성 우선순위

1. text GT 정확성
2. normalized 값 정확성
3. 가능하면 bbox

시간이 부족하면 bbox보다 text GT를 먼저 완성한다.

---

## 8. GT 검수 절차

각 이미지에 대해:

1. 작성자 1명이 GT 초안 작성
2. Dataset Manager가 원본을 다시 보고 2차 검수
3. 애매한 필드는 임의 추정하지 않고 `notes`에 기록
4. 이미지에서 실제로 읽을 수 없는 GT는 `unreadable` 표시
5. 파일명, `image_id`, `document_group_id`가 manifest와 일치하는지 확인

금액은 특히:
- 원문 한글 금액
- 숫자 정규화 값

을 함께 보존한다.

---

## 9. development / holdout_test 분리

### 중요한 규칙

동일한 원본 문서 `docA`를 다음처럼 나누면 안 된다.

```text
X development: docA_baseline
X holdout_test: docA_perspective
```

같은 문서의 내용/레이아웃을 이미 본 상태이기 때문이다.

반드시:

```text
O development: docA 전체, docB 전체
O holdout_test: docC 전체
```

처럼 `document_group_id` 단위로 나눈다.

### 권장 비율

신규 데이터의 약 20~30%, 또는 최소 1개 전체 원본 문서 그룹을 hold-out으로 지정한다.

기존 공통 10장은 이미 반복 실험에 사용되었으므로 hold-out이 아니다.

---

## 10. hold-out 사용 절차

1. development 데이터로 bang/taegu 코드와 규칙을 확정
2. commit SHA 또는 버전을 기록
3. 파라미터/규칙 동결
4. holdout_test를 공개
5. 동일 코드로 한 번 실행
6. dahye가 결과 평가

hold-out 결과를 본 뒤 수정하면:
- 수정 자체는 가능하지만
- 그 결과를 더 이상 untouched final hold-out이라고 부르면 안 됨

---

## 11. 개인정보 / EXIF

스마트폰 사진에는 GPS EXIF가 포함될 수 있다.

공유 전:
- GPS metadata 제거 확인
- 실제 개인정보 포함 여부 확인

단, 연구 평가에 필요한 이미지 자체를 임의로 색칠/필터링하여 품질 조건을 바꾸지 않는다. 개인정보가 필요한 영역과 연구 필드가 충돌한다면 해당 실제 문서를 사용하지 말고 가상 문서로 교체한다.

---

## 12. usable 기준

### usable=true
- 사람이 확대해서 핵심 텍스트를 판독할 수 있음
- 의도한 왜곡/거리/조명 조건이 명확함
- 파일 손상 없음

### usable=false 예
- 심한 흔들림으로 대부분 글자가 식별 불가
- 문서 대부분이 프레임 밖
- 파일이 깨짐
- 개인정보 문제로 사용할 수 없음

`usable=false` 이미지도 삭제하지 말고 실패한 수집 사례로 manifest에 이유를 남길 수 있다. 다만 최종 정량평가 분모에 포함할지는 dahye가 평가 규칙에서 명시한다.

---

## 13. Dataset v1.0 완료 체크리스트

- [ ] 신규 usable 이미지 10~15장 수준 확보
- [ ] 최소 2~3개 `document_group_id`
- [ ] 각 이미지 촬영 조건 기록
- [ ] 핵심 5필드 text GT 완료
- [ ] manifest와 GT의 image_id 일치
- [ ] 개인정보/GPS 확인
- [ ] 중복 이미지 없음
- [ ] development / holdout_test를 그룹 단위로 분리
- [ ] holdout은 bang/taegu 동결 전 미공개
- [ ] Dataset v1.0 버전/파일 목록 기록

이 체크리스트가 모두 충족된 데이터만 최종 논문용 평가 세트로 사용한다.
