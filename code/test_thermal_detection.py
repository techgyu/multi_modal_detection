from ultralytics import YOLO
import cv2
import glob
import os
import numpy as np

# 테스트할 thermal 이미지 폴더 경로
thermal_dir = r"data\20251029_Takistan_1400_Taleban_1\thermal"

if not os.path.exists(thermal_dir):
    print(f"❌ 경로를 찾을 수 없습니다: {thermal_dir}")
    exit()

# 출력 폴더
output_dir = 'test_thermal_detection'
os.makedirs(output_dir, exist_ok=True)

# YOLO 모델 로드
print("YOLO 모델 로드 중...")
model = YOLO('model/yolov9e.pt')
model.to('cuda')

# Thermal 이미지 파일 목록
image_paths = glob.glob(os.path.join(thermal_dir, '*.*'))
image_paths = [p for p in image_paths if p.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'))]
image_paths.sort()

print(f"총 {len(image_paths)}개의 thermal 이미지 탐지 중...\n")

# 시각화된 이미지들을 저장할 리스트
viz_images = []

for idx, img_path in enumerate(image_paths):
    print(f"[{idx+1}/{len(image_paths)}] Processing: {os.path.basename(img_path)}")
    
    # 이미지 읽기
    img = cv2.imread(img_path)
    if img is None:
        print(f"  ⚠️ 이미지를 읽을 수 없습니다: {img_path}")
        continue
    
    # YOLO 탐지
    results = model(img_path)
    
    # 결과 처리
    for r in (results if isinstance(results, list) else [results]):
        # person(class 0)만 필터링
        person_indices = (r.boxes.cls == 0).cpu().numpy()
        person_boxes = r.boxes[person_indices]
        
        # 탐지된 person 수
        num_persons = len(person_boxes)
        
        # 박스 그리기
        for box in person_boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            conf = box.conf[0].cpu().numpy()
            
            # 바운딩 박스
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # 신뢰도 표시
            label = f'person {conf:.2f}'
            cv2.putText(img, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # 상단에 통계 표시
        stats_text = f'Detected: {num_persons} persons | Image: {idx+1}/{len(image_paths)}'
        cv2.putText(img, stats_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        print(f"  ✅ {num_persons}명 탐지됨")
    
    # 시각화 이미지 저장
    viz_images.append(img.copy())
    
    # 개별 이미지도 저장
    output_path = os.path.join(output_dir, f'{idx:04d}_{os.path.basename(img_path)}')
    cv2.imwrite(output_path, img)

print(f"\n✅ 탐지 완료! 총 {len(viz_images)}장 처리됨")

# 동영상 생성
if len(viz_images) > 0:
    print("\n동영상 생성 중...")
    
    # 첫 번째 이미지 크기 기준
    height, width = viz_images[0].shape[:2]
    
    # 동영상 설정 (0.3초 = 약 3.33 fps)
    fps = 1 / 0.3  # 3.33 fps
    video_path = os.path.join(output_dir, 'thermal_detection_result.mp4')
    
    # VideoWriter 설정
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
    
    for img in viz_images:
        video_writer.write(img)
    
    video_writer.release()
    print(f"✅ 동영상 저장 완료: {video_path}")
    print(f"   - 프레임 수: {len(viz_images)}장")
    print(f"   - FPS: {fps:.2f}")
    print(f"   - 재생 시간: {len(viz_images) * 0.3:.1f}초")
else:
    print("❌ 처리된 이미지가 없어 동영상을 생성할 수 없습니다.")

print(f"\n📁 결과 폴더: {output_dir}/")
