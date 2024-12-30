import cv2
import numpy as np
import tflite_runtime.interpreter as tflite


MODEL_PATH = "/home/cng491/Downloads/movenet-tflite-singlepose-lightning-tflite-float16-v1/4.tflite"

# TensorFlow Lite Interpreter
interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

# getting indexes of input and output tensors
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# in landmark array, left and right ankles are on 15,16 indexes
LEFT_ANKLE_INDEX = 15
RIGHT_ANKLE_INDEX = 16

def detect_pose(frame):
    # resizing input image to 192x192
    input_shape = input_details[0]['shape']
    input_image = cv2.resize(frame, (input_shape[1], input_shape[2]))#(192, 192, 3).
    input_image = np.expand_dims(input_image, axis=0).astype(np.uint8)#(1, 192, 192, 3)

    # to start model, putting input datas
    interpreter.set_tensor(input_details[0]['index'], input_image)
    interpreter.invoke()

    # getting model output
    keypoints = interpreter.get_tensor(output_details[0]['index'])[0][0]#(1, 1, 17, 3) to (17,3)

    #one batch one pose [0][0]

    return keypoints


cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break


    keypoints = detect_pose(frame)


    left_ankle = keypoints[LEFT_ANKLE_INDEX]
    left_x, left_y, left_confidence = left_ankle


    right_ankle = keypoints[RIGHT_ANKLE_INDEX]
    right_x, right_y, right_confidence = right_ankle


    frame_height, frame_width, _ = frame.shape
    if left_confidence > 0.5:
        cv2.circle(frame, (int(left_x * frame_width), int(left_y * frame_height)), 5, (0, 255, 0), -1)
        cv2.putText(frame, f"Left Ankle: ({left_x:.2f}, {left_y:.2f})", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    if right_confidence > 0.5:
        cv2.circle(frame, (int(right_x * frame_width), int(right_y * frame_height)), 5, (255, 0, 0), -1)
        cv2.putText(frame, f"Right Ankle: ({right_x:.2f}, {right_y:.2f})", 
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)


    cv2.imshow('TensorFlow Lite Foot Detection', frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

