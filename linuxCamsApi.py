from ImageConvert import *
from MVSDK import *  # only for the contrastech camera
import numpy as np
import zipfile
import os
import xml.etree.ElementTree as ETree
import re
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
        self.campointer = None
        self.xml_property_file = None
        self.t = None
        self.info = None
        self.temperature = None
        self.acqCtrl = None
        self.max_width = None
        self.max_height = None
        self.connectCallBackFunc = connectCallBack(self.device_link_notify)
        self.connectCallBackFuncEx = connectCallBackEx(self.device_link_notify)
        self.frameCallbackFunc = callbackFunc(self.on_get_frame)
        self.create_camera_instance()  # instantiated upon calling the camera Class
        # self.get_xml()
        # offset_x, offset_y = self.check_image_dimension_validity(sensor_width, sensor_height, img_width, img_height)

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

    def unsubscribe_camera_status(self):
        # Anti-registration notification
        event_subscribe = pointer(GENICAM_EventSubscribe())
        event_subscribe_info = GENICAM_EventSubscribeInfo()
        event_subscribe_info.pCamera = pointer(self.campointer)
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

    def subscribe_camera_status(self):
        # Registration notification
        event_subscribe = pointer(GENICAM_EventSubscribe())
        event_subscribe_info = GENICAM_EventSubscribeInfo()
        event_subscribe_info.pCamera = pointer(self.campointer)
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

    def open_camera(self):
        n_ret = self.campointer.connect(self.campointer, c_int(GENICAM_ECameraAccessPermission.accessPermissionControl))
        if n_ret != 0:
            print("camera connect fail!")
            return -1
        else:
            print("camera connect success.")
        n_ret = self.subscribe_camera_status()
        if n_ret != 0:
            print("subscribeCameraStatus fail!")
            return -1
        return 0

    def get_xml(self):
        xml = c_char_p()
        n_ret = self.campointer.downLoadGenICamXML(self.campointer, xml)
        print(n_ret)
        if n_ret != 0:
            print("camera xml get fail!")
            return -1
        else:
            print("camera xml success.")
            print(xml.value)

    def close_camera(self):
        n_ret = self.unsubscribe_camera_status()
        if n_ret != 0:
            print("unsubscribeCameraStatus fail!")
            return -1
        n_ret = self.campointer.disConnect(byref(self.campointer))
        if n_ret != 0:
            print("disConnect camera fail!")
            return -1
        return 0

    def check_valid_frame(self, frame, image_source):
        n_ret = frame.contents.valid(frame)
        if n_ret != 0:
            print("frame is invalid!")
            frame.contents.release(frame)
            # Release related resources
            image_source.contents.release(self.campointer)
            return -1

    def deactivate(self):
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

        n_ret = self.close_camera()
        if n_ret != 0:
            print("closeCamera fail")
            self.image_source.contents.release(self.image_source)
            return -1
        self.image_source.contents.release(self.image_source)

    def activate(self):
        # connect to the camera
        self.acqCtrl = pointer(GENICAM_AcquisitionControl())
        acq_ctrl_info = GENICAM_AcquisitionControlInfo()
        acq_ctrl_info.pCamera = pointer(self.campointer)
        n_ret = GENICAM_createAcquisitionControl(pointer(acq_ctrl_info), byref(self.acqCtrl))
        if n_ret != 0:
            print("create AcquisitionControl fail!")
            return -1
        # create the streaming source
        print('creating a stream source')
        self.image_source = pointer(GENICAM_StreamSource())
        stream_source_info = GENICAM_StreamSourceInfo()
        stream_source_info.channelId = 0
        stream_source_info.pCamera = pointer(self.campointer)
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
                                                         c_int(GENICAM_EGrabStrategy.grabStrartegySequential))
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
    def enumerate_cameras():  # also get xml?
        system = pointer(GENICAM_System())
        n_ret = GENICAM_getSystemInstance(byref(system))
        if n_ret != 0:
            print("getSystemInstance fail!")
            return None, None
        camera_list = pointer(GENICAM_Camera())
        camera_cnt = c_uint()
        camera_xml = c_char_p()
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

    def connect_device_control(self):
        device_control = pointer(GENICAM_DeviceControl())
        device_control_info = GENICAM_DeviceControlInfo()
        device_control_info.pCamera = pointer(self.campointer)
        n_ret = GENICAM_createDeviceControl(byref(device_control_info), byref(device_control))
        if n_ret != 0:
            print("Failed to connect to control")
            device_control.contents.release(device_control)
        string_parser = pointer(GENICAM_StringNode())
        string_parser_info = GENICAM_StringNodeInfo()
        string_parser_info.pCamera = pointer(self.campointer)
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

    def get_usb_info(self):
        # This is test code and I'm not certain of the benefit as yet
        print("GETTING USB INTERFACE INFO!!")
        print("GETTING USB CAMERA INFO!!")
        # usb_camera = pointer(camera)
        usb_camera = pointer(GENICAM_UsbCamera())
        usb_camera_info = GENICAM_UsbCameraInfo()
        usb_camera_info.pCamera = pointer(self.campointer)
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
            fname = f"{(camera.getVendorName(camera)).decode('utf-8')}_{(camera.getModelName(camera)).decode('utf-8')}"
            zippedfilename = f"{fname}.zip"
            xmlfile = f"{fname}.xml"
            charzip = c_char_p(zippedfilename.encode())
            camera.connect(camera, c_int(GENICAM_ECameraAccessPermission.accessPermissionControl))
            camera.downLoadGenICamXML(camera, charzip)
            with zipfile.ZipFile(zippedfilename, 'r') as zip_ref:
                filecount = zip_ref.namelist()
                print(f"fc is {filecount[0]}")
                zip_ref.extract(filecount[0])
                os.rename(filecount[0], xmlfile)
                self.xml_property_file = xmlfile
            os.remove(zippedfilename)
            print("self.xml_property_file " + self.xml_property_file)

            print("GENICAM is " + charzip.value.decode('utf-8'))
            # camera.disConnect(camera)
        self.campointer = camera_list[0]  # this is the actual camera
        # self.connect_device_control(self.campointer)
        # self.property_get("ChunkEnable")
        self.get_usb_info()
        # open the camera
        # query this camera?
        n_ret = self.open_camera()  # opens the camera
        if n_ret != 0:  # handles the camera open failure
            print("openCamera fail.")
        else:
            print("Camera Opened")
            return camera_list[0]

    def grab_image(self):
        trig_software_cmd_node = self.acqCtrl.contents.triggerSoftware(self.acqCtrl)
        n_ret = trig_software_cmd_node.execute(byref(trig_software_cmd_node))
        if n_ret != 0:
            print(f"Execute triggerSoftware fail => {n_ret} ")
            # 释放相关资源 - Release related resources
            trig_software_cmd_node.release(byref(trig_software_cmd_node))
            self.acqCtrl.contents.release(self.acqCtrl)
            self.image_source.contents.release(self.image_source)
            return -1
        # print('2')
        frame = pointer(GENICAM_Frame())
        # print(datetime.datetime.now().strftime("%y%m%d%H%M%S"))
        n_ret = self.image_source.contents.getFrame(self.image_source, byref(frame), c_uint(1000))

        if n_ret != 0:
            print("SoftTrigger getFrame fail! timeOut [1000]ms")
            # Release related resources
            self.deactivate()
            self.image_source.contents.release(self.image_source)
            return -1
        else:
            # print("SoftTrigger getFrame success BlockId = " + str(frame.contents.getBlockId(frame)))
            # print("get frame time: " + str(datetime.datetime.now()))
            trig_software_cmd_node.release(byref(trig_software_cmd_node))
            self.check_valid_frame(frame, self.image_source)
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

    def property_get_temp(self):  # this is going to be for type string....setting must be of type string
        print('\n\n\nGetting info about setting')
        # setting_to_get = setting.encode()  # convert to bytes
        # set the right pointer
        temp_node_pointer = pointer(GENICAM_DoubleNode())
        temp_node_info = GENICAM_DoubleNodeInfo()
        temp_node_info.pCamera = pointer(self.campointer)
        temp_node_info.attrName = b'DeviceTemperature'
        n_ret = GENICAM_createDoubleNode(byref(temp_node_info), byref(temp_node_pointer))
        if n_ret != 0:
            print("Unable to access {}".format(temp_node_info.attrName))
            return -1
        cam_temp = c_double()
        n_ret = temp_node_pointer.contents.getValue(temp_node_pointer, byref(cam_temp))
        if n_ret != 0:
            print("Unable to get the temp value ")
            temp_node_pointer.contents.release(temp_node_pointer)
            return -1
        print("The temp node was reported as {}".format(cam_temp.value))
        temp_node_pointer.contents.release(temp_node_pointer)

    def genicam_worker(self, camera_parameter, parameter_value, camera_xml_file):
        # return the command type, a pointer and a pointers info
        # if the parameter value is empty, the go into read mode
        node_pointer = None
        node_pointer_info = None
        ctypes_value = None
        node_type = 0  # default - not string and not enum
        n_ret = -99
        tree = ETree.parse(camera_xml_file)
        # pf is a prefix -> https://www.w3schools.com/xml/xml_namespaces.asp
        pf = '{http://www.genicam.org/GenApi/Version_1_1}'
        root = tree.getroot()
        # LEVEL 1 this finds all the headings for the camera properties (lines 5 - 19 in the xml file)
        property_headings = root.findall(f"./{pf}Group[@Comment='Root']/{pf}Category[@Name='Root']/{pf}pFeature")
        # LEVEL 2 Iterate through those headings where the target is  ->pFeature
        # we are looking for the pFeature (property heading name) in the group commend and category name
        for property_heading in property_headings:
            xml_groups = root.findall(f"./{pf}Group[@Comment='{property_heading.text}']")
            # find the subtag where the
            for xmlgroup in xml_groups:
                types = xmlgroup.iter()
                for subtag in types:
                    if subtag.tag == f'{pf}Enumeration':
                        enumsubtags = subtag.iter(f"{pf}Visibility")
                        for subtags in enumsubtags:
                            if subtags.text != "Invisible":
                                # # print(f'camera_parameter => {camera_parameter} | attribute => {subtag.attrib["Name"]}')
                                if camera_parameter == subtag.attrib["Name"]:
                                    print('WORKER NODE TYPE 2')
                                    print(f'property heading is {property_heading.text}')
                                    print(f'    camera_property_heading {xmlgroup.attrib["Comment"]}')
                                    print(f'        subtag attribute {subtag.attrib["Name"]}')
                                    print(f'        subtag attribute type {self.remove_namespace(subtag.tag)}')
                                    print(f'            Visibility {subtags.text}')
                                    node_type = 2
                                    node_pointer = pointer(GENICAM_EnumNode())
                                    node_pointer_info = GENICAM_EnumNodeInfo()
                                    node_pointer_info.pCamera = pointer(self.campointer)
                                    node_pointer_info.attrName = str(camera_parameter).encode()
                                    if parameter_value is not None:  #set parameter that we have
                                        ctypes_value = parameter_value.encode()
                                    else:  # get parameter value from the camera
                                        ctypes_value = c_char_p()  # this is notworking
                                    n_ret = GENICAM_createEnumNode(byref(node_pointer_info), byref(node_pointer))
                                    break

                    elif subtag.tag == f'{pf}Integer':
                        intsubtags = subtag.iter(f"{pf}Visibility")
                        for subtags in intsubtags:
                            if subtags.text != "Invisible":
                                # # print(f'camera_parameter => {camera_parameter} | attribute => {subtag.attrib["Name"]}')
                                if camera_parameter == subtag.attrib["Name"]:
                                    # print(f'property heading is {property_heading.text}')
                                    # print(f'    camera_property_heading {xmlgroup.attrib["Comment"]}')
                                    # print(f'        subtag attribute {subtag.attrib["Name"]}')
                                    # print(f'        subtag attribute type {self.remove_namespace(subtag.tag)}')
                                    # print(f'            Visibility {subtags.text}')
                                    # print(f'                Target value is {parameter_value}')
                                    node_pointer = pointer(GENICAM_IntNode())
                                    node_pointer_info = GENICAM_IntNodeInfo()
                                    node_pointer_info.pCamera = pointer(self.campointer)
                                    node_pointer_info.attrName = str(camera_parameter).encode()
                                    if parameter_value is not None:  #set parameter that we have
                                        ctypes_value = c_longlong(parameter_value)
                                    else:  # get parameter value from the camera
                                        ctypes_value = c_longlong()  # declare as empty
                                    n_ret = GENICAM_createIntNode(byref(node_pointer_info), byref(node_pointer))
                                    break

                    elif subtag.tag == f'{pf}Float':
                        floatsubtags = subtag.iter(f"{pf}Visibility")
                        for subtags in floatsubtags:
                            if subtags.text != "Invisible":
                                # # print(f'camera_parameter => {camera_parameter} | attribute => {subtag.attrib["Name"]}')
                                if camera_parameter == subtag.attrib["Name"]:
                                    # print(f'property heading is {property_heading.text}')
                                    # print(f'    camera_property_heading {xmlgroup.attrib["Comment"]}')
                                    # print(f'        subtag attribute {subtag.attrib["Name"]}')
                                    # print(f'        subtag attribute type {self.remove_namespace(subtag.tag)}')
                                    # print(f'            Visibility {subtags.text}')
                                    node_pointer = pointer(GENICAM_DoubleNode())
                                    node_pointer_info = GENICAM_DoubleNodeInfo()
                                    node_pointer_info.pCamera = pointer(self.campointer)
                                    node_pointer_info.attrName = str(camera_parameter).encode()
                                    if parameter_value is not None:  #set parameter that we have
                                        ctypes_value = c_double(parameter_value)
                                    else:  # get parameter value from the camera
                                        ctypes_value = c_double()  # declare as empty
                                    n_ret = GENICAM_createDoubleNode(byref(node_pointer_info), byref(node_pointer))
                                    break

                    elif subtag.tag == f'{pf}Boolean':
                        boolsubtags = subtag.iter(f"{pf}Visibility")
                        for subtags in boolsubtags:
                            if subtags.text != "Invisible":
                                # # print(f'camera_parameter => {camera_parameter} | attribute => {subtag.attrib["Name"]}')
                                if camera_parameter == subtag.attrib["Name"]:
                                    # print(f'property heading is {property_heading.text}')
                                    # print(f'    camera_property_heading {xmlgroup.attrib["Comment"]}')
                                    # print(f'        subtag attribute {subtag.attrib["Name"]}')
                                    # print(f'        subtag attribute type {self.remove_namespace(subtag.tag)}')
                                    # print(f'            Visibility {subtags.text}')
                                    # node_type = 3
                                    node_pointer = pointer(GENICAM_BoolNode())
                                    node_pointer_info = GENICAM_BoolNodeInfo()
                                    node_pointer_info.pCamera = pointer(self.campointer)
                                    node_pointer_info.attrName = str(camera_parameter).encode()
                                    if parameter_value is not None:  #set parameter that we have
                                        ctypes_value = c_uint(parameter_value)
                                    else:  # get parameter value from the camera
                                        ctypes_value = c_uint()  # declare as empty
                                    n_ret = GENICAM_createBoolNode(byref(node_pointer_info), byref(node_pointer))
                                    break

                    elif subtag.tag == f'{pf}StringReg':
                        stringsubtags = subtag.iter(f"{pf}Visibility")
                        for subtags in stringsubtags:
                            if subtags.text != "Invisible":
                                # # print(f'camera_parameter => {camera_parameter} | attribute => {subtag.attrib["Name"]}')
                                if camera_parameter == subtag.attrib["Name"]:
                                    print('WORKER NODE TYPE 1')
                                    print(f'property heading is {property_heading.text}')
                                    print(f'    camera_property_heading {xmlgroup.attrib["Comment"]}')
                                    print(f'        subtag attribute {subtag.attrib["Name"]}')
                                    print(f'        subtag attribute type {self.remove_namespace(subtag.tag)}')
                                    print(f'            Visibility {subtags.text}')
                                    print(f'                Target value is {parameter_value}')
                                    node_type = 1
                                    node_pointer = pointer(GENICAM_StringNode())
                                    node_pointer_info = GENICAM_StringNodeInfo()
                                    node_pointer_info.pCamera = pointer(self.campointer)
                                    node_pointer_info.attrName = camera_parameter.encode()
                                    if parameter_value is not None:  # set parameter that we have
                                        ctypes_value = c_char_p(parameter_value.encode())  # This works
                                    else:  # get parameter value from the camera
                                        ctypes_value = c_char_p()  # declare as empty
                                        # Line 839 in MVSDK.py - the future call of getValue requires a POINTER to a
                                        # c_uint - need to understand how this works as the get function is not working
                                        # here

                                    n_ret = GENICAM_createStringNode(byref(node_pointer_info), byref(node_pointer))
                                    break

                    elif subtag.tag == f'{pf}Command':
                        commandsubtags = subtag.iter(f"{pf}Visibility")
                        for subtags in commandsubtags:
                            if subtags.text != "Invisible":
                                # # print(f'camera_parameter => {camera_parameter} | attribute => {subtag.attrib["Name"]}')
                                if camera_parameter == subtag.attrib["Name"]:
                                    # print(f'property heading is {property_heading.text}')
                                    # print(f'    camera_property_heading {xmlgroup.attrib["Comment"]}')
                                    # print(f'        subtag attribute type {self.remove_namespace(subtag.tag)}')
                                    # print(f'        subtag attribute {subtag.attrib["Name"]}')
                                    # print(f'            Visibility {subtags.text}')
                                    node_pointer = pointer(GENICAM_CmdNode())
                                    node_pointer_info = GENICAM_CmdNodeInfo()
                                    node_pointer_info.pCamera = pointer(self.campointer)
                                    node_pointer_info.attrName = str(camera_parameter).encode()
                                    if parameter_value is not None:
                                        ctypes_value = c_char_p(parameter_value.encode())  # this would be "Execute"
                                    else:
                                        ctypes_value = c_char_p()  # declare as empty
                                        # I dont see why this would even be required because there is only execution
                                        # reality is we should be telling the user, there is nothing to read here
                                        # but after investigation, our function is doing its job - we get "NotAvailable"
                                        # when called during grabbing and not readable when called before camera
                                        # image grabbing. In conclusion, I dont think we will ever get to this point and
                                        # wonder if its even worth having...
                                    n_ret = GENICAM_createCmdNode(byref(node_pointer_info), byref(node_pointer))
                                    break
        return n_ret, node_pointer, node_pointer_info, ctypes_value, node_type

    @staticmethod
    def remove_namespace(tag_with_namespace):
        tag_minus_namespace = re.sub("{(.*?)}", '', tag_with_namespace)
        return tag_minus_namespace

    def isvalid(self, node_pointer, parameter_value):
        n_ret = node_pointer.contents.isValid(node_pointer)
        if n_ret != 0:
            self.releasecontents(node_pointer, parameter_value)
            print("Not Valid")
            return False
        else:
            return True

    def isavailable(self, node_pointer, parameter_value):
        n_ret = node_pointer.contents.isAvailable(node_pointer)
        if n_ret != 0:
            self.releasecontents(node_pointer, parameter_value)
            print("Not Available")
            return False
        else:
            return True

    def iswriteable(self, node_pointer, parameter_value):
        n_ret = node_pointer.contents.isWriteable(node_pointer, parameter_value)
        if n_ret != 0:
            self.releasecontents(node_pointer, parameter_value)
            print("Not Writeable")
            return False
        else:
            return True

    def isreadable(self, node_pointer, parameter_value):
        n_ret = node_pointer.contents.isReadable(node_pointer)
        print(f"is readable {n_ret}")
        if n_ret != 0:
            self.releasecontents(node_pointer, parameter_value)
            print("Not Readable")
            return False
        else:
            return True

    def get_value(self, node_pointer, camera_parameter, parameter_value, node_type):  # keeping set and get apart here because it might be too messy
        print(f"camera parameter {camera_parameter}")
        print(f"node_pointer => {type(node_pointer)}|parameter_value => {parameter_value.value}")
        print(f'node type in get value is {node_type}')
        if self.isvalid(node_pointer, parameter_value):
            if self.isavailable(node_pointer, parameter_value):
                if self.isreadable(node_pointer, parameter_value):
                    # get the type instead
                    if node_type == 2:  # enums here
                        print("NODE TYPE 2")
                        third = c_uint()  # below, parameter_value is ctypes_value = c_char_p()
                        n_ret = node_pointer.contents.getValueSymbol(node_pointer, byref(parameter_value), byref(third))  #TODO enum this is not working
                        if n_ret != 0:
                            print(f"Could not read a ENUM value {n_ret}")
                            print(f"You are seeing this result because I havent managed to get this to work yet")
                            print("This are (EnumNode) needs work")
                            self.releasecontents(node_pointer, parameter_value)
                            return -1
                        else:
                            self.releasecontents(node_pointer, parameter_value)
                            return parameter_value.value
                    elif node_type == 1:  # stringreg here
                        print("NODE TYPE 1")
                        mycuint = c_uint(255)
                        print("GOT THIS")
                        n_ret = node_pointer.contents.getValue(node_pointer,  parameter_value, byref(mycuint))  #TODO string this is not working
                        print(f"parameter value is {parameter_value.value}")
                        if n_ret != 0:
                            print(f"Could not read a string value {n_ret}")
                            print(f"You are seeing this result because I havent managed to get this to work yet")
                            print("This are (StringReg) needs work")
                            self.releasecontents(node_pointer, parameter_value)
                            return -1
                        else:
                            self.releasecontents(node_pointer, parameter_value)
                            return parameter_value.value
                    else:
                        print("NODE TYPE 0")
                        n_ret = node_pointer.contents.getValue(node_pointer, byref(parameter_value))
                        if n_ret != 0:
                            print(f"Could not read a value")
                            self.releasecontents(node_pointer, parameter_value)
                            return -1
                        else:
                            # print(f"Successfully grabbed the value -> {parameter_value.value}")
                            self.releasecontents(node_pointer, parameter_value)
                            return parameter_value.value
                else:
                    print("Not Readable")
                    return -2
            else:
                print("Not Available")
                return -3
        else:
            print("Not Valid")
            return -4

    def set_value(self, node_pointer, parameter_value, node_type):
        # print(f"node_pointer => {node_pointer}|parameter_value => {parameter_value}")
        if self.isvalid(node_pointer, parameter_value):
            if self.isavailable(node_pointer, parameter_value):
                if self.iswriteable(node_pointer, parameter_value):
                    if node_type is 2:  # an enum
                        n_ret = node_pointer.contents.setValueBySymbol(node_pointer, parameter_value)
                    else:  # strings, ints, floats, bools....
                        n_ret = node_pointer.contents.setValue(node_pointer, parameter_value)

                    if n_ret != 0:
                        print(f"Could not set the value -> {parameter_value}")
                        self.releasecontents(node_pointer, parameter_value)
                        return -1
                    else:
                        print(f"Successfully set the value -> {parameter_value}")
                        self.releasecontents(node_pointer, parameter_value)
                        return 0
                else:
                    print("Not Writeable")
                    return -2
            else:
                print("Not Available")
                return -3
        else:
            print("Not Valid")
            return -4
    @staticmethod
    def releasecontents(node_pointer, parameter_value):
        node_pointer.contents.release(node_pointer)

    def property_getset(self, camera_parameter, parameter_value):  # type will be grabbed from the xml
        # print(f"camera parameter is  {camera_parameter}")
        # print(f"parameter_value is  {parameter_value}")
        # print(f"xml is is  {self.xml_property_file}")

        # this sets up the camera function, works out what type of command is required, adds the camera then returns
        # it all ready to apply or read (in our case apply) the value
        result, node_pointer, node_pointer_info, p_value, node_type = self.genicam_worker(camera_parameter, parameter_value, self.xml_property_file)
        if result != 0:  # is this hasnt worked, no point moving on from here....
            print(f"setting up the call to the camera has failed => {result}")
        else:
            if parameter_value is None:  # we want to read what it is
                # print(f"Get value of {camera_parameter} -> a work in progress")
                result = self.get_value(node_pointer, camera_parameter, p_value, node_type)  # this need to be the camera parameter
                return result
            elif parameter_value is "Execute":  # specifically for an execute call...
                print(f"Executing command {camera_parameter} -> a work in progress")
                # ToDo: Get the command executor working
            else:  # all other - which is set value
                final = self.set_value(node_pointer, p_value, node_type)
                print(f'final {final}')

                # check validity, check availability & check writeable

    def set_roi(self, offset_x, offset_y, n_width, n_height):  # another example from the Contrastech Demo
        # set the pointer
        width_max_node = pointer(GENICAM_IntNode())
        # set the info associated with it
        width_max_node_info = GENICAM_IntNodeInfo()
        # set the pointer to the camera
        width_max_node_info.pCamera = pointer(self.campointer)
        # set the attribute name you are chasing
        width_max_node_info.attrName = b"WidthMax"
        # create the note
        n_ret = GENICAM_createIntNode(byref(width_max_node_info), byref(width_max_node))
        if n_ret != 0:
            print("create WidthMax Node fail!")
            return -1
        # declare the type of ctype type....
        original_width = c_longlong()
        # return the value by doing the following
        # this should populate your variable with the information you want..
        n_ret = width_max_node.contents.getValue(width_max_node, byref(original_width))
        if n_ret != 0:
            print("widthMaxNode getValue fail!")
            # 释放相关资源 - Release related resources
            width_max_node.contents.release(width_max_node)
            return -1

        # Release related resources
        width_max_node.contents.release(width_max_node)

        # 获取原始的高度
        height_max_node = pointer(GENICAM_IntNode())
        height_max_node_info = GENICAM_IntNodeInfo()
        height_max_node_info.pCamera = pointer(self.campointer)
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
        width_node = pointer(GENICAM_IntNode())
        width_node_info = GENICAM_IntNodeInfo()
        width_node_info.pCamera = pointer(self.campointer)
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
        height_node = pointer(GENICAM_IntNode())
        height_node_info = GENICAM_IntNodeInfo()
        height_node_info.pCamera = pointer(self.campointer)
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
        offset_x_node = pointer(GENICAM_IntNode())
        offset_x_node_info = GENICAM_IntNodeInfo()
        offset_x_node_info.pCamera = pointer(self.campointer)
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
        offset_y_node = pointer(GENICAM_IntNode())
        offset_y_node_info = GENICAM_IntNodeInfo()
        offset_y_node_info.pCamera = pointer(self.campointer)
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

    # this will be called on the fly to return the property type
