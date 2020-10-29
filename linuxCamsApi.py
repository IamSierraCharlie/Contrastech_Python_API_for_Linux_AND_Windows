from ImageConvert import *
from MVSDK import *  # only for the contrastech camera
import numpy as np

g_cameraStatusUserInfo = b"statusInfo"


class Camera(object):
    def __init__(self, sensor_width, sensor_height, img_width, img_height, img_channels):
        # get the camera list
        self.img_width = img_width
        self.img_height = img_height
        self.img_channels = img_channels
        self.image_source = None
        self.frame = None
        self.userInfo = None
        # self.cam = None
        self.t = None
        self.info = None
        self.temperature = None
        self.acqCtrl = None
        self.max_width = None
        self.max_height = None
        self.connectCallBackFunc = connectCallBack(self.device_link_notify)
        self.connectCallBackFuncEx = connectCallBackEx(self.device_link_notify)
        self.frameCallbackFunc = callbackFunc(self.on_get_frame)
        # self.create_camera_instance()  # instantiated upon calling the camera Class
        offset_x, offset_y = self.check_image_dimension_validity(sensor_width, sensor_height, img_width, img_height)

    # self.set_roi(self.cam, offset_x, offset_y, img_width, img_height)
    @staticmethod  # this function reports the camera status.  It will output issues to the cmd prompt
    def device_link_notify(connect_arg, link_info):
        if EVType.offLine == connect_arg.contents.m_event:
            print("camera is off line, userInfo [%s]" % c_char_p(link_info).value)
        elif EVType.onLine == connect_arg.contents.m_event:
            print("camera is on line, userInfo [%s]" % c_char_p(link_info).value)

    @staticmethod
    def on_get_frame(frame):
        n_ret = frame.contents.valid(frame)
        if n_ret != 0:
            print("frame is invalid!")
            # Release driver image cache resources
            frame.contents.release(frame)
            return

        # print("BlockId = %d" % (frame.contents.getBlockId(frame)))
        frame.contents.release(frame)

    # Unregister camera connection status callback


    def unsubscribe_camera_status(self, pcamera):
        # Anti-registration notification
        event_subscribe = pointer(GenicamEventSubscribe())
        event_subscribe_info = GenicamEventSubscribeInfo()
        event_subscribe_info.pCamera = pointer(pcamera)
        n_ret = GENICAM_createEventSubscribe(byref(event_subscribe_info), byref(event_subscribe))
        if n_ret != 0:
            print("create event_subscribe fail!")
            return -1

        n_ret = event_subscribe.contents.unsubscribeConnectArgs(event_subscribe, self.connectCallBackFunc,
                                                                g_cameraStatusUserInfo)
        if n_ret != 0:
            print("unsubscribeConnectArgs fail!")
            # Release related resources
            event_subscribe.contents.release(event_subscribe)
            return -1
        # Relevant resources need to be released when they are no longer used
        event_subscribe.contents.release(event_subscribe)
        return 0

    def subscribe_camera_status(self, pcamera):
        # Registration notification
        event_subscribe = pointer(GenicamEventSubscribe())
        event_subscribe_info = GenicamEventSubscribeInfo()
        event_subscribe_info.pCamera = pointer(pcamera)
        n_ret = GENICAM_createEventSubscribe(byref(event_subscribe_info), byref(event_subscribe))
        if n_ret != 0:
            print("create eventSubscribe fail!")
            return -1

        n_ret = event_subscribe.contents.subscribeConnectArgs(event_subscribe, self.connectCallBackFunc,
                                                              g_cameraStatusUserInfo)
        if n_ret != 0:
            print("subscribeConnectArgsEx fail!")
            # Release related resources
            event_subscribe.contents.release(event_subscribe)
            return -1

        # Relevant resources need to be released when they are no longer used
        event_subscribe.contents.release(event_subscribe)
        return 0

    def open_camera(self, pcamera):
        n_ret = pcamera.connect(pcamera, c_int(GENICAM_ECameraAccessPermission.accessPermissionControl))
        if n_ret != 0:
            print("camera connect fail!")
            return -1
        else:
            print("camera connect success.")

        n_ret = self.subscribe_camera_status(pcamera)
        if n_ret != 0:
            print("subscribeCameraStatus fail!")
            return -1
        return 0

    def close_camera(self, pcamera):
        n_ret = self.unsubscribe_camera_status(pcamera)
        if n_ret != 0:
            print("unsubscribeCameraStatus fail!")
            return -1
        n_ret = pcamera.disConnect(byref(pcamera))
        if n_ret != 0:
            print("disConnect camera fail!")
            return -1
        return 0

    @staticmethod
    def check_valid_frame(cam, frame, image_source):
        n_ret = frame.contents.valid(frame)
        if n_ret != 0:
            print("frame is invalid!")
            frame.contents.release(frame)
            # Release related resources
            image_source.contents.release(cam)
            return -1

    def deactivate(self, pcamera):
        print('should deactivate')
        n_ret = self.image_source.contents.stopGrabbing(self.image_source)
        if n_ret != 0:
            print("stopGrabbing fail!")
            # Release related resourcesrces
            self.image_source.contents.release(self.image_source)
            return -1
        # Turn off trigger mode - camera light should stop flashing
        trig_mode_enum_node = self.acqCtrl.contents.triggerMode(self.acqCtrl)
        n_ret = trig_mode_enum_node.setValueBySymbol(byref(trig_mode_enum_node), b"Off")
        if n_ret != 0:
            print("set TriggerMode value [On] fail!")
            # Release related resources
            trig_mode_enum_node.release(byref(trig_mode_enum_node))
            self.acqCtrl.contents.release(self.acqCtrl)
            return -1

        n_ret = self.close_camera(pcamera)
        if n_ret != 0:
            print("closeCamera fail")
            self.image_source.contents.release(self.image_source)
            return -1
        self.image_source.contents.release(self.image_source)

    def activate(self, pcamera):
        # connect to the camera
        acq_ctrl_info = GenicamAcquisitionControlInfo()
        acq_ctrl_info.pCamera = pointer(pcamera)
        self.acqCtrl = pointer(GenicamAcquisitionControl())
        n_ret = GENICAM_createAcquisitionControl(pointer(acq_ctrl_info), byref(self.acqCtrl))
        if n_ret != 0:
            print("create AcquisitionControl fail!")
            return -1

        # create the streaming source
        print('creating a stream source')
        stream_source_info = GenicamStreamSourceInfo()
        stream_source_info.channelId = 0
        stream_source_info.pCamera = pointer(pcamera)
        self.image_source = pointer(GenicamStreamSource())
        n_ret = GENICAM_createStreamSource(pointer(stream_source_info), byref(self.image_source))
        if n_ret != 0:
            print("create image_source fail!")
            return -1
        # attach grabbing
        n_ret = self.image_source.contents.attachGrabbing(self.image_source, self.frameCallbackFunc)
        if n_ret != 0:
            print("attachGrabbing fail!")
            self.image_source.contents.release(self.image_source)
            return -1

        # Start grabbing images
        n_ret = self.image_source.contents.startGrabbing(self.image_source, c_ulonglong(0),
                                                         c_int(GENICAM_EGrabStrategy.grabStrategySequential))
        if n_ret != 0:
            print("startGrabbing fail!")
            # Release related resources
            self.image_source.contents.release(self.image_source)
            return -1

        # detach from grabbing - this step is necessary in order to successfully grab images
        n_ret = GENICAM_createAcquisitionControl(pointer(acq_ctrl_info), byref(self.acqCtrl))
        if n_ret != 0:
            print("create AcquisitionControl fail!")
            self.image_source.contents.release(self.image_source)
            return -1
        n_ret = self.image_source.contents.detachGrabbing(self.image_source, self.frameCallbackFunc)
        if n_ret != 0:
            print("detachGrabbing fail!")
            self.image_source.contents.release(self.image_source)
            return -1

    @staticmethod
    def enumerate_cameras():
        system = pointer(GENICAM_System())
        n_ret = GENICAM_getSystemInstance(byref(system))
        if n_ret != 0:
            print("getSystemInstance fail!")
            return None, None
        camera_list = pointer(GenicamCamera())
        camera_cnt = c_uint()
        n_ret = system.contents.discovery(system, byref(camera_list), byref(camera_cnt),
                                          c_int(GENICAM_EProtocolType.typeAll))
        if n_ret != 0:
            print("discovery fail!")
            return None, None
        elif camera_cnt.value < 1:
            print("No camera found - have you installed the iCentral software?")
            print("If your kernel has been updated lately, you may need to reinstall")
            return None, None
        else:
            print("cameraCnt: " + str(camera_cnt.value))
            # try get cam info here
            return camera_cnt.value, camera_list

    @staticmethod
    def connect_device_control(camera):
        device_control = pointer(GenicamDeviceControl())
        device_control_info = GenicamDeviceControlInfo()
        device_control_info.pCamera = pointer(camera)
        n_ret = GENICAM_createDeviceControl(byref(device_control_info), byref(device_control))
        if n_ret != 0:
            print("Failed to connect to control")
            device_control.contents.release(device_control)
        string_parser = pointer(GENICAM_StringNode())
        string_parser_info = GENICAM_StringNodeInfo()
        string_parser_info.pCamera = pointer(camera)
        n_ret = GENICAM_createStringNode(byref(string_parser_info), byref(string_parser))
        if n_ret != 0:
            print("Failed to create string node")
            string_parser.contents.release(string_parser)
        # feed this through string node?
        # print("The temp reported is: " + str(device_control.contents.deviceUserID(device_control)))
        # GENICAM_StringNode_getValue = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StringNode), c_char_p, POINTER(c_uint))
        print("!!!!!!!!!!!!!!!!!!!!!!" + str(
            string_parser.contents.getValue(device_control.contents.deviceUserID(device_control), b"deviceUserID",
                                            None)))

    @staticmethod
    def get_usb_info(camera):
        # This is test code and I'm not certain of the benefit as yet
        print("GETTING USB INTERFACE INFO!!")
        print("GETTING USB CAMERA INFO!!")
        # usb_camera = pointer(camera)
        usb_camera = pointer(GenicamUsbCamera())
        usb_camera_info = GenicamUsbCameraInfo()
        usb_camera_info.pCamera = pointer(camera)
        n_ret = GENICAM_createUsbCamera(byref(usb_camera_info), byref(usb_camera))
        if n_ret != 0:
            print("Failed to get USB interface info")
            usb_camera.contents.release(usb_camera)
        print("ConfigurationValid: " + str(
            usb_camera.contents.getConfigurationValid(usb_camera)))  # if this is nothing, then I think its fine...
        print("GenCPVersion: " + usb_camera.contents.getGenCPVersion(usb_camera).decode("utf-8"))
        print("U3VVersion: " + usb_camera.contents.getU3VVersion(usb_camera).decode("utf-8"))
        print("DeviceGUID: " + usb_camera.contents.getDeviceGUID(usb_camera).decode("utf-8"))
        print("FamilyName: " + usb_camera.contents.getFamilyName(usb_camera).decode("utf-8"))
        print("U3VSerialNumber: " + usb_camera.contents.getU3VSerialNumber(usb_camera).decode("utf-8"))
        print("Speeds -> negative number means unsupported, where as zero is supported?")
        print("LowSpeedSupported: " + str(usb_camera.contents.isLowSpeedSupported(usb_camera)))
        print("FullSpeedSupported: " + str(usb_camera.contents.isFullSpeedSupported(usb_camera)))
        print("HighSpeedSupported " + str(usb_camera.contents.isHighSpeedSupported(usb_camera)))
        print("SuperSpeedSupported " + str(usb_camera.contents.isSuperSpeedSupported(usb_camera)))
        print("Speed " + usb_camera.contents.getSpeed(usb_camera).decode("utf-8"))
        print("MaxPower " + usb_camera.contents.getMaxPower(usb_camera).decode("utf-8"))
        print("DriverInstalled " + str(usb_camera.contents.isDriverInstalled(usb_camera)))
        input("Press Enter to continue...")
        usb_camera.contents.release(usb_camera)

    def create_camera_instance(self):
        camera_count, camera_list = self.enumerate_cameras()
        if camera_count is None:  # no camera handler
            print('No camera handler')
        if camera_count > 1:
            print('Multiple cameras')
        for index in range(0, camera_count):  # camera details
            print('Getting camera details\n')
            camera = camera_list[index]
            print("\nCamera Id = " + str(index))
            print("vendor name   = " + str(camera.getVendorName(camera)))
            print("Model  name   = " + str(camera.getModelName(camera)))
            print("Serial number = " + str(camera.getSerialNumber(camera)))
            print("Device Version = " + str(camera.getDeviceVersion(camera)))
            print("Interface name = " + str(camera.getInterfaceName(camera)))
            print("Interface type = " + str(camera.getInterfaceType(camera)))
        # print("XML = " + str(camera.getSpeed(camera)))
        # time.sleep(3)
        pcamera = camera_list[0]  # this is the actual camera
        # self.connect_device_control(self.cam)
        # self.property_get("ChunkEnable")
        self.get_usb_info(pcamera)
        # open the camera
        # query this camera?

        n_ret = self.open_camera(pcamera)  # opens the camera
        if n_ret != 0:  # handles the camera open failure
            print("openCamera fail.")
        else:
            print("Camera Opened")
            return camera_list[0]

    def grab_image(self, pcamera):
        trig_software_cmd_node = self.acqCtrl.contents.triggerSoftware(self.acqCtrl)
        n_ret = trig_software_cmd_node.execute(byref(trig_software_cmd_node))
        if n_ret != 0:
            print("Execute triggerSoftware fail!")
            # 释放相关资源 - Release related resources
            trig_software_cmd_node.release(byref(trig_software_cmd_node))
            self.acqCtrl.contents.release(self.acqCtrl)
            self.image_source.contents.release(self.image_source)
            return -1
        # print('2')
        frame = pointer(GenicamFrame())
        # print(datetime.datetime.now().strftime("%y%m%d%H%M%S"))
        n_ret = self.image_source.contents.getFrame(self.image_source, byref(frame), c_uint(1000))

        if n_ret != 0:
            print("SoftTrigger getFrame fail! timeOut [1000]ms")
            # Release related resources
            self.deactivate(pcamera)
            self.image_source.contents.release(self.image_source)
            return -1
        else:
            # print("SoftTrigger getFrame success BlockId = " + str(frame.contents.getBlockId(frame)))
            # print("get frame time: " + str(datetime.datetime.now()))
            trig_software_cmd_node.release(byref(trig_software_cmd_node))

            self.check_valid_frame(pcamera, frame, self.image_source)
        # print("grabbed BlockId = %d" % (frame.contents.getBlockId(frame)))
        # print("Chunk = %d" % (frame.contents.getChunkCount(frame)))

        # Copy the raw data image out
        image_size = frame.contents.getImageSize(frame)
        buff_addr = frame.contents.getImage(frame)
        frame_buff = c_buffer(b'\0', image_size)
        memmove(frame_buff, c_char_p(buff_addr), image_size)
        convert_params = IMGCNV_SOpenParam()
        convert_params.dataSize = image_size
        convert_params.height = frame.contents.getImageHeight(frame)
        convert_params.width = frame.contents.getImageWidth(frame)
        convert_params.paddingX = frame.contents.getImagePaddingX(frame)
        convert_params.paddingY = frame.contents.getImagePaddingY(frame)
        convert_params.pixelFormat = frame.contents.getImagePixelFormat(frame)

        # print('dataSize', imageSize)
        # print('height', frame.contents.getImageHeight(frame))
        # print('width', frame.contents.getImageWidth(frame))
        # print('paddingX', frame.contents.getImagePaddingX(frame))
        # print('paddingY', frame.contents.getImagePaddingY(frame))
        # print('pixelFormat', frame.contents.getImagePixelFormat(frame))

        # Release driver image cache
        frame.contents.release(frame)
        rgb_buff = c_buffer(b'\0', convert_params.height * convert_params.width * 3)
        rgb_size = c_int()
        n_ret = IMGCNV_ConvertToRGB24(cast(frame_buff,
                                           c_void_p),
                                      byref(convert_params), cast(rgb_buff, c_void_p),
                                      byref(rgb_size))

        if n_ret != 0:
            print("image convert fail! errorCode = " + str(n_ret))
            # 释放相关资源 - Release related resources
            self.image_source.contents.release(self.image_source)
            return -1

        final = np.reshape(np.frombuffer(bytearray(string_at(rgb_buff,
                                                             self.img_channels * self.img_height * self.img_width)),
                                         dtype=np.uint8), (self.img_height, self.img_width, self.img_channels))
        return final

    def property_get(self, pcamera, setting, featuretype):  # this is going to be for type string....setting must be of type string
        print('\n\n\nGetting info about setting: {}'.format(setting))
        setting_to_get = setting.encode()  # convert to bytes
        # set the right pointer
        setting_grabber = pointer(GenicamDeviceControl())
        # set the right info associated with pointer
        setting_info = GenicamDeviceControlInfo()
        # set the camera
        setting_info.pCamera = pointer(pcamera)
        # assign the attribute
        # print(type(setting_to_change))
        # setting_info.attrName = setting_to_change
        n_ret = GENICAM_createDeviceControl(byref(setting_info), byref(setting_grabber))
        if n_ret != 0:
            print("Unable to access {}".format(setting))
            # Release related resources
            self.image_source.contents.release(self.image_source)
            return -1
        print(setting_grabber.contents.deviceUserID(setting_grabber))
        setting_grabber.contents.release(setting_grabber)

    def set(self, _camera, _property, _value, _type):  # adding featuretype for better control
        # here, we will eventually review the xml for _property to determine which feature type it is
        # for now, we'll set it manually....
        print('\n\n\nInstance is: {}'.format(type(_value)))
        _property = _property.encode()  # convert to bytes
        if _type is "Float":  # A Number
            print('changing with settings num')
            self.settings_float_num(_camera, _property, _value)
        elif _type is "Integer":  # A Number
            print('changing with settings num')
            self.settings_int_num(_camera, _property, _value)
        elif _type is "Enumeration":  # A string - encode to bytes
            print('changing with settings_unum_str')
            self.settings_enum_str(_camera, _property, _value.encode())
        elif _type is "Bool":  # A Boolean
            print('changing with settings_bool')
            self.settings_bool(_camera, _property, _value)
        elif _type is "String":
            print('change with settings string')
            self.settings_string(_camera, _property, _value)
        elif _type is "Command":
            print('executing the command')
            self.settings_execute_command(camera=_camera, _property=_property, _value=_value)
        else:
            print('unknown var {} from setting {} - unable to handle this'.format(_value, _property))
            exit()

    # TODO: this works - but the camera must not be in use when calling it to execute a command...

    @staticmethod
    def settings_execute_command(camera, _property, _value):
        setting_exec_command = pointer(GENICAM_CmdNode())
        setting_exec_command_info = GENICAM_CmdNodeInfo()
        setting_exec_command_info.pCamera = pointer(camera)
        setting_exec_command_info.attrName = _property
        n_ret = GENICAM_createCmdNode(byref(setting_exec_command_info), byref(setting_exec_command))
        if n_ret != 0:
            print("Unable to access {}".format(_property))
            # Release related resources
            setting_exec_command.contents.release(setting_exec_command)
            return -1
        else:  # if accessible, check command is valid
            print("Checking {}".format(_property))
            n_ret = setting_exec_command.contents.isValid(setting_exec_command, _value)
            print("nret is {}".format(n_ret))
            if n_ret != 0:
                print("{} is an invalid command".format(_property))
                # Release related resources
                setting_exec_command.contents.release(setting_exec_command)
                return -1
            else:  # if available, it is available
                print("Checking {}".format(_property))
                n_ret = setting_exec_command.contents.isAvailable(setting_exec_command, _value)
                print("nret is {}".format(n_ret))
                if n_ret != 0:
                    print("{} isAvailable cannot be achieved right now".format(_property))
                    # Release related resources
                    setting_exec_command.contents.release(setting_exec_command)
                    return -1
                else:  # its writeable so lets do it!
                    print("Checking {}".format(_property))
                    n_ret = setting_exec_command.contents.execute(setting_exec_command, _value)
                    print("nret is {}".format(n_ret))
                    if n_ret != 0:
                        print("Execution of command {} failed".format(_property))
                        # Release related resources
                        setting_exec_command.contents.release(setting_exec_command)

    def settings_enum_str(self, pcamera, _property, _value):  # Check the type under the feature name - it needs to be enumerable
        setting_char_enum_node = pointer(GENICAM_EnumNode())
        setting_char_enum_node_info = GenicamEnumNodeInfo()
        setting_char_enum_node_info.pCamera = pointer(pcamera)
        setting_char_enum_node_info.attrName = _property
        n_ret = GENICAM_createEnumNode(byref(setting_char_enum_node_info), byref(setting_char_enum_node))
        if n_ret != 0:
            print("Unable to access {}".format(_property))
            # Release related resources
            self.image_source.contents.release(self.image_source)  # this is wrong
            return -1
        # change setting_char_ mode to continuous
        print('Changing {} to {}'.format(_property, _value))
        n_ret = setting_char_enum_node.contents.setValueBySymbol(setting_char_enum_node, _value)
        if n_ret != 0:
            print('Failed!')
            # Release related resources
            setting_char_enum_node.contents.release(setting_char_enum_node)
            self.image_source.contents.release(self.image_source)  # this is wrong
            return -1
        else:
            print('Success!')
        setting_char_enum_node.contents.release(setting_char_enum_node)

    def settings_float_num(self, pcamera, _property, _value):  # Check the type under the feature name - it needs to be a number (like a float)
        setting_num_node = pointer(GenicamDoubleNode())
        setting_num_node_info = GenicamDoubleNodeInfo()
        setting_num_node_info.pCamera = pointer(pcamera)
        setting_num_node_info.attrName = _property
        n_ret = GENICAM_createDoubleNode(byref(setting_num_node_info), byref(setting_num_node))
        if n_ret != 0:
            print("create {} Node fail!".format(_property))
            return -1
        n_ret = setting_num_node.contents.setValue(setting_num_node, c_double(_value))
        if n_ret != 0:
            print("set {} to {} fail!".format(_property, _value))
            setting_num_node.contents.release(setting_num_node)
            return -1
        else:
            print("set {} to {} success.".format(_property, _value))
        setting_num_node.contents.release(setting_num_node)
        return 0

    def settings_int_num(self, pcamera, _property,
                         _value):  # Check the type under the feature name - it needs to be a number (like a float)
        setting_int_node = pointer(GenicamIntNode())
        setting_int_node_info = GenicamIntNodeInfo()
        setting_int_node_info.pCamera = pointer(pcamera,)
        setting_int_node_info.attrName = _property
        n_ret = GENICAM_createIntNode(byref(setting_int_node_info), byref(setting_int_node))
        if n_ret != 0:
            print("create {} Node fail!".format(_property))
            return -1
        n_ret = setting_int_node.contents.setValue(setting_int_node, c_longlong(_value))
        if n_ret != 0:
            print("set {} to {} fail!".format(_property, _value))
            setting_int_node.contents.release(setting_int_node)
            return -1
        else:
            print("set {} to {} success.".format(_property, _value))
        setting_int_node.contents.release(setting_int_node)
        return 0

    def settings_bool(self, pcamera, _property,
                      _value):  # Check the type under the feature name - it needs to be a Bool - true or false
        setting_bool_node = pointer(GenicamBoolNode())
        setting_bool_node_info = GENICAM_BoolNodeInfo()
        setting_bool_node_info.pCamera = pointer(pcamera)
        setting_bool_node_info.attrName = _property
        n_ret = GENICAM_createBoolNode(byref(setting_bool_node_info), byref(setting_bool_node))
        if n_ret != 0:
            print("create {} Node fail!".format(_property))
            return -1
        n_ret = setting_bool_node.contents.setValue(setting_bool_node, bool(_value))
        if n_ret != 0:
            print("set {} to {} failed!".format(_property, _value))
            setting_bool_node.contents.release(setting_bool_node)
            return -1
        else:
            print("set {} to {} success.".format(_property, _value))
        setting_bool_node.contents.release(setting_bool_node)
        return 0

    def settings_string(self, pcamera, _property, _value):  # this allows setting a string where the Type is string
        setting_string_node = pointer(GENICAM_StringNode())
        setting_string_node_info = GENICAM_StringNodeInfo()
        setting_string_node_info.pCamera = pointer(pcamera)
        setting_string_node_info.attrName = _property
        n_ret = GENICAM_createStringNode(byref(setting_string_node_info), byref(setting_string_node))
        if n_ret != 0:
            print("create {} Node fail!".format(_property))
            return -1
        n_ret = setting_string_node.contents.setValue(setting_string_node, c_char_p(
            _value.encode()))  # this was a bool need to set this
        if n_ret != 0:
            print("set {} to {} failed!".format(_property, _value))
            setting_string_node.contents.release(setting_string_node)
            return -1
        else:
            print("set {} to {} success.".format(_property, _value))
        setting_string_node.contents.release(setting_string_node)
        return 0

    # TODO get some settings from the camera - i.e. sensor width and height for correctly setting w / h and offset

    @staticmethod  # this works, but it not currently in use
    def set_roi(camera, offset_x, offset_y, n_width, n_height):  # another example from the Contrastech Demo
        # 获取原始的宽度
        width_max_node = pointer(GenicamIntNode())
        width_max_node_info = GenicamIntNodeInfo()
        width_max_node_info.pCamera = pointer(camera)
        width_max_node_info.attrName = b"WidthMax"
        n_ret = GENICAM_createIntNode(byref(width_max_node_info), byref(width_max_node))
        if n_ret != 0:
            print("create WidthMax Node fail!")
            return -1

        original_width = c_longlong()
        n_ret = width_max_node.contents.getValue(width_max_node, byref(original_width))
        if n_ret != 0:
            print("widthMaxNode getValue fail!")
            # 释放相关资源 - Release related resources
            width_max_node.contents.release(width_max_node)
            return -1

        # 释放相关资源 - Release related resources
        width_max_node.contents.release(width_max_node)

        # 获取原始的高度
        height_max_node = pointer(GenicamIntNode())
        height_max_node_info = GenicamIntNodeInfo()
        height_max_node_info.pCamera = pointer(camera)
        height_max_node_info.attrName = b"HeightMax"
        n_ret = GENICAM_createIntNode(byref(height_max_node_info), byref(height_max_node))
        if n_ret != 0:
            print("create HeightMax Node fail!")
            return -1

        original_height = c_longlong()
        n_ret = height_max_node.contents.getValue(height_max_node, byref(original_height))
        if n_ret != 0:
            print("heightMaxNode getValue fail!")
            # 释放相关资源 - Release related resources
            height_max_node.contents.release(height_max_node)
            return -1

        # 释放相关资源 - Release related resources
        height_max_node.contents.release(height_max_node)

        # 检验参数
        if (original_width.value < (offset_x + n_width)) or (original_height.value < (offset_y + n_height)):
            print("please check input param!")
            return -1

        # 设置宽度
        width_node = pointer(GenicamIntNode())
        width_node_info = GenicamIntNodeInfo()
        width_node_info.pCamera = pointer(camera)
        width_node_info.attrName = b"Width"
        n_ret = GENICAM_createIntNode(byref(width_node_info), byref(width_node))
        if n_ret != 0:
            print("create Width Node fail!")
            return -1

        n_ret = width_node.contents.setValue(width_node, c_longlong(n_width))
        if n_ret != 0:
            print("widthNode setValue [%d] fail!" % n_width)
            # 释放相关资源 - Release related resources
            width_node.contents.release(width_node)
            return -1

        # 释放相关资源 - Release related resources
        width_node.contents.release(width_node)

        # 设置高度
        height_node = pointer(GenicamIntNode())
        height_node_info = GenicamIntNodeInfo()
        height_node_info.pCamera = pointer(camera)
        height_node_info.attrName = b"Height"
        n_ret = GENICAM_createIntNode(byref(height_node_info), byref(height_node))
        if n_ret != 0:
            print("create Height Node fail!")
            return -1

        n_ret = height_node.contents.setValue(height_node, c_longlong(n_height))
        if n_ret != 0:
            print("heightNode setValue [%d] fail!" % n_height)
            # 释放相关资源 - Release related resources
            height_node.contents.release(height_node)
            return -1

        # 释放相关资源 - Release related resources
        height_node.contents.release(height_node)

        # 设置OffsetX
        offset_x_node = pointer(GenicamIntNode())
        offset_x_node_info = GenicamIntNodeInfo()
        offset_x_node_info.pCamera = pointer(camera)
        offset_x_node_info.attrName = b"OffsetX"
        n_ret = GENICAM_createIntNode(byref(offset_x_node_info), byref(offset_x_node))
        if n_ret != 0:
            print("create OffsetX Node fail!")
            return -1

        n_ret = offset_x_node.contents.setValue(offset_x_node, c_longlong(offset_x))
        if n_ret != 0:
            print("OffsetX setValue [%d] fail!" % offset_x)
            # 释放相关资源 - Release related resources
            offset_x_node.contents.release(offset_x_node)
            return -1

        # 释放相关资源 - Release related resources
        offset_x_node.contents.release(offset_x_node)

        # 设置OffsetY
        offset_y_node = pointer(GenicamIntNode())
        offset_y_node_info = GenicamIntNodeInfo()
        offset_y_node_info.pCamera = pointer(camera)
        offset_y_node_info.attrName = b"OffsetY"
        n_ret = GENICAM_createIntNode(byref(offset_y_node_info), byref(offset_y_node))
        if n_ret != 0:
            print("create OffsetY Node fail!")
            return -1

        n_ret = offset_y_node.contents.setValue(offset_y_node, c_longlong(offset_y))
        if n_ret != 0:
            print("OffsetY setValue [%d] fail!" % offset_y)
            # 释放相关资源 - Release related resources
            offset_y_node.contents.release(offset_y_node)
            return -1

        # 释放相关资源 - Release related resources
        offset_y_node.contents.release(offset_y_node)
        return 0

    # the reason for this function is because the offsets for the mars camera seem to need to be a number
    # divisible by 16.  This function takes care of that for the basic dimensions that I use. It may not
    # work for other people...

    @staticmethod
    def check_image_dimension_validity(sensor_width, sensor_height, img_width, img_height):
        if not img_height == sensor_height:
            adjusted_offset_height = sensor_height - img_height
            div_check_y = adjusted_offset_height / 16  # we are checking that the offset is divisible by 16
            while not div_check_y.is_integer():
                print('centering height offset')
                adjusted_offset_height -= 1
                div_check_y = adjusted_offset_height / 16
            offset_y = adjusted_offset_height / 2
        else:
            offset_y = 0
        if not img_width == sensor_width:
            adjusted_offset_width = sensor_width - img_width
            div_check_x = adjusted_offset_width / 16  # we are checking that the offset is divisible by 16
            while not div_check_x.is_integer():
                print('centering width offset')
                adjusted_offset_width -= 1
                div_check_x = adjusted_offset_width / 16
            offset_x = adjusted_offset_width / 2
        else:
            offset_x = 0
        print('final X offset is {}'.format(int(offset_x)))
        print('final Y offset is {}'.format(int(offset_y)))
        return int(offset_y), int(offset_x)
