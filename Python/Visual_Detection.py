import cv2
import numpy as np
import socket
import json
import os
import math

#參數設定
UDP_IP = "127.0.0.1"
UNP_PORT = 5052

Marker_Pixels = 150
Marker_Real_Size = 0.1
Poxel_To_Meter = Marker_Real_Size / Marker_Pixels

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
globa_x, global_y, global_yaw = 0.0, 0.0, 0.0

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
old_gray = None
p0 = None

trajectory_map = np.zeros((500, 500, 3), dtype=np.uint8)
map_center_x, map_center_y = 250, 250




