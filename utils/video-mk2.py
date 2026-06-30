import cv2
import numpy as np
import os

import cv2
import numpy as np
import os

def save_video2images(video_path, target_frames=100):
    i = 0
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Cannot open video file.")
        return
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 전체 프레임 개수
    frame_skip = max(1, total_frames // target_frames)  # 프레임 건너뛰기 간격 계산

    print(f"Total frames in video: {total_frames}")
    print(f"Saving every {frame_skip} frames to get approximately {target_frames} images.")

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # 영상 끝에 도달하면 종료

        if frame_count % frame_skip == 0:  # 일정 간격마다 저장
            cv2.imwrite(f"images/image{i:04d}.png", frame)
            i += 1

        frame_count += 1

    cap.release()
    print(f"Images saved: {i}")
    print("Images ready!")



def video2array(video_path, target_frames=150):
    cap = cv2.VideoCapture(video_path)
    frames = []

    if not cap.isOpened():
        print("Error: Cannot open video file.")
        return np.array([])

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 전체 프레임 개수
    frame_skip = max(1, total_frames // target_frames)  # 프레임 건너뛰기 간격 계산

    print(f"Total frames in video: {total_frames}")
    print(f"Saving every {frame_skip} frames to get approximately {target_frames} images.")

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # 영상 끝에 도달하면 종료

        if frame_count % frame_skip == 0:  # 일정 간격마다 저장
            frames.append(frame)

        frame_count += 1

    cap.release()

    frames_array = np.array(frames, dtype=np.uint8)
    print("Frames shape:", frames_array.shape)

    return frames_array

