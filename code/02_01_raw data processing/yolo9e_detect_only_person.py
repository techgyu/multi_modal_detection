from ultralytics import YOLO
import glob
import os

folder_name = '20251029_Takistan_1400_Taleban_2'  # 예: folder_name = 'sample1' (visual, thermal, ir의 상위 폴더)
base_dir = os.path.join('data', folder_name)
visual_dir = os.path.join(base_dir, 'visual')
thermal_dir = os.path.join(base_dir, 'thermal')
nvg_dir = os.path.join(base_dir, 'nvg')
output_dir = os.path.join('output', folder_name)

# 1. 사전학습된 YOLOv9e 모델 로드
model = YOLO('model/yolov9e.pt')  # yolov9e.pt 파일이 없으면 자동 다운로드
model.to('cuda')  # 명시적으로 GPU 사용

# 2. visual 폴더 내 모든 이미지 탐지
image_paths = glob.glob(os.path.join(visual_dir, '*.*'))
image_paths = [p for p in image_paths if p.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'))]

for img_path in image_paths:
    print(f'Processing: {img_path}')
    results = model(img_path)
    for r in (results if isinstance(results, list) else [results]):
        # person(class 0)만 남기고 나머지 박스는 무시
        person_indices = (r.boxes.cls == 0).cpu().numpy()
        
        # person만 필터링된 boxes 추출
        person_boxes = r.boxes[person_indices]
        
        import shutil
        
        # base_name 추출 (visual: 000001_v.png -> base: 000001)
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        if base_name.endswith('_v'):
            base_name = base_name[:-2]
        ext = os.path.splitext(img_path)[1]  # .png
        
        # thermal, nvg 경로
        thermal_path = os.path.join(thermal_dir, f'{base_name}_th{ext}')
        nvg_path = os.path.join(nvg_dir, f'{base_name}_nv{ext}')
        
        # output 폴더 구조: output/folder_name/visual, thermal, nvg
        out_visual_dir = os.path.join(output_dir, 'visual')
        out_thermal_dir = os.path.join(output_dir, 'thermal')
        out_nvg_dir = os.path.join(output_dir, 'nvg')
        
        os.makedirs(out_visual_dir, exist_ok=True)
        os.makedirs(out_thermal_dir, exist_ok=True)
        
        out_visual_path = os.path.join(out_visual_dir, os.path.basename(img_path))
        out_thermal_path = os.path.join(out_thermal_dir, f'{base_name}_th{ext}')
        out_nvg_path = os.path.join(out_nvg_dir, f'{base_name}_nv{ext}')
        
        if len(person_boxes) > 0:
            # visual, thermal, nvg 각각의 폴더로 복사
            shutil.copy(img_path, out_visual_path)
            
            if os.path.exists(thermal_path):
                shutil.copy(thermal_path, out_thermal_path)
                
            if os.path.exists(nvg_dir) and os.path.exists(nvg_path):
                os.makedirs(out_nvg_dir, exist_ok=True)
                shutil.copy(nvg_path, out_nvg_path)
            
            # YOLO 라벨 저장 (output_dir 바로 아래 labels 폴더에)
            label_dir = os.path.join(output_dir, 'labels')
            os.makedirs(label_dir, exist_ok=True)
            label_path = os.path.join(label_dir, os.path.splitext(os.path.basename(img_path))[0] + '.txt')
            with open(label_path, 'w') as f:
                for box in person_boxes:
                    # xyxy to YOLO xywh (normalized)
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    img_w = r.orig_shape[1]
                    img_h = r.orig_shape[0]
                    x_center = ((x1 + x2) / 2) / img_w
                    y_center = ((y1 + y2) / 2) / img_h
                    w = (x2 - x1) / img_w
                    h = (y2 - y1) / img_h
                    f.write(f"0 {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}\n")
            # 탐지된 객체 정보 출력 (person만)
            for box in person_boxes:
                print(box.xyxy, box.conf, box.cls)
        else:
            # person이 하나도 없으면 output과 원본 모두 삭제
            # output 삭제
            if os.path.exists(out_visual_path):
                os.remove(out_visual_path)
            if os.path.exists(out_thermal_path):
                os.remove(out_thermal_path)
            if os.path.exists(out_nvg_path):
                os.remove(out_nvg_path)
            
            # 원본 삭제
            if os.path.exists(img_path):
                os.remove(img_path)
                print(f'No person detected. Deleted: {img_path}')
                
            if os.path.exists(thermal_path):
                os.remove(thermal_path)
                print(f'No person detected. Deleted: {thermal_path}')
            
            # nvg 폴더가 존재하는 경우에만 삭제 시도 (야간 데이터)
            if os.path.exists(nvg_dir) and os.path.exists(nvg_path):
                os.remove(nvg_path)     
                print(f'No person detected. Deleted: {nvg_path}')