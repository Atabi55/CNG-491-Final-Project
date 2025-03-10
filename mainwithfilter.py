import cv2
from shoe_detector_detection import track_shoes

def main():
    cap = cv2.VideoCapture(0)  # Open webcam

    if not cap.isOpened():
        print("Error: Unable to access the webcam.")
        return

    # Define the filter area (x1, y1, x2, y2)
    filter_area = (100, 100, 500, 400)  # Example coordinates for the rectangle
    x1, y1, x2, y2 = filter_area

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        # Perform shoe/foot detection
        tracked_shoes = track_shoes(frame)

        # Print when a shoe/foot is detected
        for shoe in tracked_shoes:
            # Check if the detected foot is inside the filter area
            shoe_x1, shoe_y1, shoe_x2, shoe_y2 = shoe.bbox
            if (shoe_x1 > x1 and shoe_y1 > y1 and shoe_x2 < x2 and shoe_y2 < y2):
                print("Foot detected inside the filter area!")
                # Optionally, you can log details like bounding box
                # print(f"Bounding Box: ({shoe_x1}, {shoe_y1}), ({shoe_x2}, {shoe_y2})")

        # Display the frame with detections (optional for visualization)
        for shoe in tracked_shoes:
            shoe_x1, shoe_y1, shoe_x2, shoe_y2 = shoe.bbox
            # Check if the foot is inside the filter area before drawing
            if (shoe_x1 > x1 and shoe_y1 > y1 and shoe_x2 < x2 and shoe_y2 < y2):
                cv2.rectangle(frame, (shoe_x1, shoe_y1), (shoe_x2, shoe_y2), (0, 255, 0), 2)
                cv2.putText(frame, "Foot", (shoe_x1, shoe_y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Draw the filter area rectangle
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Blue rectangle for filter area

        # Show the frame with detections
        cv2.imshow("Foot Detection", frame)

        # Check if the window was closed or 'q' was pressed
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):  # Check if 'c' key is pressed to capture a frame
            cv2.imwrite('captured_frame.jpg', frame)
            print("Captured a frame as 'captured_frame.jpg'")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
