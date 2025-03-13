import cv2 as cv
import time

video = cv.VideoCapture(0)

if not video.isOpened():
    print("Cannot find the camera")
    exit()
frame_width = int(video.get(cv.CAP_PROP_FRAME_WIDTH))
frame_height = int(video.get(cv.CAP_PROP_FRAME_HEIGHT))

fourcc = cv.VideoWriter_fourcc(*'mp4v')
out = cv.VideoWriter('video_output.mp4', fourcc, 20.0,(frame_width,frame_height))

recording = False
paused = False 
mirroring = False 
start_time = 0
elapsed_time = 0
blink = False
last_blink_time = 0

while True:
    ret, frame = video.read()
    if not ret:
        print("Cannot read frame from camera")
        break
    
    if mirroring:
        frame = cv.flip(frame, 1)
    
    if recording and not paused:
        out.write(frame)
        elapsed_time = time.time() - start_time
        
        if time.time() - last_blink_time >= 0.5:
            blink = not blank
            last_blink_time = time.time()
            
        if blink:
            cv.circle(frame, (50,50), 10, (0,0,255), -1)    
    