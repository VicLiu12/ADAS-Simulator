import numpy as np
import cv2
import glob
import os
import sys

CheckBoard = (8, 5)
SquareSize = 0.03

accuracy = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((CheckBoard[0] * CheckBoard[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CheckBoard[0], 0:CheckBoard[1]].T.reshape(-1, 2) * SquareSize

objpoints = []
imgpoints = []

script_path = os.path.dirname(os.path.abspath(__file__))
image_folder= os.path.join(script_path, 'capture_images', '*.jpg')
images = glob.glob(image_folder)

print(f"Total {len(images)} images")
if len(images) == 0:
    print('Read images ERROR')
    sys.exit()

count = 0

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(gray, CheckBoard, None)

    if ret == True:
        count += 1
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), accuracy)
        imgpoints.append(corners2)

        cv2.drawChessboardCorners(img, CheckBoard, corners2, ret)
        cv2.imshow('Detected_Corners', img)
        cv2.waitKey(100)

cv2.destroyAllWindows()

print(f"\nDetect Success. {len(images)} images in total")
if count < 10:
    print('Need detect more photos to improve accuracy')

#print('calculate camera parameter')
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

print('\nCamera Calibrate Complete')
print('Camera matrix : \n', mtx)
print('Distortion Coefficients : ', dist)

save_path = os.path.join(script_path, 'camera_params.npz')
np.savez(save_path, mtx=mtx, dist=dist)
print('\nnpz file saves')
