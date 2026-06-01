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

model = YOLO('yolo26n.pt')

while True:
    ret, frame = cap.read()


