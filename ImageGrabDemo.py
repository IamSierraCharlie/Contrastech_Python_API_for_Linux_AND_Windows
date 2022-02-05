import cv2
import linuxCamsApi
import numpy as np
sensor_width = 1280  # this is the actual sensor width not the image_width
sensor_height = 1024  # this is the actual sensor height not the image_height
# Ideally, you should select PAL or NTSC supported resolutions
# others work, but its a bit hit and miss
img_width = 712
img_height = 712
offset_x = 284
offset_y = 184
channels = 3
# this is here to show that you probably should set the framerate of the camera and the framerate
# of the cv2 window the same.  I had problems here and this appeared to resolve them
target_framerate = 50
framerate_cv2_window = int(1000/target_framerate)
camera = linuxCamsApi.Camera(img_width, img_height, channels, debug=False)
# when you create an instance of the camera, it should do the following:
# gets camera instance
# gets the genicam schema file - you cannot get the file without connectin to the camera first
# unzips it
# gets the unzipped file and loads it as a variable

print("setting some properties")
# the offset needs to be considered with setting the Width and height
# camera.property_set(setting="DeviceReset", option='Execute', featuretype='Command')
# its probably better to instantiate the camera pointer once in the linuxCamsApi.....
camera.property_getset("AcquisitionFrameRate", target_framerate)
camera.property_getset("DeviceTemperatureSelector", "Sensor")
camera.property_getset("OffsetX", offset_x)
camera.property_getset("OffsetY", offset_y)
camera.property_getset("Width", img_width)
camera.property_getset("Height", img_height)
camera.property_getset("TriggerSource", "Software")
camera.property_getset("TriggerSelector", "FrameStart")
camera.property_getset("AcquisitionMode", "Continuous")
# activates the camera - light should start flashing on the back
camera.property_getset("TriggerMode", "On")
camera.activate()
camera.property_getset("ExposureAuto", "Off")
camera.property_getset("ExposureTime", 15000)
camera.property_getset("Brightness", 50)
print("done!")
brand_name = camera.property_getset("DeviceVendorName")
model_name = camera.property_getset("DeviceModelName")
temp = camera.property_getset("DeviceTemperature")
color = list(np.random.random(size=3) * 256)
camera_name = camera.property_getset("DeviceUserID")
counter = 0

while True:
    if counter > target_framerate * 5:
        temp = camera.property_getset("DeviceTemperature")  # dont grab temp every frame
        color = list(np.random.random(size=3) * 256)
        counter = 0
    image = camera.grab_image()
    cv2.putText(image, f'{target_framerate}fps', (img_width - 125, 30), cv2.FONT_HERSHEY_DUPLEX, 1, color)
    cv2.putText(image, f'Temp {temp}c', (30, 30), cv2.FONT_HERSHEY_DUPLEX, 1, color)
    cv2.imshow(f'{brand_name} {model_name} USB3 Vision Camera => {camera_name}', image)
    k = cv2.waitKey(framerate_cv2_window)
    counter += 1
    if k == 27:  # Esc key to stop
        break

camera.deactivate()

# deactivates the camera - light should stop flashing on the back

# camera.activate()

# camera.change_setting(setting=b"ExposureAuto", option=b'Continuous')
# acquisitrion framerate
# camera.change_setting(setting=b"AcquisitionFrameRateEnable", option=False)
# camera.change_setting(setting=b"AcquisitionFrameRate", option=target_framerate)
# camera.change_setting(setting=b"AcquisitionFrameRateEnable", option=True)
# Notes - this setting will impact the exposure time and may fail
# due to the selected framerate being too high for the requested exposure time






