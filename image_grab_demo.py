import cv2
import linux_cams_sdk

sensor_width = 1280
sensor_height = 1024
# Ideally, you should select PAL or NTSC supported resolutions
# others work, but its a bit hit and miss
img_width = 1280
img_height = 1024
offset_x = 0
offset_y = 0
channels = 3
# this is here to show that you probably should set the framerate of the camera and the framerate
# of the cv2 window the same.  I had problems here and this appeared to resolve them

# ToDo:  make changes here so you can set more settings
target_framerate = 23
framerate_cv2_window = int(1000/target_framerate)
camera = linux_cams_sdk.Camera(sensor_width, sensor_height, img_width, img_height, channels)
print("setting some properties")
# the offset needs to be considered with setting the Width and height
# camera.property_set(setting="DeviceReset", option='Execute', featuretype='Command')

camera.property_set(setting="DeviceUserID", option='mycamera', featuretype='String')

camera.property_set(setting="OffsetX", option=offset_x, featuretype='Integer')
camera.property_set(setting="OffsetY", option=offset_y, featuretype='Integer')


camera.property_set(setting="Width", option=img_width, featuretype='Integer')
camera.property_set(setting="Height", option=img_height, featuretype='Integer')
camera.property_set(setting="TriggerSource", option='Software', featuretype='Enumeration')
camera.property_set(setting="TriggerSelector", option='FrameStart', featuretype='Enumeration')
camera.property_set(setting='AcquisitionMode', option='Continuous', featuretype='Enumeration')
# activates the camera - light should start flashing on the back
camera.property_set(setting="TriggerMode", option='On', featuretype='Enumeration')
camera.activate()
camera.property_set(setting="ExposureAuto", option='Off', featuretype='Enumeration')
camera.property_set(setting="ExposureTime", option=15000, featuretype='Float')  # will fail if ExposureAuto is not set to Off First

print("done!")

while True:
    image = camera.grab_image()
    corrected_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    cv2.imshow('Contrastech Mars USB3 Vision Camera Test', corrected_image)
    k = cv2.waitKey(framerate_cv2_window)
    #print(k)
    if k == 1048603:  # Esc key to stop
        # camera.change_setting(setting=b"TriggerMode", option=b'Off')
        camera.deactivate()
        break

# deactivates the camera - light should stop flashing on the back

# camera.activate()

# camera.change_setting(setting=b"ExposureAuto", option=b'Continuous')
# acquisitrion framerate
# camera.change_setting(setting=b"AcquisitionFrameRateEnable", option=False)
# camera.change_setting(setting=b"AcquisitionFrameRate", option=target_framerate)
# camera.change_setting(setting=b"AcquisitionFrameRateEnable", option=True)
# Notes - this setting will impact the exposure time and may fail
# due to the selected framerate being too high for the requested exposure time






