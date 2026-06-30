import os
import shutil
import pathlib
import cv2
import numpy as np
from PIL import Image
from rembg import remove

def ensure_folder_exists(folder):
    """폴더가 없으면 생성"""
    folder.mkdir(parents=True, exist_ok=True)

def backup_previous_study_folder():
    """기존 image_for_study 폴더를 백업"""
    study_previous_dir = pathlib.Path("image_study_previous")
    ensure_folder_exists(study_previous_dir)
    study_dir = pathlib.Path("image_for_study")
    
    if study_dir.exists():
        existing_backups = sorted(study_previous_dir.glob("000*"))
        new_index = 1 if not existing_backups else int(existing_backups[-1].name) + 1
        new_backup_folder = study_previous_dir / f"{new_index:04d}"
        shutil.move(str(study_dir), str(new_backup_folder))
        print(f"📂 Moved previous study images to {new_backup_folder}")
    
    ensure_folder_exists(study_dir)

def is_valid_study_image(img_path):
    """이미지가 3D Vision 학습에 적합한지 확인"""
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"❌ Skipping {img_path.name}, could not read file.")
        return False
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_ratio = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
    
    if edge_ratio < 0.01:
        print(f"❌ Skipping {img_path.name}, insufficient edge details.")
        return False
    
    return True

def process_images():
    """이미지를 필터링하여 학습 가능한 이미지만 저장"""
    source_dir = pathlib.Path("image_size_down")
    target_dir = pathlib.Path("image_for_study")
    backup_previous_study_folder()
    
    images = list(source_dir.glob("*.png"))
    if not images:
        print("⚠️ No images found in image_size_down.")
        return
    
    for img_file in images:
        if is_valid_study_image(img_file):
            shutil.copy(str(img_file), str(target_dir / img_file.name))
            print(f"✅ Copied: {img_file.name}")
        else:
            print(f"❌ Removed: {img_file.name}")
    
    print("✅ Image filtering process completed!")

if __name__ == "__main__":
    process_images()
