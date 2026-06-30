import os
import pathlib
import pycolmap

# COLMAP 관련 출력 경로 설정
image_dir = pathlib.Path("image_size_down")  # 배경이 제거된 이미지 폴더 사용
output_path = pathlib.Path("output")  # COLMAP 재구성 결과 폴더
database_path = output_path / "database.db"

if __name__ == "__main__":
    # 기존 output 폴더 삭제 후 생성
    if os.path.exists(output_path):
        print(f"Removing existing {output_path} directory...")
        os.system(f"rm -rf {output_path}")  # Windows에서는 shutil.rmtree 사용 가능
        print(f"{output_path} is removed.")

    output_path.mkdir(exist_ok=True)

    # COLMAP 데이터베이스 생성 및 feature extraction
    print("Extracting features...")
    pycolmap.extract_features(database_path, image_dir)

    print("Matching features...")
    pycolmap.match_exhaustive(database_path)

    print("Running incremental mapping...")
    maps = pycolmap.incremental_mapping(database_path, image_dir, output_path)

    # 첫 번째 reconstruction 결과 저장
    if maps:
        maps[0].write(output_path)
        print("Sparse reconstruction completed.")
    else:
        print("Error: No reconstructions were generated.")
