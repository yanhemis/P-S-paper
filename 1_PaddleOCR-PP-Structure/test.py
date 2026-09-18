import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import cv2
from paddleocr import PPStructure, save_structure_res

# 1. 이미지 불러오기
img_path = '../sample.jpg' if os.path.exists('../sample.jpg') else 'sample.jpg'
img = cv2.imread(img_path)

if img is None:
    print(f"❌ 오류: '{img_path}' 파일을 찾을 수 없습니다.")
    exit()

# 2. 엔진 초기화 (핵심 포인트: lang='en'으로 변경하여 표 구조 분석 성능만 테스트)
print("엔진을 초기화하는 중입니다...")
table_engine = PPStructure(layout=False, lang='en', show_log=True)

# 3. 문서 분석 실행
print("\nPP-Structure (영어 모드) 표 구조 인식 테스트를 시작합니다...")
result = table_engine(img)

# 4. 결과 저장
save_folder = './output'
os.makedirs(save_folder, exist_ok=True)

print("\n결과 데이터를 저장하는 중입니다...")
save_structure_res(result, save_folder, os.path.basename(img_path).split('.')[0])

print(f"\n✅ 분석 완료! '{save_folder}' 폴더의 결과물(이미지)을 확인해주세요.")