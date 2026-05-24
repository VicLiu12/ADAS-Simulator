import cv2
import numpy as np
import socket
import json
import os
import math

#參數設定
UDP_IP = "127.0.0.1"
UDP_PORT = 5052

Marker_Pixels = 150
Marker_Real_Size = 0.1
Pixel_To_Meter = Marker_Real_Size / Marker_Pixels

BEV_Width, BEV_Height = 400, 500

#讀取camera_params.npz和ipm.npz
current_path = os.path.dirname(__file__)
file_path = os.path.join(current_path, 'camera_params.npz', 'ipm.npz')

if not os.path.exists(file_path):
    print('File Load ERROR')
    exit()

with np.load('camera_params.npz') as X:
    mtx, dist = X['mtx'], X['dist']
with np.load('ipm.npz') as X:
    ipm_matrix = X['M']

#設定網路
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#設定ucas-kanade (lk) 光流法
lk_params = dict(winSize = (21, 21), maxLevel = 2,
                 creteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0,01))
feature_params = dict(maxCorner = 100, qualityLevel = 0.1 , minDistance = 10, blockSize = 7)

#車子初始位置
global_x, global_y, global_yaw = 0.0, 0.0, 0.0

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
old_gray = None
p0 = None

trajectory_map = np.zeros((500, 500, 3), dtype=np.uint8)
map_center_x, map_center_y = 250, 250

while True:
    ret, frame = cap.read()
    if not ret : break
    
    frame_undistorted = cv2.undistort(frame, mtx, dist, None, mtx)
    bev_frame = cv2.warpPerspective(frame_undistorted, ipm_matrix, (BEV_Width, BEV_Height))
    frame_gray = cv2.cvtColor(bev_frame, cv2.COLOR_BGR2GRAY)
    
    if p0 is None or len(p0) < 15:
        p0 = cv2.goodFeaturesToTrack(frame_gray, mask = None, **feature_params)
        old_gray = frame_gray.copy()
        continue
    
    p1 ,st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
    
    good_new = p1[st == 1]
    good_old = p0[st == 1]
    
    if len(good_new) >= 4:
        transform_matrix, inliers = cv2.estimateAffinePartial2D(good_new, good_old)
        
        if transform_matrix is not None:
            dx = transform_matrix[0, 2]
            dy = transform_matrix[1, 2]
            d_yaw = math.atan2(transform_matrix[1, 0], transform_matrix[0, 0])
            
            dx_meter = dx * Pixel_To_Meter
            dy_meter = dx * Pixel_To_Meter
            
            global_x += (dx_meter * math.cos(global_yaw) - dy_meter * math.sin(global_yaw))
            global_y += (dx_meter * math.sin(global_yaw) + dy_meter * math.cos(global_yaw))
            
            data = {
                "id" : 0,
                "tx" : float(global_x),
                "ty" : 0.0,
                "tz" : float(global_y),
                "rx" : 0.0,
                "ry" : float(math.degrees(global_yaw)),
                "rz" : 0.0
            }
            sock.sendto(json.dumps(data).encode('utf-8'), (UDP_IP, UDP_PORT))
            
            draw_x = int(map_center_x + global_x * 100)
            draw_y = int(map_center_y - global_y * 100)
            cv2.circle(trajectory_map, (draw_x, draw_y), 2, (0, 255, 0), -1)
            
    
    for i, (new, old) in enumerate(zip(good_new, good_old)):
        a ,b = new.ravel()
        cv2.circle(bev_frame, (int(a), int(b)), 5, (0, 255, 0), -1)
        
    old_gray = frame_gray.copy()
    p0 = good_new.reshape(-1, 1, 2)
    
    cv2.imshow("Bird Eye View", bev_frame)
    cv2.imshow("Path", trajectory_map)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    
cap.release()
cv2.destroyAllWindows()    
    



