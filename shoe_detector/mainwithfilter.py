import cv2
from shoe_detector_detection import track_shoes, ShoeTracker  # import ShoeTracker too!

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access the webcam.")
        return

    # Your current filter area
    x1, y1, x2, y2 = 100, 100, 500, 400

    # Find the center of current filter area
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    # Set new width and height (smaller)
    new_width = (x2 - x1) // 2
    new_height = (y2 - y1) // 2

    # Calculate new smaller box around center
    new_x1 = center_x - new_width // 2
    new_y1 = center_y - new_height // 2
    new_x2 = center_x + new_width // 2
    new_y2 = center_y + new_height // 2

    filter_area = (new_x1, new_y1, new_x2, new_y2)

    # ➡️ Create tracker once here
    tracker = ShoeTracker()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break
        #frame = cv2.resize(frame, (320, 240))

        #tracked_shoes = track_shoes(frame, filter_area=filter_area, tracker=tracker)

        # Slightly resize the full frame smaller
        frame = cv2.resize(frame, (480, 360))  # Only a little smaller!

        # After resizing, get new frame dimensions
        frame_height, frame_width = frame.shape[:2]

        # Redefine your detection filter area (in the middle)
        filter_width = frame_width // 2  # 50% width
        filter_height = frame_height // 2  # 50% height

        center_x = frame_width // 2
        center_y = frame_height // 2

        new_x1 = center_x - filter_width // 2
        new_y1 = center_y - filter_height // 2
        new_x2 = center_x + filter_width // 2
        new_y2 = center_y + filter_height // 2

        filter_area = (new_x1, new_y1, new_x2, new_y2)

        # Then use this resized frame + updated filter_area
        tracked_shoes = track_shoes(frame, filter_area=filter_area, tracker=tracker)

        for shoe in tracked_shoes:
            shoe_x1, shoe_y1, shoe_x2, shoe_y2 = shoe.bbox
            if (shoe_x1 > new_x1 and shoe_y1 > new_y1 and shoe_x2 < new_x2 and shoe_y2 < new_y2):
                print("Foot detected inside the filter area!")

        for shoe in tracked_shoes:
            shoe_x1, shoe_y1, shoe_x2, shoe_y2 = shoe.bbox
            if (shoe_x1 > new_x1 and shoe_y1 > new_y1 and shoe_x2 < new_x2 and shoe_y2 < new_y2):
                cv2.rectangle(frame, (shoe_x1, shoe_y1), (shoe_x2, shoe_y2), (0, 255, 0), 2)
                cv2.putText(frame, "Foot", (shoe_x1, shoe_y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Draw the filter area
        cv2.rectangle(frame, (new_x1, new_y1), (new_x2, new_y2), (255, 0, 0), 2)

        cv2.imshow("Foot Detection", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            cv2.imwrite('captured_frame.jpg', frame)
            print("Captured a frame as 'captured_frame.jpg'")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
