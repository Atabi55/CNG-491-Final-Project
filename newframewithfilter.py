import cv2

# Load Haar Cascade for lower body detection
cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_lowerbody.xml")

# Initialize the webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Get frame dimensions
    height, width, _ = frame.shape

    # Define the middle region of interest (ROI)
    roi_top = int(height * 0.4)  # Start of the middle region (40% from the top)
    roi_bottom = int(height * 0.6)  # End of the middle region (60% from the top)
    roi_left = int(width * 0.3)  # Left boundary (30% from the left)
    roi_right = int(width * 0.7)  # Right boundary (70% from the left)

    # Draw the middle region on the frame for visualization
    cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bottom), (0, 255, 0), 2)

    # Convert to grayscale for detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect objects (e.g., lower body)
    detections = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

    # Process each detection
    for (x, y, w, h) in detections:
        # Shift the bounding box lower by adding an offset
        vertical_shift = int(h * 0.3)  # Shift down by 30% of the box height
        box_height_fraction = 0.3  # Only keep the bottom 30% of the detected box
        new_h = int(h * box_height_fraction)
        new_y = y + vertical_shift + h - new_h  # Shift the box down to the bottom

        # Calculate the center of the adjusted box
        center_x, center_y = x + w // 2, new_y + new_h // 2

        # Check if the box center is within the middle ROI
        if roi_left <= center_x <= roi_right and roi_top <= center_y <= roi_bottom:
            # Draw the bounding box and display "Foot Found"
            cv2.rectangle(frame, (x, new_y), (x + w, new_y + new_h), (255, 0, 0), 2)  # Blue box
            cv2.putText(frame, "Foot Found", (x, new_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # Display the frame
    cv2.imshow("Foot Detection (Middle Filter + Adjusted Box)", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
