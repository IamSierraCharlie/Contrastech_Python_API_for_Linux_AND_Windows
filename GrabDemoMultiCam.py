import cv2
import multicamsApi
import numpy as np

camA = 0
camB = 1
img_width = 640
img_height = 480
channels = 3
target_framerate0 = 50
target_framerate1 = 70

framerate_cv2_window0 = int(1000/target_framerate0)
framerate_cv2_window1 = int(1000/target_framerate1)

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
api.create_camera_instance(camA)
api.open_camera(camA)
api.set_camera_resolution(camA, img_width, img_height, img_channels=3, centre_resolution=False)
api.create_camera_instance(1)
api.open_camera(1)
api.set_camera_resolution(1, img_width, img_height, img_channels=3, centre_resolution=False)
print("setting some properties")
api.property(camA, "AcquisitionFrameRate", target_framerate0)
api.property(camA, "DeviceTemperatureSelector", "Sensor")
api.property(camA, "TriggerSource", "Software")
api.property(camA, "TriggerSelector", "FrameStart")
api.property(camA, "AcquisitionMode", "Continuous")
api.property(camA, "TriggerMode", "On")
api.activate(camA)
api.property(camA, "ExposureAuto", "Off")
api.property(camA, "ExposureTime", 15000)
api.property(camA, "Brightness", 50)
brand_name0 = api.property(camA, "DeviceVendorName")
model_name0 = api.property(camA, "DeviceModelName")

api.property(1, "AcquisitionFrameRate", target_framerate1)
api.property(1, "DeviceTemperatureSelector", "Sensor")
api.property(1, "TriggerSource", "Software")
api.property(1, "TriggerSelector", "FrameStart")
api.property(1, "AcquisitionMode", "Continuous")
api.property(1, "TriggerMode", "On")
api.activate(1)
api.property(1, "ExposureAuto", "Off")
api.property(1, "ExposureTime", 15000)
api.property(1, "Brightness", 50)
brand_name1 = api.property(1, "DeviceVendorName")
model_name1 = api.property(1, "DeviceModelName")

temp0 = api.property(camA, "DeviceTemperature")
temp1 = api.property(1, "DeviceTemperature")

color = list(np.random.random(size=3) * 256)
camera_name0 = api.property(camA, "DeviceUserID")
camera_name1 = api.property(1, "DeviceUserID")
counter = 0
print('Get sensor width, height')
# where do I get this info from??
# Check in iCentral under "Features" - dont forget to select Guru
sensor_width = api.property(camA, "SensorWidth")
sensor_height = api.property(camA, "SensorHeight")
print('poop')

while True:
    if counter > target_framerate0 * 5:

        temp0 = api.property(camA, "DeviceTemperature")  # dont grab temp every frame
        temp1 = api.property(1, "DeviceTemperature")  # dont grab temp every frame
        color = list(np.random.random(size=3) * 256)
        counter = 0
    image0 = api.grab_image(camA)
    image1 = api.grab_image(1)
    cv2.putText(image0, f'{target_framerate0}fps', (img_width - 125, 30), cv2.FONT_HERSHEY_DUPLEX, 1, color)
    cv2.putText(image1, f'{target_framerate1}fps', (img_width - 125, 30), cv2.FONT_HERSHEY_DUPLEX, 1, color)

    cv2.putText(image0, f'Temp {temp0}c', (30, 30), cv2.FONT_HERSHEY_DUPLEX, 1, color)
    cv2.putText(image1, f'Temp {temp1}c', (30, 30), cv2.FONT_HERSHEY_DUPLEX, 1, color)

    cv2.imshow(f'{brand_name0} {model_name0} USB3 Vision Camera => {camera_name0}', image0)
    cv2.imshow(f'{brand_name1} {model_name1} USB3 Vision Camera => {camera_name1}', image1)

    k = cv2.waitKey(framerate_cv2_window0)
    counter += 1
    if k == 27:  # Esc key to stop
        break

api.deactivate(camA)
api.deactivate(1)






