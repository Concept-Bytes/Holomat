import cv2
import numpy as np
import time

#read in camera calibration
camera_matrix = np.load("camera_matrix.npy")
dist_coeffs = np.load("dist_coeffs.npy")

#set up video capture
cap = cv2.VideoCapture(0)

#projector width and height
width = 1920
height = 1200

# create a black 1920x1200 image with a red rectangle frame border of 20 pixels
calibration_image = np.zeros((height, width, 3), dtype = np.uint8)
calibration_image = cv2.rectangle(calibration_image, (20,20), (width-20, height-20), (0,255,0),20)

cv2.imshow("Calibration Image", calibration_image)
cv2.waitKey(0)

# display the image full screen on the monitor
cv2.namedWindow("Calibration Frame", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Calibration Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.imshow("Calibration Frame", calibration_image)
cv2.waitKey(0)
time.sleep(5)
success, image = cap.read()

#show the captured image
cv2.imshow("Captured image", image)
cv2.waitKey(0)

# save the image
cv2.imwrite('calibration_frame.jpg', image)  # Save the result


# image = cv2.imread('./calibration_frame.jpg')

#grayscale image
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
threshold_value = 235 #try different thresholds

#Apply the Threshold
_, thresholded_image = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)

thresholded_image = thresholded_image.astype('uint8')

# #show the image
# cv2.imshow("Thresholded Image", thresholded_image)
# cv2.waitKey(0)

#find all the contours in the image
contours, _ = cv2.findContours(thresholded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#Find the largest contour based on area
largest_contour = max(contours, key=cv2.contourArea)

#draw the largest contour
cv2.drawContours(image, [largest_contour], -1, (0, 0, 255), 2)

# #show the image
# cv2.imshow("Largest Contour", image)
# cv2.waitKey(0)

# Approximate the contour to a polygon
epsilon = 0.02 * cv2.arcLength(largest_contour, True)
projection_approx_corners = cv2.approxPolyDP(largest_contour, epsilon,True)

if len(projection_approx_corners) ==4:
    for i, corner in enumerate(projection_approx_corners):
        x,y = corner.ravel()
        print(f"Corner {i + 1}: (x={x}, y={y})")
        #draw the corner
        cv2.circle(image, (x,y), 5, ((0,0,255)), -1)
        

else:
    print("Detected shape is not a quadrilateral. Adjust epison value or check contour")


#show the image
cv2.imshow("Corners", image)
cv2.waitKey(0)

#Ensure there are exactly 4 coords

if len(projection_approx_corners) ==4:

    #Flatten the corner points array and convert it to float 32
    points = projection_approx_corners.reshape((4,2)).astype(np.float32)

    #Sort the points according to their x-coords left to right
    points_sorted = points[np.argsort(points[:,0]), :]

    #Separate the points into top and bottom using y coords
    top_points = points_sorted[:2, :]
    bottom_points = points_sorted[2:,:]

    #Sort the top points from left to right
    top_points = top_points[np.argsort(top_points[:, 1]), :]
    #Sort the bottom points from left to right
    bottom_points = bottom_points[np.argsort(bottom_points[:, 1]), :]

    #Reconstruct the ordered rectangle (top-left, top-right, bottom-right, bottom-left)
    ordered_points = np.vstack([top_points, bottom_points[::-1]])

    #define the destination points

    dst_points = np.array([
        [0,0],
        [0,height-1],
        [width-1,height-1],
        [width - 1, 0]
    ], dtype = "float32")

    M = cv2.getPerspectiveTransform(ordered_points, dst_points)

    warped_image = cv2.warpPerspective(image, M, (width, height))

    cv2.imshow("warped Image", warped_image)

    cv2.waitKey(0)

else:
    print("Shape doesn't have 4 corners")

np.save("M.npy", M)




