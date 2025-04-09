import cv2 as cv
import numpy as np

# Chessboard settings
pattern_size = (7, 10)  # number of inner corners (columns x rows)
square_size = 1.0       # size of a square (any unit)

# Prepare object points
objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2) * square_size

objpoints = []  # 3D points in real world
imgpoints = []  # 2D points in image plane

# Open video
cap = cv.VideoCapture('video_output.avi')
if not cap.isOpened():
    print("Failed to open video.")
    exit()

success, frame = cap.read()
if not success:
    print("Failed to read the first frame.")
    exit()

# Output video setup
height, width = frame.shape[:2]
fourcc = cv.VideoWriter_fourcc(*'XVID')
out = cv.VideoWriter('calibrated.avi', fourcc, 20.0, (width, height))

frame_index = 0
while success:
    if frame_index % 5 == 0:  # process every 10th frame
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        found, corners = cv.findChessboardCorners(gray, pattern_size, None)

        if found:
            corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1),
                                       criteria=(cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001))
            objpoints.append(objp)
            imgpoints.append(corners2)
            cv.drawChessboardCorners(frame, pattern_size, corners2, found)

    out.write(frame)
    cv.imshow('Chessboard Detection', frame)
    if cv.waitKey(10) == 27:
        break

    success, frame = cap.read()
    frame_index += 1

cap.release()
out.release()
cv.destroyAllWindows()

num_valid = len(objpoints)
print(f"\nTotal {num_valid} valid frames with detected chessboard corners.")

if num_valid < 10:
    print("Not enough valid frames for calibration. Provide more varied views.")
else:
    try:
        print("Running calibrateCamera...")
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv.calibrateCamera(
            objpoints, imgpoints, gray.shape[::-1], None, None)

        print("Calculating reprojection error...")
        total_error = 0
        for i in range(num_valid):
            projected, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], camera_matrix, dist_coeffs)
            error = cv.norm(imgpoints[i], projected, cv.NORM_L2) / len(projected)
            total_error += error

        rmse = total_error / num_valid
        fx, fy = camera_matrix[0, 0], camera_matrix[1, 1]
        cx, cy = camera_matrix[0, 2], camera_matrix[1, 2]

        # Display results
        print("\n## Camera Calibration Results")
        print(f"* Number of applied frames = {num_valid}")
        print(f"* RMS error = {rmse:.6f}")
        print(f"* Camera matrix (K) =")
        print(f"[{camera_matrix[0,0]}, {camera_matrix[0,1]}, {camera_matrix[0,2]}]")
        print(f"[{camera_matrix[1,0]}, {camera_matrix[1,1]}, {camera_matrix[1,2]}]")
        print(f"[{camera_matrix[2,0]}, {camera_matrix[2,1]}, {camera_matrix[2,2]}]")
        print("* Distortion coefficients (k1, k2, p1, p2, k3) =")
        print(dist_coeffs.ravel().tolist())

        # Save to txt
        with open("calibration_result.txt", "w") as f:
            f.write("## Camera Calibration Results\n")
            f.write(f"* Number of applied frames = {num_valid}\n")
            f.write(f"* RMS error = {rmse:.6f}\n")
            f.write("* Camera matrix (K) =\n")
            f.write(f"[{camera_matrix[0,0]}, {camera_matrix[0,1]}, {camera_matrix[0,2]}]\n")
            f.write(f"[{camera_matrix[1,0]}, {camera_matrix[1,1]}, {camera_matrix[1,2]}]\n")
            f.write(f"[{camera_matrix[2,0]}, {camera_matrix[2,1]}, {camera_matrix[2,2]}]\n")
            f.write("* Distortion coefficients (k1, k2, p1, p2, k3) =\n")
            f.write(str(dist_coeffs.ravel().tolist()) + "\n")
            f.write(f"* Focal Length: fx = {fx:.3f}, fy = {fy:.3f}\n")
            f.write(f"* Principal Point: cx = {cx:.3f}, cy = {cy:.3f}\n")

    except Exception as e:
        print("Error during calibration:", e)
