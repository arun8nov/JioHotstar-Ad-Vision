import ultralytics
from ultralytics import YOLO
model =YOLO(r"D:\GIT\JioHotstar-Ad-Vision\models\Ad_track.pt")
model.track(source=r"D:\GIT\JioHotstar-Ad-Vision\sam.mp4",show=True)