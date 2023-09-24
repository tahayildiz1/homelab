import numpy as np
import supervision as sv
import cv2
import os
import torch
from ultralytics import YOLO
import requests  

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print('Using device:', torch.cuda.get_device_name(torch.cuda.current_device()) if device.type == 'cuda' else device)


model = YOLO("./Yolo-Weights/yolov8n.pt")

RTSP_STREAM = " " #Hinzufügen der RSTP Zugangsdaten


OUTPUT_RESOLUTION = (736, 480)


polygon = np.array([
    [192, 280],[372, 284],[380, 380],[192, 368],[192, 276]
    #[60, 171],[1018, 171],[1020, 755],[26, 751],[52, 171] Alte Zone
])

video_info = sv.VideoInfo.from_video_path(RTSP_STREAM)
zone = sv.PolygonZone(polygon=polygon, frame_resolution_wh=video_info.resolution_wh)

box_annotator = sv.BoxAnnotator(thickness=2, text_thickness=2, text_scale=1)
zone_annotator = sv.PolygonZoneAnnotator(zone=zone, color=sv.Color.white(), thickness=3, text_thickness=3, text_scale=2)

cap = cv2.VideoCapture(RTSP_STREAM)


HA_BASE_URL = 'http://homeassistant.local:8123'
ACCESS_TOKEN = 'ACCESS_TOKEN'  


def turn_on_switch():
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'} if ACCESS_TOKEN else {}
    data = {'entity_id': 'switch.SWITCH_ID'}  #Switch ID aus Homeassistant herausnehmen
    response = requests.post(f'{HA_BASE_URL}/api/services/switch/turn_on', headers=headers, json=data)
    if response.status_code == 200:
        print("Zigbee smart switch turned ON")
        return True
    else:
        print("Failed to turn on Zigbee smart switch")
        return False


def turn_off_switch():
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'} if ACCESS_TOKEN else {}
    data = {'entity_id': 'switch.SWITCH_ID'}  #Switch ID aus Homeassistant herausnehmen
    response = requests.post(f'{HA_BASE_URL}/api/services/switch/turn_off', headers=headers, json=data)
    if response.status_code == 200:
        print("Zigbee smart switch turned OFF")
        return True
    else:
        print("Failed to turn off Zigbee smart switch")
        return False

while True:
    ret, frame = cap.read()

    if not ret:
        break


    height, width, _ = frame.shape
    new_width = OUTPUT_RESOLUTION[0]
    new_height = int((new_width / width) * height)
    frame = cv2.resize(frame, (new_width, new_height))


    results = model(frame, imgsz=OUTPUT_RESOLUTION, show=False)[0] #Show=True Yolov8 Anzeige aktivieren
    detections = sv.Detections.from_yolov8(results)
    detections = detections[detections.class_id == 15]  # Klasse 15 sind Katzen


    cat_detected_in_zone = zone.trigger(detections=detections)

    labels = [f"{model.names[class_id]} {confidence:0.2f}" for _, _, confidence, class_id, _ in detections]
    frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)
    frame = zone_annotator.annotate(scene=frame)


    if cat_detected_in_zone.any():

        turn_on_switch()
    else:

        turn_off_switch()


    cv2.imshow("RTSP Stream", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
