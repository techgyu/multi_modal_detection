import cv2
import os
import glob
from concurrent.futures import ThreadPoolExecutor
import numpy as np

folder_name = '20251029_Takistan_12 00_Taleban'  # output\ 빼고 폴더명만
output_dir = os.path.join('output', folder_name)

# 폴더 경로
visual_dir = os.path.join(output_dir, 'visual')
thermal_dir = os.path.join(output_dir, 'thermal')
nvg_dir = os.path.join(output_dir, 'nvg')
label_dir = os.path.join(output_dir, 'labels')

# 시각화 결과 저장 폴더
viz_dir = os.path.join('output', 'visualization', folder_name)
os.makedirs(os.path.join(viz_dir, 'visual'), exist_ok=True)
os.makedirs(os.path.join(viz_dir, 'thermal'), exist_ok=True)
if os.path.exists(nvg_dir):
    os.makedirs(os.path.join(viz_dir, 'nvg'), exist_ok=True)

def draw_boxes(img, boxes):
    """박스를 그리는 함수 (numpy 배열로 한 번에 처리)"""
    for box in boxes:
        cls, x_center, y_center, width, height = box
        h, w = img.shape[:2]
        
        x_center_px = int(x_center * w)
        y_center_px = int(y_center * h)
        box_w = int(width * w)
        box_h = int(height * h)
        
        x1 = int(x_center_px - box_w / 2)
        y1 = int(y_center_px - box_h / 2)
        x2 = int(x_center_px + box_w / 2)
        y2 = int(y_center_px + box_h / 2)
        
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, 'person', (x1, y1-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return img

def process_single_label(label_path):
    """단일 라벨 파일 처리"""
    label_name = os.path.basename(label_path)
    base_name = os.path.splitext(label_name)[0]  # 예: 000001_v
    
    # base_name에서 숫자만 추출 (000001_v -> 000001)
    if base_name.endswith('_v'):
        base_num = base_name[:-2]
    else:
        base_num = base_name
    
    # 이미지 경로들
    visual_path = os.path.join(visual_dir, f'{base_name}.png')
    thermal_path = os.path.join(thermal_dir, f'{base_num}_th.png')
    nvg_path = os.path.join(nvg_dir, f'{base_num}_nv.png')
    
    # 라벨 읽기 (numpy로 한 번에)
    try:
        boxes = np.loadtxt(label_path, ndmin=2)
    except:
        return 0
    
    count = 0
    
    # Visual 이미지 처리
    if os.path.exists(visual_path):
        img = cv2.imread(visual_path)
        if img is not None:
            img = draw_boxes(img, boxes)
            cv2.imwrite(os.path.join(viz_dir, 'visual', f'{base_name}.png'), img)
            count += 1
    
    # Thermal 이미지 처리
    if os.path.exists(thermal_path):
        img = cv2.imread(thermal_path)
        if img is not None:
            img = draw_boxes(img, boxes)
            cv2.imwrite(os.path.join(viz_dir, 'thermal', f'{base_num}_th.png'), img)
            count += 1
    
    # NVG 이미지 처리 (있을 경우만)
    if os.path.exists(nvg_dir) and os.path.exists(nvg_path):
        img = cv2.imread(nvg_path)
        if img is not None:
            img = draw_boxes(img, boxes)
            cv2.imwrite(os.path.join(viz_dir, 'nvg', f'{base_num}_nv.png'), img)
            count += 1
    
    return count

# 라벨 파일 읽기
label_files = glob.glob(os.path.join(label_dir, '*.txt'))
print(f'총 {len(label_files)}개의 라벨 파일 처리 중...')

# 병렬 처리 (CPU 코어 수만큼 스레드 사용)
with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
    results = list(executor.map(process_single_label, label_files))

print(f'\n시각화 완료! 결과는 output/visualization/{folder_name}/ 폴더에 저장되었습니다.')
visual_count = len(glob.glob(os.path.join(viz_dir, "visual", "*.png")))
thermal_count = len(glob.glob(os.path.join(viz_dir, "thermal", "*.png")))
print(f'Visual: {visual_count}장')
print(f'Thermal: {thermal_count}장')
if os.path.exists(nvg_dir):
    nvg_count = len(glob.glob(os.path.join(viz_dir, "nvg", "*.png")))
    print(f'NVG: {nvg_count}장')
else:
    print('NVG: 없음 (주간 데이터)')

# 동영상 생성
print('\n동영상 생성 중...')

def create_video(image_dir, output_path, fps=1/0.3):
    """이미지들을 동영상으로 변환"""
    image_files = sorted(glob.glob(os.path.join(image_dir, '*.png')))
    
    if len(image_files) == 0:
        return False
    
    # 첫 번째 이미지로 크기 확인
    first_img = cv2.imread(image_files[0])
    if first_img is None:
        return False
    
    height, width = first_img.shape[:2]
    
    # VideoWriter 설정
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for img_path in image_files:
        img = cv2.imread(img_path)
        if img is not None:
            video_writer.write(img)
    
    video_writer.release()
    return True

# Visual 동영상 생성
if visual_count > 0:
    visual_video_path = os.path.join(viz_dir, 'visual_detection.mp4')
    if create_video(os.path.join(viz_dir, 'visual'), visual_video_path):
        print(f'✅ Visual 동영상 생성: {visual_video_path}')
        print(f'   - 프레임: {visual_count}장, 재생시간: {visual_count * 0.3:.1f}초')

# Thermal 동영상 생성
if thermal_count > 0:
    thermal_video_path = os.path.join(viz_dir, 'thermal_detection.mp4')
    if create_video(os.path.join(viz_dir, 'thermal'), thermal_video_path):
        print(f'✅ Thermal 동영상 생성: {thermal_video_path}')
        print(f'   - 프레임: {thermal_count}장, 재생시간: {thermal_count * 0.3:.1f}초')

# NVG 동영상 생성 (있는 경우)
if os.path.exists(nvg_dir):
    nvg_count_for_video = len(glob.glob(os.path.join(viz_dir, 'nvg', '*.png')))
    if nvg_count_for_video > 0:
        nvg_video_path = os.path.join(viz_dir, 'nvg_detection.mp4')
        if create_video(os.path.join(viz_dir, 'nvg'), nvg_video_path):
            print(f'✅ NVG 동영상 생성: {nvg_video_path}')
            print(f'   - 프레임: {nvg_count_for_video}장, 재생시간: {nvg_count_for_video * 0.3:.1f}초')

print(f'\n📁 모든 작업 완료! 결과: output/visualization/{folder_name}/')
