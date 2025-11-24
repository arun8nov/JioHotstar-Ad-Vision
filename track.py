from ultralytics import YOLO
import cv2
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
import sqlalchemy

db_user = os.getenv("db_user")
db_password = os.getenv("db_password")
db_host = os.getenv("db_host")
db_port = os.getenv("db_port")
db_name = os.getenv("db_name")

engine = sqlalchemy.create_engine(f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

model_path = r"D:\GIT\JioHotstar-Ad-Vision\models\Ad_track.pt"
model = YOLO(model_path)

class Tracking:
    def __init__(self):
        pass

    def ad_tracking_and_classwise_extraction(self,match_id, video_path, folder_path):

        # Folder and file setup
        output_csv = video_path.replace(".mp4", "_ad_tracking_details.csv")
        output_frames_root = os.path.join(folder_path, "extracted_frames")
        os.makedirs(output_frames_root, exist_ok=True)

        # Open video file for processing
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        results_list = []
        frame_no = 0
        # Process video frames
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_no += 1

            # YOLO Tracking
            results = model.track(frame, verbose=False)
            boxes = results[0].boxes
            # If detections exist, process them
            if boxes is not None and len(boxes) > 0:
                annotated_frame = results[0].plot()

                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    conf = float(box.conf[0].item())
                    x1, y1, x2, y2 = box.xyxy[0].tolist()

                    class_name = results[0].names[cls_id]
                    timestamp_sec = frame_no / fps

                    # Record detection details in results list
                    results_list.append({
                        "match_id": match_id,
                        "frame": frame_no,
                        "time_sec": round(timestamp_sec, 2),
                        "total_frames": total_frames,
                        "brand": class_name,
                        "confidence": round(conf, 3),
                        "x1": int(x1), "y1": int(y1),
                        "x2": int(x2), "y2": int(y2)
                    })

                    ## Save annotated frames class-wise
                    class_folder = os.path.join(output_frames_root, class_name)
                    os.makedirs(class_folder, exist_ok=True)

                    filename = os.path.join(
                        class_folder,
                        f"frame_{frame_no:06d}.jpg"
                    )
                    cv2.imwrite(filename, annotated_frame)

        cap.release()

        # Save CSV
        df = pd.DataFrame(results_list)
        df.to_csv(output_csv, index=False)
        df.to_sql("brand_detections", engine, if_exists="append", index=False)

        print("✔ Process Completed!")
        print(f"CSV Saved → {output_csv}")
        print(f"Frames Saved → {output_frames_root}")
