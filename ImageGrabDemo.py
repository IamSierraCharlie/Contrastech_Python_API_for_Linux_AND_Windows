import cv2
import linuxCamsApi

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
target_framerate = 144
framerate_cv2_window = int(1000/target_framerate)
camera = linuxCamsApi.Camera(sensor_width, sensor_height, img_width, img_height, channels)
pcamera = camera.create_camera_instance()
print("setting some properties")
# the offset needs to be considered with setting the Width and height
# camera.property_set(setting="DeviceReset", option='Execute', featuretype='Command')
# its probably better to instantiate the camera pointer once in the linuxCamsApi.....
camera.set(_property="DeviceUserID", _value='mycamera', _type='String')
camera.set(_property="OffsetX", _value=offset_x, _type='Integer')
camera.set(_property="OffsetY", _value=offset_y, _type='Integer')
camera.set(_property="Width", _value=img_width, _type='Integer')
camera.set(_property="Height", _value=img_height, _type='Integer')
camera.set(_property="TriggerSource", _value='Software', _type='Enumeration')
camera.set(_property="TriggerSelector", _value='FrameStart', _type='Enumeration')
camera.set(_property='AcquisitionMode', _value='Continuous', _type='Enumeration')
# activates the camera - light should start flashing on the back
camera.set(_property="TriggerMode", _value='On', _type='Enumeration')
camera.activate()
camera.set(_property="ExposureAuto", _value='Off', _type='Enumeration')
camera.set(_property="ExposureTime", _value=15000, _type='Float')  # will fail if ExposureAuto is not set to Off First
camera.set(_property="DeviceReset", _value='Execute', _type='Command')

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






