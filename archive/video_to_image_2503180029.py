import os
import shutil
import pathlib
import utils.video
from rembg import remove
from PIL import Image
import concurrent.futures
import subprocess  # ✅ colmap_reconstruction.py 실행을 위한 모듈 추가
from pathlib import Path

# 파일 경로 설정
video_path = "megu_video.mp4"
image_dir = pathlib.Path("images")  # 원본 이미지 저장 폴더
bg_removed_dir = pathlib.Path("images_no_bg")  # 배경 제거된 원본 크기 폴더
size_down_dir = pathlib.Path("image_size_down")  # 크기 조정된 이미지 폴더
output_dir = pathlib.Path("output")  # COLMAP 결과 폴더
previous_dir = pathlib.Path("image_previous")  # ✅ 이전 작업 백업 폴더
colmap_script = "colmap_reconstruction.py"

# 기존 폴더를 백업하는 함수
def backup_previous_folders():
    previous_dir.mkdir(parents=True, exist_ok=True)

    # 새로운 백업 폴더 번호 지정 (0001, 0002, ...)
    existing_backups = sorted(previous_dir.glob("000*"))
    new_index = 1 if not existing_backups else int(existing_backups[-1].name) + 1
    new_backup_folder = previous_dir / f"{new_index:04d}"

    # 이전 폴더 이동
    new_backup_folder.mkdir(parents=True, exist_ok=True)
    for folder in [image_dir, bg_removed_dir, size_down_dir, output_dir]:
        if folder.exists():
            shutil.move(str(folder), str(new_backup_folder / folder.name))
            print(f"📂 Moved {folder} → {new_backup_folder / folder.name}")

# 기존 폴더 생성
def setup_folders():
    backup_previous_folders()  # ✅ 이전 작업 백업

    for folder in [image_dir, bg_removed_dir, size_down_dir, output_dir]:
        folder.mkdir(parents=True, exist_ok=True)
        print(f"✅ {folder} is created.")

# 배경 제거 함수 (정밀 제거 + 흰색 배경 적용)
def remove_background(img_file):
    input_image = Image.open(img_file)
    output_image = remove(
        input_image,
        alpha_matting=True,
        alpha_matting_foreground_threshold=250,
        alpha_matting_background_threshold=5,
        alpha_matting_erode_size=5
    )

    # 🔹 투명한 배경을 흰색으로 변환
    white_bg = Image.new("RGBA", output_image.size, (255, 255, 255, 255))
    output_image = Image.alpha_composite(white_bg, output_image).convert("RGB")

    output_path = bg_removed_dir / img_file.name
    output_image.save(output_path)
    print(f"🖼️ Background removed and saved: {output_path}")
    return output_path  # 배경 제거된 파일 경로 반환

# 이미지 크기 조정 함수
def resize_image(img_file):
    input_image = Image.open(img_file)
    resized_image = input_image.resize((90, 90), Image.LANCZOS)
    output_path = size_down_dir / img_file.name
    resized_image.save(output_path)
    print(f"📏 Resized and saved: {output_path}")

# COLMAP 리컨스트럭션 실행
def run_colmap_reconstruction(colmap_script):
    colmap_script = Path(colmap_script)
    if colmap_script.exists():  # ✅ 파일 존재 여부 확인
        print("🚀 Running COLMAP reconstruction...")
        result = subprocess.run(["python", str(colmap_script)], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ COLMAP reconstruction completed successfully!")
        else:
            print(f"❌ COLMAP reconstruction failed! Error:\n{result.stderr}")
    else:
        print(f"⚠️ {colmap_script} not found. Skipping COLMAP reconstruction.")

if __name__ == "__main__":
    setup_folders()

    # 1️⃣ 비디오 → 이미지 변환
    print(f"📽️ Extracting frames from {video_path}...")
    utils.video.save_video2images(video_path)
    print("✅ Video to image conversion completed.")

    # 2️⃣ 멀티스레드를 이용하여 배경 제거 후 크기 조정
    img_files = list(image_dir.glob("*.png"))
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 배경 제거 실행 (원본 크기 유지)
        bg_removed_images = list(executor.map(remove_background, img_files))
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 배경 제거된 이미지를 크기 조정하여 저장
        executor.map(resize_image, bg_removed_images)

    print("✅ All images processed successfully!")

    # 3️⃣ COLMAP 리컨스트럭션 실행
    run_colmap_reconstruction(colmap_script)
