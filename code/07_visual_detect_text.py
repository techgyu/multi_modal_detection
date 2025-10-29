# YOLOv8(n) 사전학습 모델로 data/dataset/visual 내 이미지 일괄 탐지
# pip install ultralytics 필요

import os
from ultralytics import YOLO

# 1. 모델 로드 (YOLOv11n 사전학습 모델)
model = YOLO('yolo11x.pt')  # 또는 yolov11l.pt

# 2. 이미지 폴더 지정
img_dir = 'data/dataset/visual'
img_list = [os.path.join(img_dir, f) for f in os.listdir(img_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# 3. 결과 저장 폴더 지정 (YOLOv11은 자동으로 runs/detect/predict에 저장)

# 4. 일괄 탐지
results = model.predict(img_list, save=True, save_txt=True, project='runs/detect', name='visual_yolo')

print(f"탐지 완료! 결과는 runs/detect/visual_yolo 폴더에 저장됩니다. 총 {len(img_list)}장 처리.")
