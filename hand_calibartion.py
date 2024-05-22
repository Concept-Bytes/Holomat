import cv2
import numpy as np
import mediapipe as mp

# Initialize mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=1,  # Assuming you touch the target with one hand
                       min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)

mp_drawing = mp.solutions.drawing_utils

# Camera capture setup
cap = cv2.VideoCapture(0)

# Projector width and height
width, height = 1920, 1200

# Define target points for calibration (projected positions)
target_points = [(100, 100), (1820, 100), (1820, 1100), (100, 1100)]
calibration_points = []

# Function to capture hand landmarks at target points
def capture_hand_landmarks():
    global calibration_points
    calibration_points.clear()
    for i, point in enumerate(target_points):
        while True:
            calibration_image = np.zeros((height, width, 3), dtype=np.uint8)
            cv2.circle(calibration_image, point, 20, (0, 0, 255), -1)
            cv2.putText(calibration_image, f'Point {i+1}', (point[0] + 30, point[1] - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Show the calibration image in full screen
            cv2.namedWindow("Calibration Targets", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("Calibration Targets", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow("Calibration Targets", calibration_image)

            ret, frame = cap.read()
            if not ret:
                continue

            # Convert to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Run hand detection
            results = hands.process(rgb_frame)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            cv2.imshow("Camera View", frame)

            # Wait for user to press Enter
            key = cv2.waitKey(1)
            if key == 13:  # Enter key
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Assuming we use the index finger tip landmark (landmark 8)
                        x = int(hand_landmarks.landmark[8].x * frame.shape[1])
                        y = int(hand_landmarks.landmark[8].y * frame.shape[0])
                        calibration_points.append((x, y))
                        print(f"Captured hand landmark for Point {i+1} at: ({x}, {y})")
                        break
                else:
                    print("Error: No hand landmark detected. Please try again.")
                    continue
                break

# Capture hand landmarks at target points
capture_hand_landmarks()
cv2.destroyAllWindows()

# Ensure the captured points are in the correct order
if len(calibration_points) == 4:
    target_points_np = np.array(target_points, dtype=np.float32)
    calibration_points_np = np.array(calibration_points, dtype=np.float32)
    M1, _ = cv2.findHomography(calibration_points_np, target_points_np)
    np.save("M1.npy", M1)
    print("Calibration successful. M1 matrix saved.")
else:
    print("Error: Not all calibration points were captured.")
