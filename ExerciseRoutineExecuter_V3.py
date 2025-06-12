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
        sleep(0.2)
    servo1.close()

def set_angleVertical(pastAngle, angle):
    servo2 = AngularServo(15, min_angle=0, max_angle=180, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
    for ang in range(pastAngle, angle, 5):
        servo2.angle = ang
        sleep(0.2)
    servo2.close()

def AI_foot_detection(verticalArray, horizontalArray):
    stepCounter = 0
    stepStat = []

    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    tempX = horizontalArray[0]
    tempY = verticalArray[0]
    start = time.time()
    pastStep = time.time()

    ret, frame = cap.read()
    if not ret:
        raise RuntimeError("Kamera görüntüsü alınamadı.")
    height, width = frame.shape[:2]

    boxSize = 40
    center_x, center_y = width // 2, height // 2
    box_x1 = center_x - boxSize // 2
    box_y1 = center_y - boxSize // 2
    box_x2 = center_x + boxSize // 2
    box_y2 = center_y + boxSize // 2

    moveIt = True
    try:
        while True:
            if moveIt:
                ret, frame = cap.read()
                if not ret:
                    break

                roi = frame[box_y1:box_y2, box_x1:box_x2]

                # Inference sadece ROI'de
                results = model(roi, classes=[0], conf=0.6, imgsz=160)

                for r in results:
                    boxes = r.boxes.xyxy.cpu().numpy()
                    for box in boxes:
                        x1, y1, x2, y2 = map(int, box)
                        # ROI içindeki koordinatları orijinal frame'e taşı
                        foot_x = box_x1 + (x1 + x2) // 2
                        foot_y = box_y1 + y2 - int((y2 - y1) * 0.2)

                        cv2.circle(frame, (foot_x, foot_y), 10, (0, 255, 0), -1)
                        moveIt = False
                        break

                cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (0, 0, 255), 2)
                cv2.putText(frame, f"Servo: {tempX}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

                cv2.imshow("Foot Tracking", frame)
                if cv2.waitKey(1) == ord('q'):
                    break
            else:
                moveIt = True
                thisStep = time.time()
                stepStat.append(float("%.2f" % (thisStep - pastStep)))
                pastStep = thisStep

                set_angleVertical(tempY, verticalArray[stepCounter])
                set_angleHorizontal(tempX, horizontalArray[stepCounter])
                tempY = verticalArray[stepCounter]
                tempX = horizontalArray[stepCounter]
                stepCounter += 1

                if stepCounter == len(verticalArray):
                    end = time.time()
                    set_angleVertical(tempY, 50)
                    set_angleHorizontal(tempX, 50)
                    cap.release()
                    cv2.destroyAllWindows()
                    stepStat[0] = stepStat[0] - 3
                    return ((end - start) - 3) / len(verticalArray), stepStat

    finally:
        set_angleVertical(tempY, 50)
        set_angleHorizontal(tempX, 50)
        cap.release()
        cv2.destroyAllWindows()

# Argümandan veri okuma
fileAddress = sys.argv[1]
with open(fileAddress, "r") as file:
    line1 = file.readline().strip()
    line2 = file.readline().strip()

vertArray = ast.literal_eval(line1)
horizArray = ast.literal_eval(line2)

msg, stepStat = AI_foot_detection(vertArray, horizArray)
print(stepStat)
print("%.2f" % msg)
