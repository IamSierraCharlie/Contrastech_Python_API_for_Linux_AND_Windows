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
        self.cam = None
        self.t = None
        self.info = None
        self.acqCtrl = None
        self.max_width = None
        self.max_height = None

        self.connectCallBackFunc = connectCallBack(self.deviceLinkNotify)
        self.connectCallBackFuncEx = connectCallBackEx(self.deviceLinkNotify)
        self.frameCallbackFunc = callbackFunc(self.onGetFrame)
        self.create_camera_instance()  # instantiated upon calling the camera Class
        offset_x, offset_y = self.check_image_dimension_validity(sensor_width, sensor_height, img_width, img_height)
        self.set_roi(self.cam, offset_x, offset_y, img_width, img_height)

    @staticmethod # this function reports the camera status.  It will output issues to the cmd prompt
    def deviceLinkNotify(connectArg, linkInfo):
        if EVType.offLine == connectArg.contents.m_event:
            print("camera is off line, userInfo [%s]" % c_char_p(linkInfo).value)
        elif EVType.onLine == connectArg.contents.m_event:
            print("camera is on line, userInfo [%s]" % c_char_p(linkInfo).value)

    @staticmethod
    def enumCameras():
        system = pointer(GENICAM_System())
        nRet = GENICAM_getSystemInstance(byref(system))
        if nRet != 0:
            print("getSystemInstance fail!")
            return None, None

        cameraList = pointer(GENICAM_Camera())
        cameraCnt = c_uint()
        nRet = system.contents.discovery(system, byref(cameraList), byref(cameraCnt),
                                         c_int(GENICAM_EProtocolType.typeAll))
        if nRet != 0:
            print("discovery fail!")
            return None, None
        elif cameraCnt.value < 1:
            print("discovery no camera!")
            return None, None
        else:
            print("cameraCnt: " + str(cameraCnt.value))
            return cameraCnt.value, cameraList

    @staticmethod
    def onGetFrame(frame):
        nRet = frame.contents.valid(frame)
        if nRet != 0:
            print("frame is invalid!")
            # Release driver image cache resources
            frame.contents.release(frame)
            return

        #print("BlockId = %d" % (frame.contents.getBlockId(frame)))
        frame.contents.release(frame)

    # Unregister camera connection status callback
    def unsubscribeCameraStatus(self):
        # Anti-registration notification
        eventSubscribe = pointer(GENICAM_EventSubscribe())
        eventSubscribeInfo = GENICAM_EventSubscribeInfo()
        eventSubscribeInfo.pCamera = pointer(self.cam)
        nRet = GENICAM_createEventSubscribe(byref(eventSubscribeInfo), byref(eventSubscribe))
        if nRet != 0:
            print("create eventSubscribe fail!")
            return -1

        nRet = eventSubscribe.contents.unsubscribeConnectArgs(eventSubscribe, self.connectCallBackFunc, g_cameraStatusUserInfo)
        if nRet != 0:
            print("unsubscribeConnectArgs fail!")
            # Release related resources
            eventSubscribe.contents.release(eventSubscribe)
            return -1
        # Relevant resources need to be released when they are no longer used
        eventSubscribe.contents.release(eventSubscribe)
        return 0

    def subscribeCameraStatus(self):
        # Registration notification
        eventSubscribe = pointer(GENICAM_EventSubscribe())
        eventSubscribeInfo = GENICAM_EventSubscribeInfo()
        eventSubscribeInfo.pCamera = pointer(self.cam)
        nRet = GENICAM_createEventSubscribe(byref(eventSubscribeInfo), byref(eventSubscribe))
        if nRet != 0:
            print("create eventSubscribe fail!")
            return -1

        nRet = eventSubscribe.contents.subscribeConnectArgs(eventSubscribe, self.connectCallBackFunc, g_cameraStatusUserInfo)
        if nRet != 0:
            print("subscribeConnectArgsEx fail!")
            # Release related resources
            eventSubscribe.contents.release(eventSubscribe)
            return -1

        # Relevant resources need to be released when they are no longer used
        eventSubscribe.contents.release(eventSubscribe)
        return 0

    def openCamera(self):
        nRet = self.cam.connect(self.cam, c_int(GENICAM_ECameraAccessPermission.accessPermissionControl))
        if nRet != 0:
            print("camera connect fail!")
            return -1
        else:
            print("camera connect success.")

        nRet = self.subscribeCameraStatus()
        if nRet != 0:
            print("subscribeCameraStatus fail!")
            return -1
        return 0

    def closeCamera(self):
        nRet = self.unsubscribeCameraStatus()
        if nRet != 0:
            print("unsubscribeCameraStatus fail!")
            return -1

        nRet = self.cam.disConnect(byref(self.cam))
        if nRet != 0:
            print("disConnect camera fail!")
            return -1

        return 0

    @staticmethod
    def check_valid_frame(cam, frame, image_source):
        nRet = frame.contents.valid(frame)
        if nRet != 0:
            print("frame is invalid!")
            frame.contents.release(frame)
            # Release related resources
            image_source.contents.release(cam)
            return -1

    def deactivate(self):
        print('should deactivate')
        nRet = self.image_source.contents.stopGrabbing(self.image_source)
        if nRet != 0:
            print("stopGrabbing fail!")
            # Release related resourcesrces
            self.image_source.contents.release(self.image_source)
            return -1
            # Turn off trigger mode - camera light should stop flashing
        trigModeEnumNode = self.acqCtrl.contents.triggerMode(self.acqCtrl)
        nRet = trigModeEnumNode.setValueBySymbol(byref(trigModeEnumNode), b"Off")
        if nRet != 0:
            print("set TriggerMode value [On] fail!")
            # Release related resources
            trigModeEnumNode.release(byref(trigModeEnumNode))
            self.acqCtrl.contents.release(self.acqCtrl)
            return -1

        nRet = self.closeCamera()
        if nRet != 0:
            print("closeCamera fail")
            self.image_source.contents.release(self.image_source)
            return -1
        self.image_source.contents.release(self.image_source)

    def activate(self):
        # connect to the camera
        acqCtrlInfo = GENICAM_AcquisitionControlInfo()
        acqCtrlInfo.pCamera = pointer(self.cam)
        self.acqCtrl = pointer(GENICAM_AcquisitionControl())
        nRet = GENICAM_createAcquisitionControl(pointer(acqCtrlInfo), byref(self.acqCtrl))
        if nRet != 0:
            print("create AcquisitionControl fail!")
            return -1

        # create the streaming source
        print('creating a stream source')
        streamSourceInfo = GENICAM_StreamSourceInfo()
        streamSourceInfo.channelId = 0
        streamSourceInfo.pCamera = pointer(self.cam)
        self.image_source = pointer(GENICAM_StreamSource())
        nRet = GENICAM_createStreamSource(pointer(streamSourceInfo), byref(self.image_source))
        if nRet != 0:
            print("create image_source fail!")
            return -1
        # attach grabbing
        nRet = self.image_source.contents.attachGrabbing(self.image_source, self.frameCallbackFunc)
        if nRet != 0:
            print("attachGrabbing fail!")
            self.image_source.contents.release(self.image_source)
            return -1

        # Start grabbing images
        nRet = self.image_source.contents.startGrabbing(self.image_source, c_ulonglong(0),
                                                        c_int(GENICAM_EGrabStrategy.grabStrategySequential))
        if nRet != 0:
            print("startGrabbing fail!")
            # Release related resources
            self.image_source.contents.release(self.image_source)
            return -1

        # detach from grabbing - this step is necessary in order to successfully grab images
        nRet = GENICAM_createAcquisitionControl(pointer(acqCtrlInfo), byref(self.acqCtrl))
        if nRet != 0:
            print("create AcquisitionControl fail!")
            self.image_source.contents.release(self.image_source)
            return -1
        nRet = self.image_source.contents.detachGrabbing(self.image_source, self.frameCallbackFunc)
        if nRet != 0:
            print("detachGrabbing fail!")
            self.image_source.contents.release(self.image_source)
            return -1

    def create_camera_instance(self):
        cameraCnt, cameraList = self.enumCameras()
        if cameraCnt is None:  # no camera handler
            print('No camera handler')
        if cameraCnt > 1:
            print('Multiple cameras')
        for index in range(0, cameraCnt):  # camera details
            print('Getting camera details\n')
            camera = cameraList[index]
            print("\nCamera Id = " + str(index))
            print("Key           = " + str(camera.getKey(camera)))
            print("vendor name   = " + str(camera.getVendorName(camera)))
            print("Model  name   = " + str(camera.getModelName(camera)))
            print("Serial number = " + str(camera.getSerialNumber(camera)))

        self.cam = cameraList[0]  # this is the actual camera
        # open the camera
        nRet = self.openCamera()  # opens the camera
        if nRet != 0:  # handles the camera open failure
            print("openCamera fail.")

    def grab_image(self):
        trigSoftwareCmdNode = self.acqCtrl.contents.triggerSoftware(self.acqCtrl)
        nRet = trigSoftwareCmdNode.execute(byref(trigSoftwareCmdNode))
        if nRet != 0:
            print("Execute triggerSoftware fail!")
            # 释放相关资源 - Release related resources
            trigSoftwareCmdNode.release(byref(trigSoftwareCmdNode))
            self.acqCtrl.contents.release(self.acqCtrl)
            self.image_source.contents.release(self.image_source)
            return -1
        #print('2')
        frame = pointer(GENICAM_Frame())
        # print(datetime.datetime.now().strftime("%y%m%d%H%M%S"))
        nRet = self.image_source.contents.getFrame(self.image_source, byref(frame), c_uint(1000))

        if nRet != 0:
            print("SoftTrigger getFrame fail! timeOut [1000]ms")
            # Release related resources
            self.deactivate()
            self.image_source.contents.release(self.image_source)
            return -1
        else:
            #print("SoftTrigger getFrame success BlockId = " + str(frame.contents.getBlockId(frame)))
            #print("get frame time: " + str(datetime.datetime.now()))
            trigSoftwareCmdNode.release(byref(trigSoftwareCmdNode))

            self.check_valid_frame(self.cam, frame, self.image_source)
            #print("grabbed BlockId = %d" % (frame.contents.getBlockId(frame)))
            #print("Chunk = %d" % (frame.contents.getChunkCount(frame)))

        # Copy the raw data image out
        imageSize = frame.contents.getImageSize(frame)
        buffAddr = frame.contents.getImage(frame)
        frameBuff = c_buffer(b'\0', imageSize)
        memmove(frameBuff, c_char_p(buffAddr), imageSize)
        convertParams = IMGCNV_SOpenParam()
        convertParams.dataSize = imageSize
        convertParams.height = frame.contents.getImageHeight(frame)
        convertParams.width = frame.contents.getImageWidth(frame)
        convertParams.paddingX = frame.contents.getImagePaddingX(frame)
        convertParams.paddingY = frame.contents.getImagePaddingY(frame)
        convertParams.pixelForamt = frame.contents.getImagePixelFormat(frame)

        print('dataSize', imageSize)
        print('height', frame.contents.getImageHeight(frame))
        print('width', frame.contents.getImageWidth(frame))
        print('paddingX', frame.contents.getImagePaddingX(frame))
        print('paddingY', frame.contents.getImagePaddingY(frame))
        print('pixelFormat', frame.contents.getImagePixelFormat(frame))

        # Release driver image cache
        frame.contents.release(frame)
        rgbBuff = c_buffer(b'\0', convertParams.height * convertParams.width * 3)
        rgbSize = c_int()
        nRet = IMGCNV_ConvertToRGB24(cast(frameBuff, c_void_p), byref(convertParams), cast(rgbBuff, c_void_p), byref(rgbSize))

        if nRet != 0:
            print("image convert fail! errorCode = " + str(nRet))
            # 释放相关资源 - Release related resources
            self.image_source.contents.release(self.image_source)
            return -1

        final = np.reshape(np.frombuffer(bytearray(string_at(rgbBuff,
                                                             self.img_channels * self.img_height * self.img_width)),
                                         dtype=np.uint8), (self.img_height, self.img_width,  self.img_channels))
        return final

    def change_setting(self, setting, option):
        print('\n\n\nInstance is: {}'.format(type(option)))
        #option = option.encode()
        setting = setting.encode()
        if isinstance(option, int) and not isinstance(option, bool):  # A Number
            print('changing with settings num')
            self.settings_num(setting, int_option=option)
        elif isinstance(option, str):  # A string - encode to bytes
            print('changing with settings_str')
            self.settings_str(setting, option.encode())
        elif isinstance(option, bool):  # A Boolean
            print('changing with settings_bool')
            self.settings_bool(setting, option)

        else:
            print('unknown var {} from setting {} - unable to handle this'.format(option, setting))
            exit()

    def settings_str(self, setting, option):
        setting_char_EnumMode = pointer(GENICAM_EnumNode())
        setting_char_EnumModeInfo = GENICAM_EnumNodeInfo()
        setting_char_EnumModeInfo.pCamera = pointer(self.cam)
        setting_char_EnumModeInfo.attrName = setting
        nRet = GENICAM_createEnumNode(byref(setting_char_EnumModeInfo), byref(setting_char_EnumMode))
        if nRet != 0:
            print("Unable to access {}".format(setting))
            # Release related resources
            self.image_source.contents.release(self.image_source)
            return -1
        # change setting_char_ mode to continuous
        print('Changing {} to {}'.format(setting, option))
        nRet = setting_char_EnumMode.contents.setValueBySymbol(setting_char_EnumMode, option)
        if nRet != 0:
            print('Failed!')
            # Release related resources
            setting_char_EnumMode.contents.release(setting_char_EnumMode)
            self.image_source.contents.release(self.image_source)  # this line dumps everything
            return -1
        else:
            print('Success!')
        setting_char_EnumMode.contents.release(setting_char_EnumMode)

    def settings_num(self, setting, int_option):  # almost straight from the contrastech demo
        setting_num_Node = pointer(GENICAM_DoubleNode())
        setting_num_NodeInfo = GENICAM_DoubleNodeInfo()
        setting_num_NodeInfo.pCamera = pointer(self.cam)
        setting_num_NodeInfo.attrName = setting
        nRet = GENICAM_createDoubleNode(byref(setting_num_NodeInfo), byref(setting_num_Node))
        if nRet != 0:
            print("create {} Node fail!".format(setting))
            return -1
        nRet = setting_num_Node.contents.setValue(setting_num_Node, c_double(int_option))
        if nRet != 0:
            print("set {} to {} fail!".format(setting, int_option))
            setting_num_Node.contents.release(setting_num_Node)
            return -1
        else:
            print("set {} to {} success.".format(setting, int_option))
        setting_num_Node.contents.release(setting_num_Node)
        return 0
    
    def settings_bool(self, setting, bool_option):
        setting_bool_Node = pointer(GENICAM_BoolNode())
        setting_bool_NodeInfo = GENICAM_BoolNodeInfo()
        setting_bool_NodeInfo.pCamera = pointer(self.cam)
        setting_bool_NodeInfo.attrName = setting
        nRet = GENICAM_createBoolNode(byref(setting_bool_NodeInfo), byref(setting_bool_Node))
        if nRet != 0:
            print("create {} Node fail!".format(setting))
            return -1
        nRet = setting_bool_Node.contents.setValue(setting_bool_Node, bool(bool_option))
        if nRet != 0:
            print("set {} to {} failed!".format(setting, bool_option))
            setting_bool_Node.contents.release(setting_bool_Node)
            return -1
        else:
            print("set {} to {} success.".format(setting, bool_option))
        setting_bool_Node.contents.release(setting_bool_Node)
        return 0

