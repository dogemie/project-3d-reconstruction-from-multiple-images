import os
import shutil
import pathlib
import utils.video
from rembg import remove
from PIL import Image
import concurrent.futures

# 파일 경로 설정
video_path = "megu_video.mp4"
image_dir = pathlib.Path("images")  # 원본 이미지 저장 폴더
size_down_dir = pathlib.Path("image_size_down")  # 크기 조정된 이미지 폴더
bg_size_down_dir = pathlib.Path("images_no_bg_size_down")  # 배경 제거 및 크기 조정된 이미지 폴더
output_dir = pathlib.Path("output")  # COLMAP 결과 폴더

# 기존 폴더 삭제 및 생성
def setup_folders():
    for folder in [image_dir, size_down_dir, bg_size_down_dir, output_dir]:
        if folder.exists():
            shutil.rmtree(folder)
            print(f"⚠️ {folder} is removed.")
        folder.mkdir(parents=True, exist_ok=True)
        print(f"✅ {folder} is created.")

# 이미지 크기 조정 함수
def resize_image(img_file):
    input_image = Image.open(img_file)
    resized_image = input_image.resize((360, 360), Image.LANCZOS)
    output_path = size_down_dir / img_file.name
    resized_image.save(output_path)
    print(f"📏 Resized and saved: {output_path}")
    return output_path

# 배경 제거 함수 (흰색 배경 적용)
def remove_background(img_file):
    input_image = Image.open(img_file)

    # 배경 제거 수행
    output_image = remove(
        input_image,
        alpha_matting=True,
        alpha_matting_foreground_threshold=250,  # 좀 더 높은 임계값으로 정밀 구분
        alpha_matting_background_threshold=5,  # 배경을 최대한 날리도록 조정
        alpha_matting_erode_size=5  # 경계 부분을 부드럽게
    )

    # 배경을 흰색으로 변환
    white_bg = Image.new("RGBA", output_image.size, (255, 255, 255, 255))  # 흰색 배경 생성
    output_image = Image.alpha_composite(white_bg, output_image)  # 흰색 배경과 합성

    # PNG의 알파 채널 제거하고 RGB로 변환 (투명도 제거)
    output_image = output_image.convert("RGB")

    output_path = bg_size_down_dir / img_file.name
    output_image.save(output_path)
    print(f"🖼️ Background removed and saved (with white bg): {output_path}")

if __name__ == "__main__":
    setup_folders()

    # 1️⃣ 비디오 → 이미지 변환
    print(f"📽️ Extracting frames from {video_path}...")
    utils.video.save_video2images(video_path)
    print("✅ Video to image conversion completed.")

    # 2️⃣ 멀티스레드를 이용하여 크기 조정과 배경 제거를 동시에 실행
    img_files = list(image_dir.glob("*.png"))
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 이미지 크기 조정 실행
        resized_images = list(executor.map(resize_image, img_files))
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 배경 제거 실행 (흰색 배경 적용)
        executor.map(remove_background, resized_images)
    
    print("✅ All images processed successfully!")
