import cv2
import os

current_path = os.path.dirname(os.path.abspath(__file__))

save_image = os.path.join(current_path, "capture_images")
if not os.path.exists(save_image):
    os.makedirs(save_image)


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
count = 0
print('s:capture  q:quit')

while True:
    ret, frame = cap.read()
    if not ret:
        print("can't capture image")
        break

    cv2.imshow('Camera', frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        img_name = os.path.join(save_image, f"calib_{count:02d}.jpg")
        cv2.imwrite(img_name, frame)
        print(f"Success save : {img_name}")
        count += 1

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()