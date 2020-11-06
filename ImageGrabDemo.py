import cv2
import linuxCamsApi

sensor_width = 1280  # this is the actual sensor width not the image_width
sensor_height = 1024 # this is the actual sensor height not the image_height
# Ideally, you should select PAL or NTSC supported resolutions
# others work, but its a bit hit and miss
img_width = 1280
img_height = 1024
offset_x = 0
offset_y = 0
channels = 3
# this is here to show that you probably should set the framerate of the camera and the framerate
# of the cv2 window the same.  I had problems here and this appeared to resolve them
target_framerate = 144
framerate_cv2_window = int(1000/target_framerate)
camera = linuxCamsApi.Camera(sensor_width, sensor_height, img_width, img_height, channels)
# when you create an instance of the camera, it should do the following:
# gets camera instance
# gets the genicam schema file - you cannot get the file without connectin to the camera first
# unzips it
# gets the unzipped file and loads it as a variable

print("setting some properties")
# the offset needs to be considered with setting the Width and height
# camera.property_set(setting="DeviceReset", option='Execute', featuretype='Command')
# its probably better to instantiate the camera pointer once in the linuxCamsApi.....
camera.property_set("DeviceUserID", 'Camera')
camera.property_set("OffsetX", offset_x)
camera.property_set("OffsetY", offset_y)
camera.property_set("Width", img_width)
camera.property_set("Height", img_height)
camera.property_set("TriggerSource", "Software")
camera.property_set("TriggerSelector", "FrameStart")
camera.property_set("AcquisitionMode", "Continuous")
# activates the camera - light should start flashing on the back
camera.property_set("TriggerMode", "On")
camera.activate()
camera.property_set("ExposureAuto", "Off")
camera.property_set("ExposureTime", 15000)
camera.property_set("Brightness", 50)
# camera.set(_property="DeviceReset", _value='Execute', _type='Command')

print("done!")

while True:
    image = camera.grab_image()
    corrected_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    cv2.imshow('Contrastech Mars USB3 Vision Camera Test', corrected_image)
    k = cv2.waitKey(framerate_cv2_window)
    camera.property_get_temp()
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






