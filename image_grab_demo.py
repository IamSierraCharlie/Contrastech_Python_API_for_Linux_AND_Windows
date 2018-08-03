import cv2
import linux_cams_sdk

camwidth = 1280
camheight = 1024
channels = 3

camera = linux_cams_sdk.Camera(camwidth, camheight, channels)
camera.activate()

while True:
    image = camera.grab_image()
    cv2.imshow('test', image)
    k = cv2.waitKey(int(1000/30))
    if k == 27:  # Esc key to stop
        break

