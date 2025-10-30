"""
데이터셋 파일명을 순차적으로 재정렬하는 스크립트
- 이미지 파일과 labels 폴더의 txt 파일을 함께 리네임
- 기존 번호 건너뛴 파일들을 연속된 번호로 정리
"""

import os
import glob
from pathlib import Path
import shutil

def rename_dataset(dataset_dir, start_index=1, suffix='_v'):
    """
    데이터셋 파일명을 순차적으로 재정렬
    
    Args:
        dataset_dir: 데이터셋 디렉토리 경로 (예: 'output/20251029_Takistan_1200_Taleban')
        start_index: 시작 인덱스 (기본값: 1)
        suffix: 파일명 접미사 (예: '_v', '_th', '_ir')
    """
    dataset_path = Path(dataset_dir)
    labels_dir = dataset_path / 'labels'
    
    # 디렉토리 존재 확인
    if not dataset_path.exists():
        print(f"Error: 디렉토리가 존재하지 않습니다: {dataset_dir}")
        return
    
    # 이미지 파일 목록 가져오기 (숫자 순으로 정렬)
    image_files = sorted(glob.glob(str(dataset_path / f'*{suffix}.*')))
    image_files = [f for f in image_files if Path(f).suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp']]
    
    if not image_files:
        print(f"Error: {suffix} 접미사를 가진 이미지 파일이 없습니다.")
        return
    
    print(f"총 {len(image_files)}개 파일 발견")
    print(f"시작 인덱스: {start_index}")
    print(f"접미사: {suffix}")
    print()
    
    # 임시 디렉토리 생성 (충돌 방지)
    temp_dir = dataset_path / 'temp_rename'
    temp_labels_dir = temp_dir / 'labels'
    temp_dir.mkdir(exist_ok=True)
    temp_labels_dir.mkdir(exist_ok=True)
    
    # 파일 리네임 (임시 디렉토리로)
    current_index = start_index
    rename_mapping = []
    
    for img_file in image_files:
        img_path = Path(img_file)
        ext = img_path.suffix
        
        # 새 파일명 생성
        new_img_name = f"{current_index:06d}{suffix}{ext}"
        new_label_name = f"{current_index:06d}{suffix}.txt"
        
        # 원본 label 파일 경로
        old_label_path = labels_dir / f"{img_path.stem}.txt"
        
        # 임시 경로
        temp_img_path = temp_dir / new_img_name
        temp_label_path = temp_labels_dir / new_label_name
        
        # 이미지 복사
        shutil.copy2(img_path, temp_img_path)
        
        # 라벨 복사 (존재하는 경우)
        if old_label_path.exists():
            shutil.copy2(old_label_path, temp_label_path)
            rename_mapping.append((img_path.name, new_img_name, '✓'))
        else:
            rename_mapping.append((img_path.name, new_img_name, '✗ (no label)'))
        
        current_index += 1
    
    # 원본 파일 삭제
    print("원본 파일 삭제 중...")
    for img_file in image_files:
        os.remove(img_file)
        # 해당 라벨 파일도 삭제
        label_file = labels_dir / f"{Path(img_file).stem}.txt"
        if label_file.exists():
            os.remove(label_file)
    
    # 임시 디렉토리에서 원본 위치로 이동
    print("리네임된 파일 이동 중...")
    for file in temp_dir.glob(f'*{suffix}.*'):
        shutil.move(str(file), str(dataset_path / file.name))
    
    for file in temp_labels_dir.glob(f'*{suffix}.txt'):
        shutil.move(str(file), str(labels_dir / file.name))
    
    # 임시 디렉토리 삭제
    temp_labels_dir.rmdir()
    temp_dir.rmdir()
    
    # 결과 출력
    print("\n=== 리네임 완료 ===")
    print(f"총 {len(rename_mapping)}개 파일 처리")
    print("\n변경 내역:")
    for old_name, new_name, status in rename_mapping[:10]:  # 처음 10개만 출력
        print(f"  {old_name} → {new_name} {status}")
    
    if len(rename_mapping) > 10:
        print(f"  ... 외 {len(rename_mapping) - 10}개")
    
    print(f"\n최종 인덱스: {current_index - 1}")
    print(f"다음 데이터셋 추가 시 시작 인덱스: {current_index}")


def rename_multimodal_dataset(base_dir, start_index=1):
    """
    멀티모달 데이터셋 전체 리네임 (visual, thermal, nvg 모두)
    
    Args:
        base_dir: 상위 폴더 경로 (visual, thermal, nvg 포함)
        start_index: 시작 인덱스
    """
    base_path = Path(base_dir)
    
    modalities = {
        'visual': '_v',
        'thermal': '_th',
        'nvg': '_n'
    }
    
    print("=== 멀티모달 데이터셋 리네임 ===")
    print(f"Base directory: {base_dir}")
    print()
    
    for modality, suffix in modalities.items():
        modality_dir = base_path / modality
        if modality_dir.exists():
            print(f"\n--- {modality.upper()} 처리 중 ---")
            rename_dataset(str(modality_dir), start_index, suffix)
        else:
            print(f"Warning: {modality} 폴더가 존재하지 않습니다.")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("사용법:")
        print("  1. 단일 모달리티:")
        print("     python rename_dataset.py <dataset_dir> [start_index] [suffix]")
        print("     예: python rename_dataset.py output/visual_1 1 _v")
        print()
        print("  2. 멀티모달 (visual, thermal, nvg 모두):")
        print("     python rename_dataset.py <base_dir> [start_index] --multimodal")
        print("     예: python rename_dataset.py data/20251029_Takistan_1200 1 --multimodal")
        sys.exit(1)
    
    dataset_dir = sys.argv[1]
    start_index = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    if '--multimodal' in sys.argv:
        # 멀티모달 모드
        rename_multimodal_dataset(dataset_dir, start_index)
    else:
        # 단일 모달리티 모드
        suffix = sys.argv[3] if len(sys.argv) > 3 else '_v'
        rename_dataset(dataset_dir, start_index, suffix)
