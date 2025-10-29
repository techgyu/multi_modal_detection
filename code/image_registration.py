import cv2
import numpy as np
import os
import glob

# 테스트할 폴더 (여기 경로 수정)
folder_name = '20251029_Takistan_1400_Taleban_2'
data_dir = os.path.join('data', folder_name)
visual_dir = os.path.join(data_dir, 'visual')
thermal_dir = os.path.join(data_dir, 'thermal')
label_dir = os.path.join('output', folder_name, 'labels')

# 출력 폴더
output_dir = 'test_registration'
os.makedirs(output_dir, exist_ok=True)

print("=" * 60)
print("Visual ↔ Thermal 이미지 정합 테스트")
print("=" * 60)

# Visual과 Thermal 이미지 쌍 가져오기 (처음 5장으로 테스트)
visual_files = sorted(glob.glob(os.path.join(visual_dir, '*_v.png')))[:5]

if len(visual_files) == 0:
    print("❌ Visual 이미지를 찾을 수 없습니다!")
    exit()

print(f"\n📁 총 {len(visual_files)}개 이미지 쌍으로 정합 테스트\n")

# 변환 행렬을 저장할 리스트
homography_matrices = []

for idx, visual_path in enumerate(visual_files):
    base_name = os.path.basename(visual_path)
    # 000001_v.png -> 000001
    base_num = base_name.replace('_v.png', '').replace('_v.jpg', '')
    thermal_path = os.path.join(thermal_dir, f'{base_num}_th.png')
    
    if not os.path.exists(thermal_path):
        thermal_path = os.path.join(thermal_dir, f'{base_num}_th.jpg')
    
    if not os.path.exists(thermal_path):
        print(f"⚠️  Thermal 이미지 없음: {base_num}")
        continue
    
    print(f"[{idx+1}/{len(visual_files)}] Processing: {base_num}")
    
    # 이미지 읽기
    img_visual = cv2.imread(visual_path)
    img_thermal = cv2.imread(thermal_path)
    
    if img_visual is None or img_thermal is None:
        print(f"  ⚠️  이미지 로드 실패")
        continue
    
    # Grayscale 변환
    gray_visual = cv2.cvtColor(img_visual, cv2.COLOR_BGR2GRAY)
    gray_thermal = cv2.cvtColor(img_thermal, cv2.COLOR_BGR2GRAY)
    
    # 히스토그램 평활화 (대비 향상)
    gray_visual = cv2.equalizeHist(gray_visual)
    gray_thermal = cv2.equalizeHist(gray_thermal)
    
    # SIFT 특징점 검출기 생성 (ORB보다 정밀함)
    try:
        sift = cv2.SIFT_create(nfeatures=10000, contrastThreshold=0.02, edgeThreshold=5)
    except:
        print("  ⚠️  SIFT 사용 불가, ORB 사용")
        sift = cv2.ORB_create(nfeatures=10000)
    
    # 특징점 및 디스크립터 검출
    kp1, des1 = sift.detectAndCompute(gray_visual, None)
    kp2, des2 = sift.detectAndCompute(gray_thermal, None)
    
    print(f"  Visual 특징점: {len(kp1)}개, Thermal 특징점: {len(kp2)}개")
    
    if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
        print(f"  ⚠️  특징점 부족 (최소 4개 필요)")
        continue
    
    # FLANN 매칭 (더 정밀함)
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=100)  # 검색 정밀도 높임
    
    try:
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)
        
        # Lowe's ratio test로 좋은 매칭만 선택
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < 0.7 * n.distance:  # ratio threshold
                    good_matches.append(m)
    except:
        # SIFT 못 쓰면 BFMatcher
        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
        matches = bf.match(des1, des2)
        good_matches = sorted(matches, key=lambda x: x.distance)[:int(len(matches) * 0.3)]
    
    print(f"  좋은 매칭: {len(good_matches)}개")
    
    if len(good_matches) < 20:  # 최소 매칭 수 증가
        print(f"  ⚠️  매칭 포인트 부족 (최소 20개 권장)")
        continue
    
    # 매칭된 점들의 좌표 추출
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    
    # Homography 행렬 계산 (RANSAC, 더 엄격한 threshold)
    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 3.0, maxIters=5000, confidence=0.995)
    
    if H is None:
        print(f"  ❌ Homography 계산 실패")
        continue
    
    # Inlier 비율 확인 (품질 검증)
    inliers = np.sum(mask)
    inlier_ratio = inliers / len(good_matches)
    
    print(f"  Homography: Inliers {inliers}/{len(good_matches)} ({inlier_ratio*100:.1f}%)")
    
    # Inlier 비율이 너무 낮으면 신뢰도 낮음
    if inlier_ratio < 0.3:
        print(f"  ⚠️  Inlier 비율 낮음 ({inlier_ratio*100:.1f}%), 품질 의심")
    else:
        homography_matrices.append(H)
        print(f"  ✅ 고품질 Homography 계산 성공")
    
    # Visual 이미지를 Thermal 좌표계로 변환
    h, w = img_thermal.shape[:2]
    img_warped = cv2.warpPerspective(img_visual, H, (w, h))
    
    # 라벨이 있으면 변환해서 시각화
    label_path = os.path.join(label_dir, f'{base_num}_v.txt')
    
    if os.path.exists(label_path):
        # 원본 라벨로 thermal에 박스 그리기 (빨간색 - 정합 전)
        img_thermal_before = img_thermal.copy()
        
        # 변환된 라벨로 thermal에 박스 그리기 (초록색 - 정합 후)
        img_thermal_after = img_thermal.copy()
        
        with open(label_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 5:
                    cls, x_center, y_center, width, height = map(float, parts)
                    
                    # YOLO normalized -> pixel 좌표
                    img_h, img_w = img_thermal.shape[:2]
                    x_center_px = x_center * img_w
                    y_center_px = y_center * img_h
                    box_w = width * img_w
                    box_h = height * img_h
                    
                    x1 = int(x_center_px - box_w / 2)
                    y1 = int(y_center_px - box_h / 2)
                    x2 = int(x_center_px + box_w / 2)
                    y2 = int(y_center_px + box_h / 2)
                    
                    # 원본 좌표 (빨간색)
                    cv2.rectangle(img_thermal_before, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(img_thermal_before, 'original', (x1, y1-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    
                    # Homography로 박스 좌표 변환
                    # 박스의 4개 코너 포인트
                    corners = np.float32([
                        [x1, y1],
                        [x2, y1],
                        [x2, y2],
                        [x1, y2]
                    ]).reshape(-1, 1, 2)
                    
                    # 변환된 코너
                    corners_warped = cv2.perspectiveTransform(corners, H)
                    
                    # 변환된 코너로 새로운 bounding box 계산
                    x_coords = corners_warped[:, 0, 0]
                    y_coords = corners_warped[:, 0, 1]
                    x1_new = int(np.min(x_coords))
                    y1_new = int(np.min(y_coords))
                    x2_new = int(np.max(x_coords))
                    y2_new = int(np.max(y_coords))
                    
                    # 변환된 좌표 (초록색)
                    cv2.rectangle(img_thermal_after, (x1_new, y1_new), (x2_new, y2_new), (0, 255, 0), 2)
                    cv2.putText(img_thermal_after, 'registered', (x1_new, y1_new-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # 비교 이미지 저장
        cv2.imwrite(os.path.join(output_dir, f'{base_num}_thermal_before.png'), img_thermal_before)
        cv2.imwrite(os.path.join(output_dir, f'{base_num}_thermal_after.png'), img_thermal_after)
        print(f"  💾 저장: {base_num}_thermal_before.png, {base_num}_thermal_after.png")
    
    # 매칭 시각화
    img_matches = cv2.drawMatches(img_visual, kp1, img_thermal, kp2, 
                                  good_matches[:50], None, 
                                  flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    cv2.imwrite(os.path.join(output_dir, f'{base_num}_matches.png'), img_matches)
    
    # 정합된 이미지 저장
    cv2.imwrite(os.path.join(output_dir, f'{base_num}_warped.png'), img_warped)
    
    print()

# 평균 Homography 계산
if len(homography_matrices) > 0:
    avg_H = np.mean(homography_matrices, axis=0)
    print("=" * 60)
    print(f"✅ 총 {len(homography_matrices)}개 이미지에서 Homography 계산 성공")
    print("\n평균 Homography 행렬:")
    print(avg_H)
    
    # 행렬 저장
    np.save(os.path.join(output_dir, 'homography_matrix.npy'), avg_H)
    print(f"\n💾 Homography 행렬 저장: {output_dir}/homography_matrix.npy")
    print("=" * 60)
    print(f"\n📁 결과 확인: {output_dir}/")
    print("   - *_thermal_before.png: 원본 라벨 (빨간색)")
    print("   - *_thermal_after.png: 정합 후 라벨 (초록색)")
    print("   - *_matches.png: 특징점 매칭 결과")
    print("   - *_warped.png: 정합된 Visual 이미지")
else:
    print("❌ Homography 계산 실패!")
