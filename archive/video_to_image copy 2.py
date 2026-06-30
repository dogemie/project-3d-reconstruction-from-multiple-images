import os
import shutil
import pathlib
import utils.video
from rembg import remove
from PIL import Image
import cv2
import numpy as np
import asyncio

# 파일 경로 설정
video_path = "megu_video.mp4"
image_dir = pathlib.Path("images")  # 원본 이미지 저장 폴더
bg_removed_dir = pathlib.Path("images_no_bg")  # 배경 제거된 이미지 폴더
size_down_dir = pathlib.Path("image_size_down")  # 크기 조정된 이미지 폴더
bg_size_down_dir = pathlib.Path("images_no_bg_size_down")  # 배경 제거 및 크기 조정된 이미지 폴더
output_dir = pathlib.Path("output")  # COLMAP 결과 폴더

def preprocess_image(img_path):
    img = cv2.imread(img_path)
    blurred = cv2.GaussianBlur(img, (5,5), 0)  # 블러 처리로 부드러운 경계 만들기
    return Image.fromarray(blurred)

if __name__ == "__main__":
    # 1️⃣ 기존 폴더 삭제
    for folder in [image_dir, bg_removed_dir, size_down_dir, output_dir, bg_size_down_dir]:
        if folder.exists():
            shutil.rmtree(folder)
            print(f"⚠️ {folder} is removed.")

    # 2️⃣ 새 폴더 생성
    for folder in [image_dir, bg_removed_dir, size_down_dir, output_dir, bg_size_down_dir]:
        folder.mkdir(parents=True, exist_ok=True)
        print(f"✅ {folder} is created.")

    # 3️⃣ 비디오 → 이미지 변환
    print(f"📽️ Extracting frames from {video_path}...")
    utils.video.save_video2images(video_path)
    print("✅ Video to image conversion completed.")

    # 4️⃣ 이미지 배경 제거 및 크기 조정
    print("🎨 Removing backgrounds and resizing images...")
    for img_file in image_dir.glob("*.png"):  # PNG 형식 이미지만 처리
        input_image = Image.open(img_file)

        # 🔹 사전 필터링 적용
        input_image = preprocess_image(str(img_file))
        
        # 🔹 이미지 크기 1/4로 줄이기 (360x360)
        input_small_image = input_image.resize((360, 360), Image.LANCZOS)
        
        # 🔹 배경 제거 (알파 매팅 적용)
        output_image = remove(input_small_image, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=5)
        output_2_image = remove(input_image)  # 배경 제거

        
        # # 🔹 이미지 크기 1/4로 줄이기 (360x360)
        # output_image = output_image.resize((360, 360), Image.LANCZOS)

        # 배경 제거된 이미지 저장
        output_path = bg_removed_dir / img_file.name
        output_2_image.save(output_path)
        
        # 배경 제거된 사이즈 조절 이미지 저장
        output_path = bg_size_down_dir / img_file.name
        output_image.save(output_path)
        
        # 크기 조정된 이미지 저장
        size_down_path = size_down_dir / img_file.name
        input_small_image.save(size_down_path)
        
        print(f"🖼️ Saved (background removed): {output_path}")
        # print(f"📏 Saved (resized): {size_down_path}")

    print("✅ Background removal and resizing completed.")
