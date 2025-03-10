import cv2
from shoe_detector_detection import track_shoes

def main():
    cap = cv2.VideoCapture(0)  # Open webcam

    if not cap.isOpened():
        print("Error: Unable to access the webcam.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        # Perform shoe/foot detection
        tracked_shoes = track_shoes(frame)

        # Print when a shoe/foot is detected
        for shoe in tracked_shoes:
            print("Foot detected!")
            # Optionally, you can log details like bounding box
            # x1, y1, x2, y2 = shoe.bbox
            # print(f"Bounding Box: ({x1}, {y1}), ({x2}, {y2})")

        # Display the frame with detections (optional for visualization)
        for shoe in tracked_shoes:
            x1, y1, x2, y2 = shoe.bbox
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, "Foot", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("Foot Detection", frame)

        # Exit when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
