import os
import cv2
from paddleocr import PPStructure, save_structure_res

# 기존: table_engine = PPStructure(layout=False, show_log=True, lang='korean')
# 변경: 한국어를 차단하므로, 일단 영어(en)라고 속여서 표 구조(칸)만 분리하도록 강제 실행
table_engine = PPStructure(layout=False, show_log=True, lang='en')

# 2. 이미지 읽기
img_path = 'sample.jpg'
img = cv2.imread(img_path)

# 3. 표 인식 및 구조 분석 실행 (SLANet 구동)
print("표 구조를 분석 중입니다...")
result = table_engine(img)

# 4. 결과 저장 (엑셀 파일 및 영역별 좌표)
save_folder = './output_table'
save_structure_res(result, save_folder, 'contract_table_result')
print("✅ 분석 완료! 왼쪽 파일 목록에서 output_table 폴더를 확인하세요.")