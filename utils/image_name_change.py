import os

def rename_images(folder_path):
    # 폴더 내의 파일 목록 가져오기
    files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))])
    
    # 이미지 파일 이름 변경
    for idx, file_name in enumerate(files, start=1):
        ext = os.path.splitext(file_name)[1]  # 확장자 추출
        new_name = f"image{idx:03d}{ext}"  # 3자리 숫자로 포맷팅
        old_path = os.path.join(folder_path, file_name)
        new_path = os.path.join(folder_path, new_name)
        
        # 파일 이름 변경
        os.rename(old_path, new_path)
        print(f"Renamed: {file_name} -> {new_name}")

# 사용 예시
folder_path = "data\Megumin"  # 폴더 경로를 변경하세요
rename_images(folder_path)
