from ultralytics import YOLO
import glob
import os

folder_name = '폴더명을_여기에_입력하세요'  # 예: folder_name = 'sample1'
data_dir = os.path.join('data', folder_name)
output_dir = os.path.join('output', folder_name)

# 1. 사전학습된 YOLOv9e 모델 로드
model = YOLO('model/yolov9e.pt')  # yolov9e.pt 파일이 없으면 자동 다운로드

# 2. data/폴더명 내 모든 이미지 탐지
image_paths = glob.glob(os.path.join(data_dir, '*.*'))
image_paths = [p for p in image_paths if p.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'))]

for img_path in image_paths:
    print(f'Processing: {img_path}')
    results = model(img_path)
    # 결과 시각화
    for r in (results if isinstance(results, list) else [results]):
        r.show()
        # output/폴더명/이미지이름 폴더에 저장
        out_dir = os.path.join(output_dir, os.path.splitext(os.path.basename(img_path))[0])
        os.makedirs(out_dir, exist_ok=True)
        r.save(out_dir)
        # 탐지된 객체 정보 출력
        for box in r.boxes:
            print(box.xyxy, box.conf, box.cls)