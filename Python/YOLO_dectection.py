import cv2
import numpy as np 
import os
import math
from ultralytics import YOLO

if not os.path.exists('camera_params.npz') or not os.path.exists('ipm_matrix.npz'):
    print('npz load ERROR')
    exit()
    
with np.load('camera_params.npz') as X:
    mtx, dist = X['mtx'], X['dist']
with np.load('ipm_matrix.npz') as X:
    ipm_matrix = X['M']

Marker_Pixels = 150
Marker_Real_Size = 0.1
Pixel_To_Meter = Marker_Real_Size / Marker_Pixels

BEV_Width, BEV_Height = 400, 500

Camera_BEV_X = BEV_Width / 2
Camera_BEV_Y = BEV_Height

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

model = YOLO('yolo26n.pt')




