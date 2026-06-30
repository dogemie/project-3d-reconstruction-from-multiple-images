import os
import shutil
import pathlib
import utils.video
from rembg import remove
from PIL import Image, ImageOps
import concurrent.futures

# 파일 경로 설정
video_path = "megu_video.mp4"
image_dir = pathlib.Path("images")  # 원본 이미지 저장 폴더
size_down_dir = pathlib.Path("image_size_down")  # 크기 조정된 이미지 폴더
bg_size_down_dir = pathlib.Path("images_no_bg_size_down")  # 배경 제거 및 크기 조정된 이미지 폴더
output_dir = pathlib.Path("output")  # COLMAP 결과 폴더
previous_dir = pathlib.Path("image_previous")  # 백업 폴더

# 🔹 이전 폴더를 백업하는 함수
def backup_previous_folders():
    """ 기존 작업 폴더들을 백업 폴더(image_previous/000X)로 이동 """
    previous_dir.mkdir(parents=True, exist_ok=True)
    
    # 현재 몇 개의 백업 폴더가 있는지 확인하고 새로운 폴더 번호 지정
    existing_folders = sorted(previous_dir.glob("*/"), key=lambda x: int(x.name) if x.name.isdigit() else -1)
    next_folder_num = int(existing_folders[-1].name) + 1 if existing_folders else 1
    new_backup_folder = previous_dir / f"{next_folder_num:04d}"
    new_backup_folder.mkdir(parents=True, exist_ok=True)

    # 이동할 폴더 리스트
    folders_to_move = [size_down_dir, bg_size_down_dir, output_dir]

    for folder in folders_to_move:
        if folder.exists():
            shutil.move(str(folder), str(new_backup_folder / folder.name))
            print(f"📂 Moved {folder} → {new_backup_folder / folder.name}")

    print(f"✅ All previous folders backed up to {new_backup_folder}")

# 🔹 새로운 폴더 생성
def setup_folders():
    """ 새 작업 폴더 생성 """
    for folder in [size_down_dir, bg_size_down_dir, output_dir]:
        folder.mkdir(parents=True, exist_ok=True)
        print(f"✅ {folder} is created.")

# 🔹 이미지 크기 조정 함수
def resize_image(img_file):
    input_image = Image.open(img_file)
    resized_image = input_image.resize((360, 360), Image.LANCZOS)
    output_path = size_down_dir / img_file.name
    resized_image.save(output_path)
    print(f"📏 Resized and saved: {output_path}")
    return output_path

# 🔹 배경 제거 후 흰색 배경 적용 함수
def remove_background(img_file):
    input_image = Image.open(img_file)

    # 배경 제거 수행
    output_image = remove(
        input_image,
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=2
    )

    # RGBA → RGB 변환 (투명한 부분을 흰색으로 채우기)
    output_image = output_image.convert("RGBA")  # RGBA 모드로 변환
    white_background = Image.new("RGBA", output_image.size, (255, 255, 255, 255))  # 흰색 배경 생성
    output_image = Image.alpha_composite(white_background, output_image).convert("RGB")  # 배경 합성 후 RGB 변환

    # 저장
    output_path = bg_size_down_dir / img_file.name
    output_image.save(output_path)
    print(f"🖼️ Background removed and saved (with white bg): {output_path}")

if __name__ == "__main__":
    # 1️⃣ 기존 작업 백업
    backup_previous_folders()

    # 2️⃣ 새 폴더 생성
    setup_folders()

    # 3️⃣ 비디오 → 이미지 변환
    print(f"📽️ Extracting frames from {video_path}...")
    utils.video.save_video2images(video_path)
    print("✅ Video to image conversion completed.")

    # 4️⃣ 멀티스레드를 이용하여 크기 조정과 배경 제거를 동시에 실행
    img_files = list(image_dir.glob("*.png"))
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 이미지 크기 조정 실행
        resized_images = list(executor.map(resize_image, img_files))
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 배경 제거 실행 (흰색 배경 포함)
        executor.map(remove_background, resized_images)
    
    print("✅ All images processed successfully!")
