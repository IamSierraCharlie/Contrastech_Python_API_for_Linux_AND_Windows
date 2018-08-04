import cv2
import linux_cams_sdk

camwidth = 1280
camheight = 1024
channels = 3
# this is here to show that you probably should set the framerate of the camera and the framerate
# of the cv2 window the same.  I had problems here and this appeared to resolve them

target_framerate = 200
framerate_cv2_window = int(1000/target_framerate)
camera = linux_cams_sdk.Camera(camwidth, camheight, channels)
camera.change_setting(setting=b"TriggerSource", option=b'Software')
camera.change_setting(setting=b"TriggerSelector", option=b'FrameStart')
# activates the camera - light should start flashing on the back
camera.change_setting(setting=b'AcquisitionMode', option=b'Continuous')
camera.change_setting(setting=b"TriggerMode", option=b'On')
camera.activate()
camera.change_setting(setting=b"ExposureAuto", option=b'Off')
camera.change_setting(setting=b"ExposureTime", option=5000)  # will fail if ExposureAuto is not set to Off First

while True:
    #image = camera.grab_image()
    image = cv2.cvtColor(camera.grab_image(), cv2.COLOR_BGR2RGB)
    cv2.imshow('Contrastech Mars USB3 Vision Camera Test', image)
    k = cv2.waitKey(framerate_cv2_window)

    if k == 27:  # Esc key to stop
        camera.change_setting(setting=b"TriggerMode", option=b'Off')
        break



# dectivates the camera - light should stop flashing on the back



#camera.activate()

#camera.change_setting(setting=b"ExposureAuto", option=b'Continuous')
#### acquisitrion framerate
#camera.change_setting(setting=b"AcquisitionFrameRateEnable", option=False)
#camera.change_setting(setting=b"AcquisitionFrameRate", option=target_framerate)
#camera.change_setting(setting=b"AcquisitionFrameRateEnable", option=True)

# Notes - this setting will impact the exposure time and may fail
# due to the selected framerate being too high for the requested exposure time






