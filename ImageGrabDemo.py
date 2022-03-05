import cv2
import camsApi
import numpy as np

# Ideally, you should select PAL or NTSC supported resolutions
# others work, but its a bit hit and miss

# want to create a function that sets the image width and then sets the offset according to what is left not being used
# I dont think you can just set any image width - I believe it needs to be divisible by 4??
# check this...

# TODO: These settings much match your camera - you must set the image width to be less that the maximum
# Width and Height of your camera sensor
# Also note that your image width / height must be divisible by 4 to my knowledge.
# You may wish to check and verify this
img_width = 640
img_height = 480
channels = 3
# this is here to show that you probably should set the framerate of the camera and the framerate
# of the cv2 window the same.  I had problems here and this appeared to resolve them
target_framerate = 50
framerate_cv2_window = int(1000/target_framerate)
camera = camsApi.Camera(debug=True)
camera.set_camera_resolution(img_width, img_height, img_channels=3, centre_resolution=False)
# when you create an instance of the camera, it should do the following:
# gets camera instance
# gets the genicam schema file - you cannot get the file without connecting to the camera first
# unzips it
# gets the unzipped file and loads it as a variable

print("setting some properties")
# the offset needs to be considered with setting the Width and height
# camera.property_set(setting="DeviceReset", option='Execute', featuretype='Command')
# its probably better to instantiate the camera pointer once in the linuxCamsApi.....

# you could create a properties file i.e. a dictionary or a JSON file - open the json file, read its contents and then
# apply accordingly
camera.property("AcquisitionFrameRate", target_framerate)
camera.property("DeviceTemperatureSelector", "Sensor")
# the following have been left here as an example - they are not deprecated - more superseded by the new high level
# function set_camera_resolution
#camera.property("OffsetX", offset_x)
#camera.property("OffsetY", offset_y)
#camera.property("Width", img_width)
#camera.property("Height", img_height)
camera.property("TriggerSource", "Software")
camera.property("TriggerSelector", "FrameStart")
camera.property("AcquisitionMode", "Continuous")
# activates the camera - light should start flashing on the back
camera.property("TriggerMode", "On")
camera.activate()
camera.property("ExposureAuto", "Off")
camera.property("ExposureTime", 15000)
camera.property("Brightness", 50)
print("done!")
brand_name = camera.property("DeviceVendorName")
model_name = camera.property("DeviceModelName")
temp = camera.property("DeviceTemperature")
color = list(np.random.random(size=3) * 256)
camera_name = camera.property("DeviceUserID")
counter = 0
print('Get sensor width, height')
# where do I get this info from??
# Check in iCentral under "Features" - dont forget to select Guru
sensor_width = camera.property("SensorWidth")
sensor_height = camera.property("SensorHeight")


while True:
    if counter > target_framerate * 5:
        temp = camera.property("DeviceTemperature")  # dont grab temp every frame
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






