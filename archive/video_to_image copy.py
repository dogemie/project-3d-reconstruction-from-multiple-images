import os
import shutil
import pathlib
import utils.video
from rembg import remove
from PIL import Image

# 파일 경로 설정
video_path = "megu_video.mp4"
image_dir = pathlib.Path("images")  # 비디오에서 추출한 이미지가 저장될 폴더
bg_removed_dir = pathlib.Path("images_no_bg")  # 배경이 제거된 이미지 폴더
output_dir = pathlib.Path("output")  # COLMAP 결과 폴더

if __name__ == "__main__":
    # 1️⃣ 기존 폴더 삭제 (images, images_no_bg, output)
    for folder in [image_dir, bg_removed_dir, output_dir]:
        if folder.exists():
            shutil.rmtree(folder)
            print(f"⚠️ {folder} is removed.")

    # 2️⃣ 새 폴더 생성
    for folder in [image_dir, bg_removed_dir, output_dir]:
        folder.mkdir(parents=True, exist_ok=True)
        print(f"✅ {folder} is created.")

    # 3️⃣ 비디오 → 이미지 변환
    print(f"📽️ Extracting frames from {video_path}...")
    utils.video.save_video2images(video_path)
    print("✅ Video to image conversion completed.")

    # 4️⃣ 이미지 배경 제거 (rembg 사용)
    print("🎨 Removing backgrounds from images...")
    for img_file in image_dir.glob("*.png"):  # PNG 형식 이미지만 처리 (필요 시 JPG 추가)
        input_image = Image.open(img_file)
        output_image = remove(input_image)  # 배경 제거

        # 배경 제거된 이미지 저장
        output_path = bg_removed_dir / img_file.name
        output_image.save(output_path)
        print(f"🖼️ Saved: {output_path}")

    print("✅ Background removal completed.")
