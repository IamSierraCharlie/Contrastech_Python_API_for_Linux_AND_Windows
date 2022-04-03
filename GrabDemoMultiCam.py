import cv2
import multicamsApi
import numpy as np

img_width = 640
img_height = 480
channels = 3
target_framerate = 50
framerate_cv2_window = int(1000/target_framerate)
api = multicamsApi.CameraApi(debug=True)
# next, set the list of camera pointers - this will set a count of cameras plus a list of the camera pointers
api.get_camera_list()
''' 
api.camera_count represents a list of cameras that were found when getting the camera list 
api.camera_pointer_list represents a list of the camera pointers - instead of just one camera
'''
print(f'The number of cameras was {api.camera_count}')
# essentially, here, you could loop through a range to set up each camera
# next, create the camera instance
''' repeat these lines below for each camera 0, for the first camera, 1 for the second and so on'''
api.create_camera_instance(0)
api.open_camera(0)
api.set_camera_resolution(0, img_width, img_height, img_channels=3, centre_resolution=False)
print("setting some properties")
api.property(0, "AcquisitionFrameRate", target_framerate)
api.property(0, "DeviceTemperatureSelector", "Sensor")
api.property(0, "TriggerSource", "Software")
api.property(0, "TriggerSelector", "FrameStart")
api.property(0, "AcquisitionMode", "Continuous")
api.property(0, "TriggerMode", "On")
api.activate(0)
api.property(0, "ExposureAuto", "Off")
api.property(0, "ExposureTime", 15000)
api.property(0, "Brightness", 50)
print("done!")
brand_name = api.property(0, "DeviceVendorName")
model_name = api.property(0, "DeviceModelName")
temp = api.property(0, "DeviceTemperature")
color = list(np.random.random(size=3) * 256)
camera_name = api.property(0, "DeviceUserID")
counter = 0
print('Get sensor width, height')
# where do I get this info from??
# Check in iCentral under "Features" - dont forget to select Guru
sensor_width = api.property(0, "SensorWidth")
sensor_height = api.property(0, "SensorHeight")
print('poop')

while True:
    if counter > target_framerate * 5:

        temp = api.property(0, "DeviceTemperature")  # dont grab temp every frame
        color = list(np.random.random(size=3) * 256)
        counter = 0
    image = api.grab_image(0)
    cv2.putText(image, f'{target_framerate}fps', (img_width - 125, 30), cv2.FONT_HERSHEY_DUPLEX, 1, color)
    cv2.putText(image, f'Temp {temp}c', (30, 30), cv2.FONT_HERSHEY_DUPLEX, 1, color)
    cv2.imshow(f'{brand_name} {model_name} USB3 Vision Camera => {camera_name}', image)
    k = cv2.waitKey(framerate_cv2_window)
    counter += 1
    if k == 27:  # Esc key to stop
        break

api.deactivate(0)







