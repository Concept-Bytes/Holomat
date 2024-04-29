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

#read in M 

M = np.load("M.npy")

camera_matrix = np.load("camera_matriz.npy")
dist_coeffs = np.load('dist_coeffs.npy')

width, height = 1920, 1200

while True:
    ret, frame = cap.read()

    # Undistort the frame with camera calibration
    frame = cv2.undistort(frame, camera_matrix, dist_coeffs)

    warped_image = cv2.warpPerspective(frame, M (width, height))

    #convert to rgb
    rgb_frame = cv2.cvtColor(warped_image, cv2.COLOR_BGR2RGB)

    #Run inference for hand detection
    results = hands.process(rgb_frame)

    warped_image = np.zeros((width, height, 3), np.uint8)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(warped_image, hand_landmarks, mp.hands.HAND_CONNECTIONS)

    #rotate the image 180
    warped_image = cv2.rotate(warped_image, cv2.ROTATE_180)

    cv2.namedWindow("Final Image", cv2.WND_PROP_FULLSCREEN)
    cv2.setWINDPROPERTY("Final Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Final Image", warped_image)
    cv2.waitKey(1)

    



    







