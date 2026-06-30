import os
import shutil
import pathlib
import pycolmap

# COLMAP 관련 출력 경로 설정
image_dir = pathlib.Path("images_no_bg_size_down")  # 배경이 제거된 이미지 폴더 사용
output_path = pathlib.Path("output")  # COLMAP 재구성 결과 폴더
sparse_path = output_path / "sparse"  # Sparse reconstruction 데이터 저장 폴더
final_output_path = output_path / "0"  # NeRF에서 사용하기 위한 최종 폴더
database_path = output_path / "database.db"

if __name__ == "__main__":
    # 1️⃣ 기존 output 폴더 삭제 후 새로 생성
    if output_path.exists():
        print(f"⚠️ Removing existing {output_path} directory...")
        shutil.rmtree(output_path)  # Windows에서도 동작하도록 변경
        print(f"✅ {output_path} is removed.")

    output_path.mkdir(exist_ok=True)
    sparse_path.mkdir(exist_ok=True)

    # 2️⃣ COLMAP 데이터베이스 생성 및 feature extraction
    print("🔍 Extracting features...")
    pycolmap.extract_features(database_path, image_dir)

    print("🔗 Matching features...")
    pycolmap.match_exhaustive(database_path)

    print("🛠️ Running incremental mapping...")
    maps = pycolmap.incremental_mapping(database_path, image_dir, sparse_path)

    # 3️⃣ 첫 번째 reconstruction 결과 저장
    if maps:
        maps[0].write(sparse_path)
        print("✅ Sparse reconstruction completed.")

        # 4️⃣ `output/0` 폴더 생성 및 필요한 파일 이동
        final_output_path.mkdir(exist_ok=True)

        for file_name in ["cameras.bin", "images.bin", "points3D.bin"]:
            src = sparse_path / "0" / file_name
            dst = final_output_path / file_name
            if src.exists():
                shutil.move(str(src), str(dst))
                print(f"📂 Moved {file_name} to {final_output_path}")

        print("✅ All reconstruction files are ready for NeRF.")
    else:
        print("❌ Error: No reconstructions were generated.")
