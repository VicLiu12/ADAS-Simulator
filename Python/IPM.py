import cv2
import numpy as np
import os 

current_path = os.path.dirname(__file__)
file_path = os.path.join(current_path, 'camera_params.npz')

if not os.path.exists(file_path):
    print ('File Load ERROR')
    exit()

with np.load(file_path) as X:
    mtx, dist = X['mtx'], X['dist']

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)

BEV_Width, BEV_Height = 400, 500
Markers_Pixels = 150

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

print('s --> save')
print('q --> quit')

homography_matrix = None




