from ultralytics import YOLO
import glob
import os

folder_name = 'visual_5'  # 예: folder_name = 'sample1'
data_dir = os.path.join('data', folder_name)
output_dir = os.path.join('output', folder_name)

# 1. 사전학습된 YOLOv9e 모델 로드
model = YOLO('model/yolov9e.pt')  # yolov9e.pt 파일이 없으면 자동 다운로드
model.to('cuda')  # 명시적으로 GPU 사용

# 2. data/폴더명 내 모든 이미지 탐지
image_paths = glob.glob(os.path.join(data_dir, '*.*'))
image_paths = [p for p in image_paths if p.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'))]

for img_path in image_paths:
    print(f'Processing: {img_path}')
    results = model(img_path)
    for r in (results if isinstance(results, list) else [results]):
        # output/폴더명/에 이미지 이름으로 저장 (탐지 결과가 그려진 이미지)
        os.makedirs(output_dir, exist_ok=True)
        out_img_path = os.path.join(output_dir, os.path.basename(img_path))
        r.save(filename=out_img_path, line_width=1)
        # 탐지된 객체 정보 출력
        for box in r.boxes:
            print(box.xyxy, box.conf, box.cls)