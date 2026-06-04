import cv2
import numpy as np 
import os
import math
from ultralytics import YOLO

current_path = os.path.dirname(__file__)
camera_params_path = os.path.join(current_path, "camera_params.npz")
ipm_path = os.path.join(current_path, "IPM.npz")

if not os.path.exists(camera_params_path) or not os.path.exists(ipm_path):
    print("npz file load ERROR")
    exit()
    
with np.load(camera_params_path) as X:
    mtx, dist = X['mtx'], X['dist']
with np.load(ipm_path) as X:
    ipm_matrix = X['M']

Marker_Pixels = 150
Marker_Real_Size = 0.1
Pixel_To_Meter = Marker_Real_Size / Marker_Pixels

BEV_Width, BEV_Height = 400, 500

Camera_BEV_X = BEV_Width / 2
Camera_BEV_Y = BEV_Height

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

model = YOLO('yolo26m-sem.pt')

while True:
    ret, frame = cap.read()
    if not ret: 
        break

    frame_undistorted = cv2.undistort(frame, mtx, dist, None, mtx)

    results = model(frame_undistorted, stream = True, conf= 0.5, verbose = False)

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

            cls_name = model.names[int(box.cls[0])]

            bottom_center_x = (x1 + x2) / 2
            bottom_center_y = y2

            pt_src = np.array([[[bottom_center_x, bottom_center_y]]], dtype = np.float32)

            pt_bev = cv2.perspectiveTransform(pt_src, ipm_matrix)
            bev_x, bev_y = pt_bev[0][0]

            distance_pixels = math.sqrt((bev_x - Camera_BEV_X)**2 + (bev_y - Camera_BEV_Y)**2)
            distance_meters = distance_pixels * Pixel_To_Meter

            if bev_y > Camera_BEV_Y: 
                continue

            cv2.rectangle(frame_undistorted, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.circle(frame_undistorted, (int(bottom_center_x), int(bottom_center_y)), 5, (0, 0, 255), -1)

            text = f"{cls_name} {distance_meters:.2f}m"
            cv2.putText(frame_undistorted, text, (x1, y1, -10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            #測試看看會不會有反應
            if distance_meters < 0.5:
                print("TOO CLOSE !!!!!!!!!")

    cv2.imshow("YOLO distance detection", frame_undistorted)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()



