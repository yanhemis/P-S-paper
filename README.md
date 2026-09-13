# TestReult.py

임대차계약서 이미지에서 표의 선을 검출해 셀 격자를 만들고, 끊어진 경계를 이용해
병합된 셀(merged cell)까지 복원하는 OpenCV 기반 프로토타입입니다.

## 처리 흐름
1. 기울기 보정 + 전처리(CLAHE, 이진화)
2. 수평/수직 표선 검출 및 끊긴 선 보정
3. 셀 경계(상하좌우) 존재 여부 판정 → Union-Find로 병합 셀 재구성
4. 결과를 `cells.json`으로 저장하고 3단계 시각화 이미지 출력

## 실행
```bash
python TestReult.py
```
`sample.jpg`를 입력으로 받아 `cells.json`을 생성합니다.

## 출력
각 셀은 `general`(일반) 또는 `merged`(병합) 타입으로 구분되어 bbox와 함께 저장됩니다.