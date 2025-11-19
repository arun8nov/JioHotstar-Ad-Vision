from ultralytics import YOLO
import cv2
import pandas as pd
import os

# ---------------------------
# Input video + model path
# ---------------------------
video_path = r"data/1/source_video.mp4"  # your file
model = YOLO(r"D:\GIT\JioHotstar-Ad-Vision\models\Ad_track.pt")     # your brand/logo trained model

# ---------------------------
# Prepare output csv
# ---------------------------
results_list = []

cap = cv2.VideoCapture(video_path)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)

print(f"Total Frames: {total_frames}, FPS: {fps}")

frame_no = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_no += 1

    # Run detection for this frame
    detections = model(frame, verbose=False)

    for result in detections:
        boxes = result.boxes

        for box in boxes:
            cls = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            class_name = model.names[cls]

            # timestamp from frame number
            timestamp_sec = frame_no / fps

            # Add to results
            results_list.append({
                "frame": frame_no,
                "time_sec": round(timestamp_sec, 2),
                "total_frames": total_frames,
                "brand": class_name,
                "confidence": round(conf, 3),
                "x1": int(x1), "y1": int(y1),
                "x2": int(x2), "y2": int(y2)
            })

cap.release()

# Save CSV
df = pd.DataFrame(results_list)
output_csv = "ad_detection_results.csv"
df.to_csv(output_csv, index=False)

print(f"Saved: {output_csv}")
