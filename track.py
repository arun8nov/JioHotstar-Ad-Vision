from ultralytics import YOLO
import csv

class Traking:
    def __init__(self):
        pass

    def Ad_tracking(self,video_path):
        # Paths
        model_path = r"D:\GIT\JioHotstar-Ad-Vision\models\Ad_track.pt"
        csv_path = video_path.replace(".mp4", "_ad_tracking_results.csv")

        # Load model
        model = YOLO(model_path)

            
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


