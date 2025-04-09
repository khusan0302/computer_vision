import cv2 as cv
import numpy as np

# Calibration results
K = np.array([
    [619.8880278431839, 0.0, 479.21308178014766],
    [0.0, 612.9917053473229, 312.7732748752825],
    [0.0, 0.0, 1.0]
])
dist_coeff = np.array([
    -0.6168214215341291, 0.8249170705983586,
    -0.008869648423715328, -0.021134863957153003,
    -0.505503026009792
])

# Open video
video_file = 'video_output.avi'
cap = cv.VideoCapture(video_file)
if not cap.isOpened():
    print("Failed to open video file.")
    exit()

# Read first frame for comparison image
ret, frame = cap.read()
if not ret:
    print("Failed to read the first frame.")
    exit()

height, width = frame.shape[:2]
map1, map2 = cv.initUndistortRectifyMap(K, dist_coeff, None, K, (width, height), cv.CV_32FC1)
undistorted_first = cv.remap(frame, map1, map2, interpolation=cv.INTER_LINEAR)

# Add labels
before = frame.copy()
after = undistorted_first.copy()
cv.putText(before, "Before", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
cv.putText(after, "After", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

# Concatenate and save side-by-side image
comparison = cv.hconcat([before, after])
cv.imwrite("distortion_comparison.jpg", comparison)
print("Saved comparison image as distortion_comparison.jpg")

# Prepare output video
cap.set(cv.CAP_PROP_POS_FRAMES, 0)
fourcc = cv.VideoWriter_fourcc(*'XVID')
out = cv.VideoWriter('undistorted_output.avi', fourcc, 20.0, (width, height))

# Distortion correction
while True:
    ret, frame = cap.read()
    if not ret:
        break

    undistorted = cv.remap(frame, map1, map2, interpolation=cv.INTER_LINEAR)
    cv.putText(undistorted, "Rectified", (10, 25), cv.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0), 1)

    out.write(undistorted)
    cv.imshow('Undistorted Video', undistorted)

    if cv.waitKey(10) == 27:
        break

cap.release()
out.release()
cv.destroyAllWindows()
