import cv2
import camsApi
import numpy as np

#

# want to create a function that sets the image width and then sets the offset according to what is left not being used
# I dont think you can just set any image width - I believe it needs to be divisible by 4??
# check this...

# TODO: With the latest additions, all you need to do is set the image and height.  Channels is now 3 by default and
#  you dont need to even set it. Ideally, you should select PAL or NTSC supported resolutions
#  others work, but its a bit hit and miss - your frame width and heights should be divisible by 4
img_width = 640
img_height = 480
channels = 3
# this is here to show that you probably should set the framerate of the camera and the framerate
# of the cv2 window the same.  I had problems here and this appeared to resolve them
target_framerate = 50
framerate_cv2_window = int(1000/target_framerate)
camera = camsApi.Camera(debug=True)
# TODO: Once you create your camera instance as above, then you can set your resolution as per below
#  if img_channels is not included, it will automatically be 3
#  if centre_resolution is not included, it will automatically be set to true (I'd normally have resolution centred)
camera.set_camera_resolution(img_width, img_height, img_channels=3, centre_resolution=False)
# TODO: Additionally, you can also set properties as per below
print("setting some properties")
camera.property("AcquisitionFrameRate", target_framerate)
camera.property("DeviceTemperatureSelector", "Sensor")
# TODO: the following have been left here as an example - they are not deprecated - more superseded by the new high
#  level function set_camera_resolution
# camera.property("OffsetX", offset_x)
# camera.property("OffsetY", offset_y)
# camera.property("Width", img_width)
# camera.property("Height", img_height)
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
# TODO: where do I get this info from??
#  Check in iCentral under "Features" - don't forget to select Guru
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







