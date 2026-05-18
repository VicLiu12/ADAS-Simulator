import cv2
import os

#取得此python檔案的路徑
current_path = os.path.dirname(os.path.abspath(__file__))

#新增資料夾
save_image = os.path.join(current_path, "capture_images")
if not os.path.exists(save_image):
    os.makedirs(save_image)

#開啟攝影機
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
count = 0
print('s:capture  q:quit')


while True:
    ret, frame = cap.read()   #ret -> Return Value 是否有讀取到畫面
    if not ret:
        print("can't capture image")
        break

    cv2.imshow('Camera', frame)  #顯示畫面
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        img_name = os.path.join(save_image, f"calib_{count:02d}.jpg")
        cv2.imwrite(img_name, frame)  #儲存照片
        print(f"Success save : {img_name}")
        count += 1

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()