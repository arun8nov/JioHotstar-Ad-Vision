import cv2
import os

video_path = "sample.mp4"   # Path to your video
output_folder = "frames"         # Folder to save frames

os.makedirs(output_folder, exist_ok=True)
cap = cv2.VideoCapture(video_path)

fps = cap.get(cv2.CAP_PROP_FPS)  # Frames per second in video
frame_count = 0
saved_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    # Save only one frame per second
    if frame_count % int(fps) == 0:
        frame_name = os.path.join(output_folder, f"frame_{saved_count:06d}.jpg")
        cv2.imwrite(frame_name, frame)
        saved_count += 1
    frame_count += 1

cap.release()
print(f"Extracted {saved_count} frames at 1 fps to {output_folder}")
