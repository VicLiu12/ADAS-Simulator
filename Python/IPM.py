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

while True:
    ret, frame = cap.read()
    if not ret: break

    frame_undistorted = cv2.undistort(frame, mtx, dist, None, mtx)
    gray = cv2.cvtColor(frame_undistorted, cv2.COLOR_BGR2GRAY)

    corners, ids, rejected = detector.detectMarkers(gray)

    if ids is not None and len(ids) > 0:
        cv2.aruco.drawDetectedMarkers(frame_undistorted, corners, ids)

        pts_src = np.array(corners[0][0], dtype="float32")

        offset_x = (BEV_Width - Markers_Pixels) // 2
        offset_y = BEV_Height -Markers_Pixels -50

        pts_dst = np.array([
            #左上
            [offset_x, offset_y],
            #右上
            [offset_x + Markers_Pixels, offset_y],
            #右下
            [offset_x + Markers_Pixels, offset_y + Markers_Pixels],
            #左下
            [offset_x, offset_y + Markers_Pixels]
        ], dtype="float32")


        homography_matrix = cv2.getPerspectiveTransform(pts_src, pts_dst)
    
    cv2.imshow("Front View", frame_undistorted)

    if homography_matrix is not None:
        bev = cv2.warpPerspective(frame_undistorted, homography_matrix, (BEV_Width, BEV_Height))
        cv2.imshow("Bird EYE", bev)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s') and homography_matrix is not None:
        save_path = os.path.join(current_path, 'ipm.npz')
        np.savez(save_path, M=homography_matrix)
        print('Save ipm matrix')
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


