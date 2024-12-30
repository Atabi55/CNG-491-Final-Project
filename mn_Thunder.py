import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
import psutil  # Bellek kontrolü için

MODEL_PATH = "/home/cng491/Downloads/movenet_singlepose_thunder.tflite"

interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()


TARGET_INPUT_SIZE = 256
LEFT_ANKLE_INDEX = 15
RIGHT_ANKLE_INDEX = 16

def detect_pose(frame):
    try:
        input_image = cv2.resize(frame, (TARGET_INPUT_SIZE, TARGET_INPUT_SIZE))
        input_image = np.expand_dims(input_image, axis=0).astype(np.int32)

        interpreter.set_tensor(input_details[0]['index'], input_image)
        interpreter.invoke()

        keypoints = interpreter.get_tensor(output_details[0]['index'])[0]
        return keypoints
    except Exception as e:
        print("Hata:", e)
        return None

cap = cv2.VideoCapture(0)
frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % 3 != 0:  # Perform an action every 3 frames
        continue

    # control ram usage
    print("RAM usage:", psutil.virtual_memory().percent, "%")

    keypoints = detect_pose(frame)
    if keypoints is not None:
        left_ankle = keypoints[0][LEFT_ANKLE_INDEX]
        right_ankle = keypoints[0][RIGHT_ANKLE_INDEX]

        left_x, left_y, left_confidence = left_ankle
        right_x, right_y, right_confidence = right_ankle

        frame_height, frame_width, _ = frame.shape
        if left_confidence > 0.5:
            cv2.circle(frame, (int(left_x * frame_width), int(left_y * frame_height)), 5, (0, 255, 0), -1)
        if right_confidence > 0.5:
            cv2.circle(frame, (int(right_x * frame_width), int(right_y * frame_height)), 5, (255, 0, 0), -1)

    cv2.imshow('MoveNet foot detected', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

