import cv2
import numpy as np
import socket
import json

with np.load('camera_params.npz') as X:
    mtx, dist = X['mtx'], X['dist']

Marker_Size = 0.05

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)

Mark_3D_Edges = np.array([
    [-Marker_Size / 2, Marker_Size / 2, 0],
    [Marker_Size / 2, Marker_Size / 2, 0],
    [Marker_Size / 2, -Marker_Size / 2, 0],
    [-Marker_Size / 2, -Marker_Size / 2, 0]
], dtype=np.float32)

# 之後用到遙控車時要做修改
UDP_IP = "127.0.0.1" 
UDP_PORT = 5050
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
print(f"Detect Start, Network Coordinates send to {UDP_IP} : {UDP_PORT}")
print("Press q quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    corners, ids, rejected = detector.detectMarkers(gray)

    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        
        for i in range(len(ids)):
            ret, rvec, tvec = cv2.solvePnP(
                Mark_3D_Edges, corners[i][0], mtx, dist, flags = cv2.SOLVEPNP_IPPE_SQUARE
            )

            if ret:
                cv2.drawFrameAxes(frame, mtx, dist, rvec, tvec, Marker_Size)

                data = {
                    "id" : int(ids[i][0]),
                    "tx" : float(tvec[0][0]),
                    "ty" : float(tvec[1][0]),
                    "tz" : float(tvec[2][0]),
                    "rx" : float(rvec[0][0]),
                    "ry" : float(rvec[1][0]),
                    "rz" : float(rvec[2][0]),
                }

                sock.sendto(json.dumps(data).encode('utf-8'), (UDP_IP, UDP_PORT))

                print(f"Label ID : {data['id']}  Distance : {data['tz']:.2f} meters")
    
    cv2.imshow('ArUco Tracker', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

