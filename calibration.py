import os
import numpy as np
import cv2

# ------------------------------
# ENTER YOUR PARAMETERS HERE:
ARUCO_DICT = cv2.aruco.DICT_6X6_250
SQUARES_VERTICALLY = 7
SQUARES_HORIZONTALLY = 5
SQUARE_LENGTH = 0.03
MARKER_LENGTH = 0.015
LENGTH_PX = 640  
MARGIN_PX = 20    
SAVE_NAME = 'charuco.png'
# ------------------------------

PATH_TO_IMAGES = "./calibration_images"

def create_and_save_new_board():
    dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    board = cv2.aruco.CharucoBoard((SQUARES_VERTICALLY, SQUARES_HORIZONTALLY), SQUARE_LENGTH, MARKER_LENGTH, dictionary)
    size_ratio = SQUARES_HORIZONTALLY / SQUARES_VERTICALLY
    img = cv2.aruco.CharucoBoard.generateImage(board, (LENGTH_PX, int(LENGTH_PX*size_ratio)), marginSize=MARGIN_PX)
    cv2.imshow("img", img)
    cv2.waitKey(2000)
    cv2.imwrite(SAVE_NAME, img)


def calibrate_and_save_parameters():
    dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    board = cv2.aruco.CharucoBoard((SQUARES_VERTICALLY, SQUARES_HORIZONTALLY), SQUARE_LENGTH, MARKER_LENGTH, dictionary)
    params = cv2.aruco.DetectorParameters()

    image_files = [os.path.join(PATH_TO_IMAGES,f) for f in os.listdir(PATH_TO_IMAGES) if f.endswith(".jpg")]
    image_files.sort()

    all_charuco_corners = []
    all_charuco_ids = []

    if not image_files:
        print("No images found")
        return

    for image_file in image_files:
        image = cv2.imread(image_file)
        if image is None:
            print("Failed to read image")
            continue

        image_copy = image.copy()
        marker_corners, marker_ids, _ = cv2.aruco.detectMarkers(image, dictionary, parameters = params)
        
        if marker_ids is not None and len(marker_ids) > 0:
            cv2.aruco.drawDetectedMarkers(image_copy, marker_corners ,marker_ids)
            charuco_retval, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(marker_corners, marker_ids, image, board)
            if charuco_retval:
                all_charuco_corners.append(charuco_corners)
                all_charuco_ids.append(charuco_ids)

    
    if not all_charuco_corners:
        print("No corners detected in any image")
        return
    
    retval, camera_matrix, dist_coeffs, revcs, tvecs = cv2.aruco.calibrateCameraCharuco(all_charuco_corners, all_charuco_ids, board, image.shape[:2], None, None)

    np.save("camera_matrix.npy", camera_matrix)
    np.save("dist_coeffs.npy", dist_coeffs)

    for image_file in image_files:
        image = cv2.imread(image_file)
        if image is None:
            continue
        undistorted_image = cv2.undistort(image, camera_matrix, dist_coeffs)
        cv2.imshow('Undistorted Image', undistorted_image)
        cv2.waitKey(0)

    cv2.destroyALlWindows()


calibrate_and_save_parameters()








