import ultralytics
from ultralytics import YOLO
import sys
from contextlib import redirect_stdout

log_file = 'sample_video_log.txt'
with open(log_file, 'w') as f:
    with redirect_stdout(f):    
        model =YOLO("best.pt")
        model.track(
            source=r"D:\GIT\JioHotstar-Ad-Vision\data\videos\sample.mp4",
            show=True)

print(f"Logs have been written to {log_file}")