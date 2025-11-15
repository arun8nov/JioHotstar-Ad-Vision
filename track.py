from ultralytics import YOLO
import csv
import cv2
import os

model_path = r"D:\GIT\JioHotstar-Ad-Vision\models\Ad_track.pt"
model = YOLO(model_path)

class Traking:
    def __init__(self):
        pass

    def Ad_tracking(self,video_path):
        
        csv_path = video_path.replace(".mp4", "_ad_tracking_results.csv")
 
        # Run tracking and get generator of results
        results = model.track(source=video_path, save=True, stream=True, show=False)

        # Get total frames with OpenCV
        import cv2
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        # Write CSV
        with open(csv_path, "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "Frame",
                "Total_Frames",
                "Detections",
                "Time (ms)"
            ])
            frame_num = 1
            for result in results:
                

                # Get detections/comment
                names = []
                if hasattr(result, "names") and result.boxes is not None:
                    cls_list = result.boxes.cls.tolist()
                    for c in cls_list:
                        names.append(result.names[int(c)])
                    detection_str = ", ".join(names) if names else "(no detections)"
                else:
                    detection_str = "(no detections)"

                # Get inference time in ms
                inference_time = getattr(result, "speed", {}).get("inference", None)
                inference_ms = f"{inference_time:.1f}" if inference_time is not None else "-"

                # Write row
                writer.writerow([
                    frame_num,
                    total_frames,
                    detection_str,
                    inference_ms
                ])
                frame_num += 1

        print(f"Tracking and CSV export complete! Saved as {csv_path}")


    def class_frame_extraction(self,video_path,folder_path):
        output_base_folder = folder_path+"/extracted_frames"
        if not os.path.exists(output_base_folder):
            os.makedirs(output_base_folder)

        cap = cv2.VideoCapture(video_path)
        frame_index = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = model.track(frame)
            boxes = results[0].boxes

            # Get all detected class ids in this frame
            detected_classes = set(int(cls) for cls in boxes.cls)

            for class_id in detected_classes:
                class_name = results[0].names[class_id]
                class_folder = os.path.join(output_base_folder, class_name)
                os.makedirs(class_folder, exist_ok=True)
                filename = os.path.join(class_folder, f"frame_{frame_index:06d}.jpg")
                annotated_frame = results[0].plot()
                cv2.imwrite(filename, annotated_frame)

            frame_index += 1

        cap.release()
        print(f"Frame extraction complete! Frames saved in {output_base_folder}")

        