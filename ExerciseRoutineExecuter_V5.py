#best

import cv2
from ultralytics import YOLO
import time
from gpiozero import AngularServo
from time import sleep
import sys
import ast

def set_angleHorizontal(pastAngle, angle):
    servo1 = AngularServo(14, min_angle=0, max_angle=180, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
    for ang in range(pastAngle, angle, 5):
        servo1.angle = ang
        sleep(0.05)
    servo1.close()

def set_angleVertical(pastAngle, angle):
    servo2 = AngularServo(15, min_angle=0, max_angle=180, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
    for ang in range(pastAngle, angle, 5):
        servo2.angle = ang
        sleep(0.05)
    servo2.close()

def AI_foot_detection(verticalArray, horizontalArray):
    stepCounter = 1
    stepStat = []

    model = YOLO("yolov8n.pt")

    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    
    #position servo
    tempX = horizontalArray[0]
    tempY = verticalArray[0]
    set_angleVertical(tempY, verticalArray[0])
    set_angleHorizontal(tempX, horizontalArray[0])
    
    #start= None
    start = time.time()
    pastStep = time.time()

    ret, frame = cap.read()
    if not ret:
        raise RuntimeError("Kamera görüntüsü alınamadı.")
    height, width = frame.shape[:2]

    center_x, center_y = width // 2, height // 2
    boxSize = 60
    box_width, box_height = boxSize, boxSize
    current_angle = 50

    moveIt = True
    waiting = False
    cooldown_start_time = 0
    cooldown = 0.1  #saniye
    
    

    def is_foot_in_box(foot_x, foot_y):
        box_x1 = center_x - box_width // 2
        box_y1 = center_y - box_height // 2
        box_x2 = center_x + box_width // 2
        box_y2 = center_y + box_height // 2
        return box_x1 <= foot_x <= box_x2 and box_y1 <= foot_y <= box_y2

    try:
        prev_frame_time = time.time()
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            new_frame_time = time.time()
            fps = 1 / (new_frame_time - prev_frame_time)
            prev_frame_time = new_frame_time

            boxSize = int(2800 / verticalArray[0])
            box_width, box_height = boxSize, boxSize
            roi_margin = box_width * 3
            roi_x1 = max(0, center_x - roi_margin // 2)
            roi_x2 = min(width, center_x + roi_margin // 2)

            roi_frame = frame[:, roi_x1:roi_x2]
            results = model(roi_frame, classes=[0], conf=0.6, imgsz=160)

            if moveIt and not waiting:
                for r in results:
                    boxes = r.boxes.xyxy.cpu().numpy()
                    for box in boxes:
                        x1, y1, x2, y2 = map(int, box)
                        foot_x = (x1 + x2) // 2 + roi_x1
                        foot_y = y2 - int((y2 - y1) * 0.2)

                        if is_foot_in_box(foot_x, foot_y):
                            moveIt = False
                            break

            elif not moveIt and not waiting:
                # Servo hareketi başlatıldıktan sonra beklemeye gir
                waiting = True
                thisStep = time.time()
                stepStat.append(round((thisStep - pastStep),2))
                pastStep = thisStep

                set_angleVertical(tempY, verticalArray[stepCounter])
                set_angleHorizontal(tempX, horizontalArray[stepCounter])
                tempY = verticalArray[stepCounter]
                tempX = horizontalArray[stepCounter]
                #if stepCounter == 1 and start is None:#ilk geçen süreyi kaldırmka
                #    start = start.time()#ddddd
                stepCounter += 1

                if stepCounter == len(verticalArray):
                    end = time.time()
                    set_angleVertical(tempY, 50)
                    set_angleHorizontal(tempX, 50)
                    cap.release()
                    cv2.destroyAllWindows()
                    stepStat[0] -= 3
                    stepStat[0] = round(stepStat[0],2)
                    return ((end - start) - 3) / len(verticalArray), stepStat, round((end-start),2)

                cooldown_start_time = time.time()

            elif waiting:
                if time.time() - cooldown_start_time >= cooldown:
                    waiting = False
                    moveIt = True

            # Maskeleme için görüntü kopyası
            masked_frame = frame.copy()
            masked_frame[:, :roi_x1] = 0
            masked_frame[:, roi_x2:] = 0

            # ROI çiz
            cv2.rectangle(masked_frame, (roi_x1, 0), (roi_x2, height), (255, 255, 0), 2)

            # Kırmızı kutu çiz
            box_x1 = center_x - box_width // 2
            box_y1 = center_y - box_height // 2
            box_x2 = center_x + box_width // 2
            box_y2 = center_y + box_height // 2
            cv2.rectangle(masked_frame, (box_x1, box_y1), (box_x2, box_y2), (0, 0, 255), 2)

            # FPS ve servo açısı
            cv2.putText(masked_frame, f"Servo: {current_angle}deg", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(masked_frame, f"FPS: {int(fps)}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            cv2.imshow("Foot Tracking", masked_frame)
            if cv2.waitKey(1) == ord('q'):
                break

    finally:
        set_angleVertical(tempY, 50)
        set_angleHorizontal(tempX, 50)
        cap.release()
        cv2.destroyAllWindows()

# Dosya oku
fileAddress = sys.argv[1]
with open(fileAddress, "r") as file:
    line1 = file.readline().strip()
    line2 = file.readline().strip()

vertArray = ast.literal_eval(line1)
horizArray = ast.literal_eval(line2)

msg, stepStat, duration = AI_foot_detection(vertArray, horizArray)
print(duration)
print(stepStat)
print("%.2f" % msg)


