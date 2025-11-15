from ultralytics import YOLO
import csv
import cv2
import os

model_path = r"D:\GIT\JioHotstar-Ad-Vision\models\Ad_track.pt"
model = YOLO(model_path)

class Traking:
    def __init__(self):
        pass

    def ad_tracking_and_classwise_extraction(self, video_path, folder_path):
        # Setup paths
        csv_path = video_path.replace(".mp4", "_ad_tracking_results.csv")
        output_base_folder = os.path.join(folder_path, "extracted_frames")
        os.makedirs(output_base_folder, exist_ok=True)

        # Get total frames
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Open CSV for writing
        with open(csv_path, "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "Frame",
                "Total_Frames",
                "Detections",
                "Time (ms)"
            ])
            frame_index = 0

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                results = model.track(frame)
                boxes = results[0].boxes

                names = []
                if hasattr(results[0], "names") and boxes is not None:
                    cls_list = boxes.cls.tolist()
                    for c in cls_list:
                        names.append(results[0].names[int(c)])
                    detection_str = ", ".join(names) if names else "(no detections)"
                else:
                    detection_str = "(no detections)"

                # Get inference time
                inference_time = getattr(results[0], "speed", {}).get("inference", None)
                inference_ms = f"{inference_time:.1f}" if inference_time is not None else "-"

                # Write to CSV
                writer.writerow([
                    frame_index + 1,
                    total_frames,
                    detection_str,
                    inference_ms
                ])

                # Save frames class-wise
                detected_classes = set(int(cls) for cls in boxes.cls) if boxes is not None else set()
                for class_id in detected_classes:
                    class_name = results[0].names[class_id]
                    class_folder = os.path.join(output_base_folder, class_name)
                    os.makedirs(class_folder, exist_ok=True)
                    filename = os.path.join(class_folder, f"frame_{frame_index:06d}.jpg")
                    annotated_frame = results[0].plot()
                    cv2.imwrite(filename, annotated_frame)

                frame_index += 1

            cap.release()
        print(f"Process complete! CSV: {csv_path}, Frames: {output_base_folder}")

