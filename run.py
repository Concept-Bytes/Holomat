import cv2
import numpy as np
import mediapipe as mp

# Initialize mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.1,
                       min_tracking_confidence=0.1)

mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# Read in M and M2 matrices
M1 = np.load("M1.npy")

width, height = 1920, 1200

while True:
    ret, frame = cap.read()

    # If the frame was not read, exit
    if not ret:
        print("Failed to capture frame")
        break

    # Convert to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Run inference for hand detection
    results = hands.process(rgb_frame)

    # Create an empty image to draw on
    output_image = np.zeros((height, width, 3), np.uint8)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Extract landmark coordinates
            landmark_coords = []
            for landmark in hand_landmarks.landmark:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                landmark_coords.append([x, y])
            
            landmark_coords = np.array(landmark_coords, dtype=np.float32)
            print(f"Original Landmark Coordinates: {landmark_coords}")

            # Apply M1 transformation to landmark coordinates
            transformed_coords = cv2.perspectiveTransform(np.array([landmark_coords]), M1)[0]
            print(f"Transformed Landmark Coordinates: {transformed_coords}")

            # Draw landmarks on the output image
            for i, (x, y) in enumerate(transformed_coords):
                cv2.circle(output_image, (int(x), int(y)), 5, (0, 255, 0), -1)
                cv2.putText(output_image, f'ID:{i}', (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    

    # Display the final image
    cv2.namedWindow("Final Image", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Final Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Final Image", output_image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

