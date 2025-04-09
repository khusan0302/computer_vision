import cv2 as cv
import numpy as np

# 체스보드 정보
pattern_size = (7, 10)
square_size = 1.0

# 내부 코너 기준 체스보드의 3D 좌표 생성
objp = np.zeros((np.prod(pattern_size), 3), np.float32)
objp[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
objp *= square_size

# 피라미드의 3D 좌표 설정
pyramid_base = np.array([
    [0, 0, 0],
    [6, 0, 0],
    [6, 6, 0],
    [0, 6, 0]
], dtype=np.float32)
pyramid_top = np.array([[3, 3, -5]], dtype=np.float32)

# 카메라 캘리브레이션 결과
K = np.array([[619.8880278431839, 0.0, 479.21308178014766],
              [0.0, 612.9917053473229, 312.7732748752825],
              [0.0, 0.0, 1.0]])
dist_coeff = np.array([-0.6168214215341291, 0.8249170705983586,
                       -0.008869648423715328, -0.021134863957153003,
                       -0.505503026009792])

# 비디오 열기
cap = cv.VideoCapture('video_output.avi')
if not cap.isOpened():
    print("영상 열기 실패")
    exit()

# 저장용 비디오 설정
frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv.CAP_PROP_FPS)

fourcc = cv.VideoWriter_fourcc(*'XVID')
out = cv.VideoWriter('ar_pyramid.avi', fourcc, fps, (frame_width, frame_height))

saved_image = False  # 캡쳐 여부 확인

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    found, corners = cv.findChessboardCorners(gray, pattern_size)

    if found:
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1),
                                   criteria=(cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001))

        ret, rvec, tvec = cv.solvePnP(objp, corners2, K, dist_coeff)

        base_2d, _ = cv.projectPoints(pyramid_base, rvec, tvec, K, dist_coeff)
        top_2d, _ = cv.projectPoints(pyramid_top, rvec, tvec, K, dist_coeff)

        base_2d = np.int32(base_2d).reshape(-1, 2)
        top_2d = np.int32(top_2d).reshape(-1, 2)[0]

        cv.polylines(frame, [base_2d], isClosed=True, color=(0, 255, 0), thickness=2)
        for pt in base_2d:
            cv.line(frame, tuple(top_2d), tuple(pt), (0, 0, 255), 2)

        R, _ = cv.Rodrigues(rvec)
        camera_position = (-R.T @ tvec).flatten()
        info = f'Camera XYZ: [{camera_position[0]:.2f}, {camera_position[1]:.2f}, {camera_position[2]:.2f}]'
        cv.putText(frame, info, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # 이미지 저장 (한 번만 저장)
        if not saved_image:
            cv.imwrite("image.png", frame)
            saved_image = True

    out.write(frame)
    cv.imshow('AR Pyramid', frame)
    if cv.waitKey(10) == 27:
        break

cap.release()
out.release()
cv.destroyAllWindows()
