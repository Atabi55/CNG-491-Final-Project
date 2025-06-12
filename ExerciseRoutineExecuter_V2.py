import cv2
from ultralytics import YOLO
import time
from gpiozero import AngularServo
from time import sleep
import sys
import ast

# Function to set the servo angle
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
    
    # YOLO modeli
    model = YOLO("yolov8n.pt")

    # Kamera ayarları
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    
    #baslangıc parametreleri
    tempX = horizontalArray[0]
    tempY = verticalArray[0]
    start = time.time()
    pastStep =  time.time()
    
    # İlk kareyi alarak gerçek çözünürlüğü öğren
    ret, frame = cap.read()
    if not ret:
        raise RuntimeError("Kamera görüntüsü alınamadı.")
    height, width = frame.shape[:2]
    
    
    # Tespit alanı (görüntünün merkezinde küçük bir kutu)
    boxSize = (int)(2800/verticalArray[0])
    box_width, box_height = boxSize, boxSize  # Daha küçük kutu
    center_x, center_y = width // 2, height // 2
    box_x1 = center_x - box_width // 2
    box_y1 = center_y - box_height // 2
    box_x2 = center_x + box_width // 2
    box_y2 = center_y + box_height // 2

    # Servo kontrol değişkenleri
    current_angle = 50
    angle_step = 45
    last_movement_time = 0
    DEBOUNCE_TIME = 1.3

    def is_foot_in_box(foot_x, foot_y):
        return box_x1 <= foot_x <= box_x2 and box_y1 <= foot_y <= box_y2
    moveIt = True
    try:
        while True:
            if moveIt:
            
                ret, frame = cap.read()
                if not ret:
                    break
                boxSize = (int)(2800/verticalArray[0])
                box_width, box_height = boxSize, boxSize  # Dinamik boyutlu kutu
                
                current_time = time.time()

                # Kırmızı tespit kutusunu çiz
                cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (0, 0, 255), 2)

                # Ayak tespiti
                results = model(frame, classes=[0], conf=0.6, imgsz=160)

                for r in results:
                    boxes = r.boxes.xyxy.cpu().numpy()
                    for box in boxes:
                        x1, y1, x2, y2 = map(int, box)
                        foot_x = (x1 + x2) // 2
                        foot_y = y2 - int((y2 - y1) * 0.2)
                        #foot_y = y2

                        if is_foot_in_box(foot_x, foot_y):
                            cv2.circle(frame, (foot_x, foot_y), 10, (0, 255, 0), -1)
                            moveIt = False
                            continue
                            

                #Servo açısını göster
                cv2.putText(frame, f"Servo: {current_angle}deg", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                cv2.imshow("Foot Tracking", frame)
                if cv2.waitKey(1) == ord('q'):
                    break
            else:
                moveIt = True
                #iki adım arası not ediliyor
                thisStep = time.time()
                stepStat.append("%.2f"%(thisStep-pastStep))
                pastStep = thisStep         
                #servo harekete geçiyor
                set_angleVertical(tempY, verticalArray[stepCounter])
                set_angleHorizontal(tempX, horizontalArray[stepCounter])
                tempY = verticalArray[stepCounter]
                tempX = horizontalArray[stepCounter]
                stepCounter += 1
                if(stepCounter == len(verticalArray)):#array bittiyse servo kapa
                    end = time.time()
                    set_angleVertical(tempY, 50)
                    set_angleHorizontal(tempX, 50)
                    cap.release()
                    cv2.destroyAllWindows()
                    return ((end-start)-3)/len(verticalArray), stepStat
                #Servo açısını göster
                cv2.putText(frame, f"Servo: {current_angle}deg", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                cv2.imshow("Foot Tracking", frame)
                if cv2.waitKey(1) == ord('q'):
                    break

    finally:
        set_angleVertical(tempY, 50)
        set_angleHorizontal(tempX, 50)
        cap.release()
        cv2.destroyAllWindows()
    
fileAddress = sys.argv[1]
 
with open(fileAddress, "r") as file:
    line1 = file.readline().strip()
    line2 = file.readline().strip()

vertArray = ast.literal_eval(line1)
horizArray = ast.literal_eval(line2)

msg, stepStat = AI_foot_detection(vertArray, horizArray)
print(stepStat)
print ("%.2f" % msg)
