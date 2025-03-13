import cv2 as cv

video = cv.VideoCapture(0)

if not video.isOpened():
    print("Cannot find the camera")
    exit()
frame_width = int(video.get(cv.CAP_PROP_FRAME_WIDTH))
frame_height = int(video.get(cv.CAP_PROP_FRAME_HEIGHT))

fourcc = cv.VideoWriter_fourcc(*'mp4v')
out = cv.VideoWriter('video_output.mp4', fourcc, 20.0,(frame_width,frame_height))
