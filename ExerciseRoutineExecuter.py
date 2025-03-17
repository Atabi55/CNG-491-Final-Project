import cv2
import mediapipe as mp
import numpy as np
from gpiozero import AngularServo
from time import sleep
import ast
import sys
# Initialize the servo on GPIO pin 14
# min_pulse_width and max_pulse_width may need to be adjusted for your servo
#14, 15


# Function to set the servo angle
def set_angleHorizontal(angle):
    servo1 = AngularServo(14, min_angle=0, max_angle=180, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
    servo1.angle = angle
    sleep(0.5)
    servo1.close()
                
def set_angleVertical(angle):
    servo2 = AngularServo(15, min_angle=0, max_angle=180, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
    servo2.angle = angle
    sleep(0.5)
    servo2.close()
# defining  pose model

def AI_foot_detection(verticalArray, horizontalArray):
    mp_pose = mp.solutions.pose
    stepCounter = 0
    ankleChecker = False
    AREA_WIDTH = 300
    AREA_HEIGHT = 200

    # open web cam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("camera error")
        exit()

    #starting mp model

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("capture error")
                break

            # calculating detection area dynamically, assuming people stay on the center of camera

            frame_height, frame_width, _ = frame.shape
            center_x, center_y = frame_width // 2, frame_height // 2
            top_left_x = center_x - AREA_WIDTH // 2
            top_left_y = center_y - AREA_HEIGHT // 2
            bottom_right_x = center_x + AREA_WIDTH // 2
            bottom_right_y = center_y + AREA_HEIGHT // 2

            # bgr to rgb
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	        #işleme sırasında,ram,process time
            frame_rgb.flags.writeable = False

            # detection
            results = pose.process(frame_rgb)

            # to write on detection i make it true 
            frame.flags.writeable = True

            # masking for unnecessery area
            mask = np.zeros_like(frame)
            mask[top_left_y:bottom_right_y, top_left_x:bottom_right_x] = frame[top_left_y:bottom_right_y, top_left_x:bottom_right_x]
            frame = mask

            # checks foot ankle only in foot detection area
		    
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                # takes coordinates of right and left angles.
                right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE] #oran
                left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]

                # calculating pixel coordiantes
                right_ankle_x = int(right_ankle.x * frame_width)
                right_ankle_y = int(right_ankle.y * frame_height)
                left_ankle_x = int(left_ankle.x * frame_width)
                left_ankle_y = int(left_ankle.y * frame_height)

                # right ankle in detection aree
                if (top_left_x <= right_ankle_x <= bottom_right_x and
                    top_left_y <= right_ankle_y <= bottom_right_y):
                    cv2.circle(frame, (right_ankle_x, right_ankle_y), 5, (255, 0, 0), -1)
                    cv2.putText(frame, f"Right Ankle: ({right_ankle_x}, {right_ankle_y})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                    ankleChecker = True

                # left ankle in detectioın area
                if (top_left_x <= left_ankle_x <= bottom_right_x and
                    top_left_y <= left_ankle_y <= bottom_right_y):
                    cv2.circle(frame, (left_ankle_x, left_ankle_y), 5, (0, 255, 0), -1)
                    cv2.putText(frame, f"Left Ankle: ({left_ankle_x}, {left_ankle_y})", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    ankleChecker = True
                    
                if(ankleChecker == True):
                    print("vert: ",verticalArray[stepCounter]," horz: ", horizontalArray[stepCounter])
                    ankleChecker = False
                    #calling servo functions
                    set_angleVertical(verticalArray[stepCounter])
                    set_angleHorizontal(horizontalArray[stepCounter])
                    stepCounter += 1
                    if(stepCounter == len(verticalArray)):
                        print("sequence complete")
                        cap.release()
                        cv2.destroyAllWindows()
                
            # Draw detection area with a red frame
            cv2.rectangle(frame, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 0, 255), 2)


            cv2.imshow('MediaPipe Foot Detection Area', frame)


            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


    cap.release()
    cv2.destroyAllWindows()
#vertArray = [37, 40, 43, 46, 49, 52, 51, 49, 48, 46, 45, 42, 49, 46, 43, 40, 46, 42, 48, 54, 60, 55, 51, 46, 42, 37, 40, 43, 46, 49, 52, 51, 49, 48, 46, 45, 42, 49, 46, 43, 40, 46, 42, 48, 54, 60]
print("hello mars")
if len(sys.argv) < 2:
    print("Usage: python read_array.py <filename>")
    sys.exit(1)

fileAddress = sys.argv[1]
 
with open(fileAddress, "r") as file:
    line1 = file.readline().strip()
    line2 = file.readline().strip()

vertArray = ast.literal_eval(line1)
horizArray = ast.literal_eval(line2)

AI_foot_detection(vertArray, horizArray)
