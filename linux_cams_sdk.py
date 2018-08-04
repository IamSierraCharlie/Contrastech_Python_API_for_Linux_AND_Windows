from ImageConvert import *
from MVSDK import *  # only for the contrastech camera
import numpy as np
g_cameraStatusUserInfo = b"statusInfo"

class Camera(object):
    def __init__(self, img_width, img_height, img_channels):
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
        self.connectCallBackFunc = connectCallBack(self.deviceLinkNotify)
        self.connectCallBackFuncEx = connectCallBackEx(self.deviceLinkNotify)
        self.frameCallbackFunc = callbackFunc(self.onGetFrame)

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
        # 连接相机
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
        ## FIND CAMERA
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
        self.cam = cameraList[0]  # this is tha actual camera
        # open the camera
        nRet = self.openCamera()  # opens the camera
        if nRet != 0:  # handles the camera open failure
            print("openCamera fail.")

        acqCtrlInfo = GENICAM_AcquisitionControlInfo()
        acqCtrlInfo.pCamera = pointer(self.cam)
        self.acqCtrl = pointer(GENICAM_AcquisitionControl())
        nRet = GENICAM_createAcquisitionControl(pointer(acqCtrlInfo), byref(self.acqCtrl))
        if nRet != 0:
            print("create AcquisitionControl fail!")
            return -1

        # Set trigger source to soft trigger
        trigSourceEnumNode = self.acqCtrl.contents.triggerSource(self.acqCtrl)
        nRet = trigSourceEnumNode.setValueBySymbol(byref(trigSourceEnumNode), b"Software")
        if nRet != 0:
            print("set TriggerSource value [Software] fail!")
            # Release related resources
            # Release related resources
            trigSourceEnumNode.release(byref(trigSourceEnumNode))
            self.acqCtrl.contents.release(self.acqCtrl)
            return -1

        # Need to release Node resources
        trigSourceEnumNode.release(byref(trigSourceEnumNode))

        # Set trigger mode
        trigSelectorEnumNode = self.acqCtrl.contents.triggerSelector(self.acqCtrl)
        nRet = trigSelectorEnumNode.setValueBySymbol(byref(trigSelectorEnumNode), b"FrameStart")
        if nRet != 0:
            print("set TriggerSelector value [FrameStart] fail!")
            # Release related resources
            trigSelectorEnumNode.release(byref(trigSelectorEnumNode))
            self.acqCtrl.contents.release(self.acqCtrl)
            return -1

        # Node
        # Need to release Node resources
        trigSelectorEnumNode.release(byref(trigSelectorEnumNode))

        # Turn on trigger mode
        trigModeEnumNode = self.acqCtrl.contents.triggerMode(self.acqCtrl)
        nRet = trigModeEnumNode.setValueBySymbol(byref(trigModeEnumNode), b"On")
        if nRet != 0:
            print("set TriggerMode value [On] fail!")
            # 释放相关资源 - Release related resources
            # Release related resources
            trigModeEnumNode.release(byref(trigModeEnumNode))
            self.acqCtrl.contents.release(self.acqCtrl)
            return -1

        # Need to release related resources
        trigModeEnumNode.release(byref(trigModeEnumNode))
        self.acqCtrl.contents.release(self.acqCtrl)

        print('creating a stream source')
        streamSourceInfo = GENICAM_StreamSourceInfo()
        streamSourceInfo.channelId = 0
        streamSourceInfo.pCamera = pointer(self.cam)
        self.image_source = pointer(GENICAM_StreamSource())
        nRet = GENICAM_createStreamSource(pointer(streamSourceInfo), byref(self.image_source))
        if nRet != 0:
            print("create image_source fail!")
            return -1

        acquisitionEnumMode = pointer(GENICAM_EnumNode())
        acquisitionEnumModeInfo = GENICAM_EnumNodeInfo()
        acquisitionEnumModeInfo.pCamera = pointer(self.cam)
        acquisitionEnumModeInfo.attrName = b"AcquisitionMode"
        nRet = GENICAM_createEnumNode(byref(acquisitionEnumModeInfo), byref(acquisitionEnumMode))
        if nRet != 0:
            print("Setting acquisition mode failed!")
            # Release related resources
            self.image_source.contents.release(self.image_source)
            return -1
        # change acquisition mode to continuous
        print('change acquisition mode to continuous')
        nRet = acquisitionEnumMode.contents.setValueBySymbol(acquisitionEnumMode, b"Continuous")
        if nRet != 0:
            print("FAILED - change acquisition mode to continuous")
            # Release related resources
            acquisitionEnumMode.contents.release(acquisitionEnumMode)
            self.image_source.contents.release(self.image_source)  # this line dumps everything
            return -1
        acquisitionEnumMode.contents.release(acquisitionEnumMode)


        nRet = self.image_source.contents.attachGrabbing(self.image_source, self.frameCallbackFunc)
        if nRet != 0:
            print("attachGrabbing fail!")
            self.image_source.contents.release(self.image_source)
            return -1

        # Start the camera grabbing images
        nRet = self.image_source.contents.startGrabbing(self.image_source, c_ulonglong(0),
                                                        c_int(GENICAM_EGrabStrategy.grabStrategySequential))
        if nRet != 0:
            print("startGrabbing fail!")
            #Release related resources
            self.image_source.contents.release(self.image_source)
            return -1

        # this should create the necessary control to do the grabbing with "software"
        #acqCtrlInfo = GENICAM_AcquisitionControlInfo()
        #acqCtrlInfo.pCamera = pointer(self.cam)
        #self.acqCtrl = pointer(GENICAM_AcquisitionControl())
        nRet = GENICAM_createAcquisitionControl(pointer(acqCtrlInfo), byref(self.acqCtrl))
        if nRet != 0:
            print("create AcquisitionControl fail!")
            # 释放相关资源 - Release related resources
            self.image_source.contents.release(self.image_source)
            return -1
        nRet = self.image_source.contents.detachGrabbing(self.image_source, self.frameCallbackFunc)
        if nRet != 0:
            print("detachGrabbing fail!")
            self.image_source.contents.release(self.image_source)
            return -1


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

        #print(current - self.t)
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
        # self.acqCtrl.contents.release(self.acqCtrl)

        # current = time.perf_counter()

        # Assigning parameters for transcoding
        convertParams = IMGCNV_SOpenParam()
        convertParams.dataSize = imageSize
        convertParams.height = frame.contents.getImageHeight(frame)
        convertParams.width = frame.contents.getImageWidth(frame)
        convertParams.paddingX = frame.contents.getImagePaddingX(frame)
        convertParams.paddingY = frame.contents.getImagePaddingY(frame)
        convertParams.pixelForamt = frame.contents.getImagePixelFormat(frame)

        #print('dataSize', imageSize)
        #print('height', frame.contents.getImageHeight(frame))
        #print('width', frame.contents.getImageWidth(frame))
        #print('paddingX', frame.contents.getImagePaddingX(frame))
        #print('paddingY', frame.contents.getImagePaddingY(frame))
        #print('pixelFormat', frame.contents.getImagePixelFormat(frame))

        # Release driver image cache
        frame.contents.release(frame)

        # Save bmp pictures
        #bmpInfoHeader = contras.BITMAPINFOHEADER()
        #bmpFileHeader = contras.BITMAPFILEHEADER()

        #uRgbQuadLen = 0
        #rgbQuad = (contras.RGBQUAD * 256)()  # Palette information
        rgbBuff = c_buffer(b'\0', convertParams.height * convertParams.width * 3)

        # If the image format is Mono8 no transcoding is required
        #if convertParams.pixelForamt == EPixelType.gvspPixelMono8:
        #	# Initialization palette rgbQuad in real applications rgbQuad only need to initialize once
        #	for i in range(0, 256):
        #		rgbQuad[i].rgbBlue = rgbQuad[i].rgbGreen = rgbQuad[i].rgbRed = i
        #
        #	uRgbQuadLen = sizeof(contras.RGBQUAD) * 256
        #	bmpFileHeader.bfSize = sizeof(bmpFileHeader) + sizeof(bmpInfoHeader) + uRgbQuadLen + convertParams.dataSize
        #	bmpInfoHeader.biBitCount = 8
        #else:
            # Transcoding => BGR24
        rgbSize = c_int()
        nRet = IMGCNV_ConvertToRGB24(cast(frameBuff, c_void_p), byref(convertParams), cast(rgbBuff, c_void_p), byref(rgbSize))

        if nRet != 0:
            print("image convert fail! errorCode = " + str(nRet))
            # 释放相关资源 - Release related resources
            self.image_source.contents.release(self.image_source)
            return -1

        #bmpFileHeader.bfSize = sizeof(bmpFileHeader) + sizeof(bmpInfoHeader) + rgbSize.value
        #bmpInfoHeader.biBitCount = 24

        #print('rgbBuff', rgbBuff)  # rgbBuff <ctypes.c_char_Array_1108992 object at 0x7f95b888d2f0>
        # image_data = bytearray(string_at(rgbBuff, 3 * 608 * 608))
        #print('type', type(image_data))

        final = np.reshape(np.frombuffer(bytearray(string_at(rgbBuff,
                                                             self.img_channels * self.img_height * self.img_width)),
                                         dtype=np.uint8), (self.img_height, self.img_width,  self.img_channels))
        return final


    # the plan here is to create a single function that allows control over many aspects of the camera
    # caveats - unable to set numbers - only settings
    def change_setting(self, setting, option):
        print('\n\n\nInstance is: {}'.format(type(option)))
        if isinstance(option, int) and not isinstance(option, bool):
            print('changing with settings num')
            self.settings_num(setting, int_option=option)
        elif isinstance(option, bytes):
            print('changing with settings')
            self.settings(setting, option)
        elif isinstance(option, bool):
            print('changing with settings_bool')
            self.settings_bool(setting, option)

        else:
            print('unknown var {} from setting {} - unable to handle this'.format(option, setting))
            exit()

    def settings(self, setting, option):
        #######################################################
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
        #######################################################

    # TODO turn this into a function that servers all settings where numbers need to be changed
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
            print("set {} [{}]us fail!".format(setting, int_option))
            setting_num_Node.contents.release(setting_num_Node)
            return -1
        else:
            print("set {} value [{}]us success.".format(setting, int_option))
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
            print("set {} [{}]us fail!".format(setting, bool_option))
            setting_bool_Node.contents.release(setting_bool_Node)
            return -1
        else:
            print("set {} value [{}]us success.".format(setting, bool_option))
        setting_bool_Node.contents.release(setting_bool_Node)
        return 0

