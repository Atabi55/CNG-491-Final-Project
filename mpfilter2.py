import cv2
import mediapipe as mp
import numpy as np

# defining  pose model


mp_pose = mp.solutions.pose

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

            # left ankle in detectioın area
            if (top_left_x <= left_ankle_x <= bottom_right_x and
                top_left_y <= left_ankle_y <= bottom_right_y):
                cv2.circle(frame, (left_ankle_x, left_ankle_y), 5, (0, 255, 0), -1)
                cv2.putText(frame, f"Left Ankle: ({left_ankle_x}, {left_ankle_y})", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Draw detection area with a red frame
        cv2.rectangle(frame, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 0, 255), 2)


        cv2.imshow('MediaPipe Foot Detection Area', frame)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


cap.release()
cv2.destroyAllWindows()

