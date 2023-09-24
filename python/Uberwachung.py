import numpy as np
import supervision as sv
import cv2
import os
import torch
from ultralytics import YOLO


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print('Using device:', torch.cuda.get_device_name(torch.cuda.current_device()) if device.type == 'cuda' else device)

# Initialize the YOLO model
model = YOLO("./Yolo-Weights/yolov8n.pt")

RTSP_STREAM = " " #RTSP Zugansdaten eingeben


OUTPUT_RESOLUTION = (1920, 1088)


polygon = np.array([
[8, 242],[80, 218],[224, 210],[440, 190],[528, 182],[560, 182],[564, 350],[812, 342],[816, 638],[1392, 658],[1492, 10],[1904, 18],[1908, 982],[12, 978],[4, 242]])

video_info = sv.VideoInfo.from_video_path(RTSP_STREAM)
zone = sv.PolygonZone(polygon=polygon, frame_resolution_wh=video_info.resolution_wh)

box_annotator = sv.BoxAnnotator(thickness=2, text_thickness=2, text_scale=1)
zone_annotator = sv.PolygonZoneAnnotator(zone=zone, color=sv.Color.white(), thickness=3, text_thickness=3, text_scale=2)

cap = cv2.VideoCapture(RTSP_STREAM)


output_folder = "detected_person"
os.makedirs(output_folder, exist_ok=True)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    height, width, _ = frame.shape
    new_width = OUTPUT_RESOLUTION[0]
    new_height = int((new_width / width) * height)
    frame = cv2.resize(frame, (new_width, new_height))

    results = model(frame, imgsz=OUTPUT_RESOLUTION, show=False)[0]
    detections = sv.Detections.from_yolov8(results)
    detections = detections[detections.class_id == 0]

    person_detected_in_zone = zone.trigger(detections=detections)

    labels = [f"{model.names[class_id]} {confidence:0.2f}" for _, _, confidence, class_id, _ in detections]
    frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)
    frame = zone_annotator.annotate(scene=frame)

    if person_detected_in_zone.any():
        person_image_name = f"person_{len(os.listdir(output_folder))}.png"
        person_image_path = os.path.join(output_folder, person_image_name)
        cv2.imwrite(person_image_path, frame)

    cv2.imshow("RTSP Stream", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