# TODO get some settings from the camera - i.e. sensor width and height for correctly setting w / h and offset

    @staticmethod
    def set_roi(camera, OffsetX, OffsetY, nWidth, nHeight):  # another example from the Contrastech Demo
        # 获取原始的宽度
        widthMaxNode = pointer(GENICAM_IntNode())
        widthMaxNodeInfo = GENICAM_IntNodeInfo()
        widthMaxNodeInfo.pCamera = pointer(camera)
        widthMaxNodeInfo.attrName = b"WidthMax"
        nRet = GENICAM_createIntNode(byref(widthMaxNodeInfo), byref(widthMaxNode))
        if (nRet != 0):
            print("create WidthMax Node fail!")
            return -1

        oriWidth = c_longlong()
        nRet = widthMaxNode.contents.getValue(widthMaxNode, byref(oriWidth))
        if (nRet != 0):
            print("widthMaxNode getValue fail!")
            # 释放相关资源 - Release related resources
            widthMaxNode.contents.release(widthMaxNode)
            return -1

            # 释放相关资源 - Release related resources
        widthMaxNode.contents.release(widthMaxNode)

        # 获取原始的高度
        heightMaxNode = pointer(GENICAM_IntNode())
        heightMaxNodeInfo = GENICAM_IntNodeInfo()
        heightMaxNodeInfo.pCamera = pointer(camera)
        heightMaxNodeInfo.attrName = b"HeightMax"
        nRet = GENICAM_createIntNode(byref(heightMaxNodeInfo), byref(heightMaxNode))
        if (nRet != 0):
            print("create HeightMax Node fail!")
            return -1

        oriHeight = c_longlong()
        nRet = heightMaxNode.contents.getValue(heightMaxNode, byref(oriHeight))
        if (nRet != 0):
            print("heightMaxNode getValue fail!")
            # 释放相关资源 - Release related resources
            heightMaxNode.contents.release(heightMaxNode)
            return -1

        # 释放相关资源 - Release related resources
        heightMaxNode.contents.release(heightMaxNode)

        # 检验参数
        if (oriWidth.value < (OffsetX + nWidth)) or (oriHeight.value < (OffsetY + nHeight)):
            print("please check input param!")
            return -1

        # 设置宽度
        widthNode = pointer(GENICAM_IntNode())
        widthNodeInfo = GENICAM_IntNodeInfo()
        widthNodeInfo.pCamera = pointer(camera)
        widthNodeInfo.attrName = b"Width"
        nRet = GENICAM_createIntNode(byref(widthNodeInfo), byref(widthNode))
        if (nRet != 0):
            print("create Width Node fail!")
            return -1

        nRet = widthNode.contents.setValue(widthNode, c_longlong(nWidth))
        if (nRet != 0):
            print("widthNode setValue [%d] fail!" % (nWidth))
            # 释放相关资源 - Release related resources
            widthNode.contents.release(widthNode)
            return -1

            # 释放相关资源 - Release related resources
        widthNode.contents.release(widthNode)

        # 设置高度
        heightNode = pointer(GENICAM_IntNode())
        heightNodeInfo = GENICAM_IntNodeInfo()
        heightNodeInfo.pCamera = pointer(camera)
        heightNodeInfo.attrName = b"Height"
        nRet = GENICAM_createIntNode(byref(heightNodeInfo), byref(heightNode))
        if (nRet != 0):
            print("create Height Node fail!")
            return -1

        nRet = heightNode.contents.setValue(heightNode, c_longlong(nHeight))
        if (nRet != 0):
            print("heightNode setValue [%d] fail!" % (nHeight))
            # 释放相关资源 - Release related resources
            heightNode.contents.release(heightNode)
            return -1

            # 释放相关资源 - Release related resources
        heightNode.contents.release(heightNode)

        # 设置OffsetX
        OffsetXNode = pointer(GENICAM_IntNode())
        OffsetXNodeInfo = GENICAM_IntNodeInfo()
        OffsetXNodeInfo.pCamera = pointer(camera)
        OffsetXNodeInfo.attrName = b"OffsetX"
        nRet = GENICAM_createIntNode(byref(OffsetXNodeInfo), byref(OffsetXNode))
        if (nRet != 0):
            print("create OffsetX Node fail!")
            return -1

        nRet = OffsetXNode.contents.setValue(OffsetXNode, c_longlong(OffsetX))
        if (nRet != 0):
            print("OffsetX setValue [%d] fail!" % (OffsetX))
            # 释放相关资源 - Release related resources
            OffsetXNode.contents.release(OffsetXNode)
            return -1

            # 释放相关资源 - Release related resources
        OffsetXNode.contents.release(OffsetXNode)

        # 设置OffsetY
        OffsetYNode = pointer(GENICAM_IntNode())
        OffsetYNodeInfo = GENICAM_IntNodeInfo()
        OffsetYNodeInfo.pCamera = pointer(camera)
        OffsetYNodeInfo.attrName = b"OffsetY"
        nRet = GENICAM_createIntNode(byref(OffsetYNodeInfo), byref(OffsetYNode))
        if (nRet != 0):
            print("create OffsetY Node fail!")
            return -1

        nRet = OffsetYNode.contents.setValue(OffsetYNode, c_longlong(OffsetY))
        if (nRet != 0):
            print("OffsetY setValue [%d] fail!" % (OffsetY))
            # 释放相关资源 - Release related resources
            OffsetYNode.contents.release(OffsetYNode)
            return -1

            # 释放相关资源 - Release related resources
        OffsetYNode.contents.release(OffsetYNode)
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
            offsetY = adjusted_offset_height / 2
        else:
            offsetY = 0
        if not img_width == sensor_width:
            adjusted_offset_width = sensor_width - img_width
            div_check_x = adjusted_offset_width / 16  # we are checking that the offset is divisible by 16
            while not div_check_x.is_integer():
                print('centering width offset')
                adjusted_offset_width -= 1
                div_check_x = adjusted_offset_width / 16
            offsetX = adjusted_offset_width / 2
        else:
            offsetX = 0
        print('final X offset is {}'.format(int(offsetX)))
        print('final Y offset is {}'.format(int(offsetY)))
        return int(offsetY), int(offsetX)
