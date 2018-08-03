import cv2
import linux_cams_sdk

camwidth = 1280
camheight = 1024
channels = 3


camera = linux_cams_sdk.Camera(camwidth, camheight, channels)
camera.activate()

camera.set_setting(setting=b"ExposureAuto", option=b'Off')
# other settings that work here
# this will not take a number
# setting=b"ExposureAuto", option=b'Continuous'
# setting=b"ExposureAuto", option=b'Once'
# setting=b"

camera.setExposureTime(dVal=10000)
# a dVal between 5000 and 10000 works well here

# get some camera information






while True:
    image = cv2.cvtColor(camera.grab_image(), cv2.COLOR_BGR2RGB)
    cv2.imshow('test', image)
    k = cv2.waitKey(int(1000/30))
    if k == 27:  # Esc key to stop
        camera.deactivate()
        break

