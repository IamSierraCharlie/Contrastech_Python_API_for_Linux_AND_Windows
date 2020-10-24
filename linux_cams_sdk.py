from ImageConvert import *
from MVSDK import *  # only for the contrastech camera
import numpy as np
import time

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

	@staticmethod  # this function reports the camera status.  It will output issues to the cmd prompt
	def deviceLinkNotify(connectArg, linkInfo):
		if EVType.offLine == connectArg.contents.m_event:
			print("camera is off line, userInfo [%s]" % c_char_p(linkInfo).value)
		elif EVType.onLine == connectArg.contents.m_event:
			print("camera is on line, userInfo [%s]" % c_char_p(linkInfo).value)

	@staticmethod
	def enumCameras():
		system = pointer(GENICAM_System())
		n_ret = GENICAM_getSystemInstance(byref(system))
		if n_ret != 0:
			print("getSystemInstance fail!")
			return None, None

		cameraList = pointer(GenicamCamera())
		cameraCnt = c_uint()
		n_ret = system.contents.discovery(system, byref(cameraList), byref(cameraCnt), c_int(GENICAM_EProtocolType.typeAll))
		if n_ret != 0:
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
		n_ret = frame.contents.valid(frame)
		if n_ret != 0:
			print("frame is invalid!")
			# Release driver image cache resources
			frame.contents.release(frame)
			return

		# print("BlockId = %d" % (frame.contents.getBlockId(frame)))
		frame.contents.release(frame)

	# Unregister camera connection status callback
	def unsubscribeCameraStatus(self):
		# Anti-registration notification
		eventSubscribe = pointer(GenicamEventSubscribe())
		eventSubscribeInfo = GenicamEventSubscribeInfo()
		eventSubscribeInfo.pCamera = pointer(self.cam)
		n_ret = GENICAM_createEventSubscribe(byref(eventSubscribeInfo), byref(eventSubscribe))
		if n_ret != 0:
			print("create eventSubscribe fail!")
			return -1

		n_ret = eventSubscribe.contents.unsubscribeConnectArgs(eventSubscribe, self.connectCallBackFunc,
		                                                      g_cameraStatusUserInfo)
		if n_ret != 0:
			print("unsubscribeConnectArgs fail!")
			# Release related resources
			eventSubscribe.contents.release(eventSubscribe)
			return -1
		# Relevant resources need to be released when they are no longer used
		eventSubscribe.contents.release(eventSubscribe)
		return 0

	def subscribeCameraStatus(self):
		# Registration notification
		eventSubscribe = pointer(GenicamEventSubscribe())
		eventSubscribeInfo = GenicamEventSubscribeInfo()
		eventSubscribeInfo.pCamera = pointer(self.cam)
		n_ret = GENICAM_createEventSubscribe(byref(eventSubscribeInfo), byref(eventSubscribe))
		if n_ret != 0:
			print("create eventSubscribe fail!")
			return -1

		n_ret = eventSubscribe.contents.subscribeConnectArgs(eventSubscribe, self.connectCallBackFunc,
		                                                    g_cameraStatusUserInfo)
		if n_ret != 0:
			print("subscribeConnectArgsEx fail!")
			# Release related resources
			eventSubscribe.contents.release(eventSubscribe)
			return -1

		# Relevant resources need to be released when they are no longer used
		eventSubscribe.contents.release(eventSubscribe)
		return 0

	def openCamera(self):
		n_ret = self.cam.connect(self.cam, c_int(GENICAM_ECameraAccessPermission.accessPermissionControl))
		if n_ret != 0:
			print("camera connect fail!")
			return -1
		else:
			print("camera connect success.")

		n_ret = self.subscribeCameraStatus()
		if n_ret != 0:
			print("subscribeCameraStatus fail!")
			return -1
		return 0

	def closeCamera(self):
		n_ret = self.unsubscribeCameraStatus()
		if n_ret != 0:
			print("unsubscribeCameraStatus fail!")
			return -1

		n_ret = self.cam.disConnect(byref(self.cam))
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

	def deactivate(self):
		print('should deactivate')
		n_ret = self.image_source.contents.stopGrabbing(self.image_source)
		if n_ret != 0:
			print("stopGrabbing fail!")
			# Release related resourcesrces
			self.image_source.contents.release(self.image_source)
			return -1
		# Turn off trigger mode - camera light should stop flashing
		trigModeEnumNode = self.acqCtrl.contents.triggerMode(self.acqCtrl)
		n_ret = trigModeEnumNode.setValueBySymbol(byref(trigModeEnumNode), b"Off")
		if n_ret != 0:
			print("set TriggerMode value [On] fail!")
			# Release related resources
			trigModeEnumNode.release(byref(trigModeEnumNode))
			self.acqCtrl.contents.release(self.acqCtrl)
			return -1

		n_ret = self.closeCamera()
		if n_ret != 0:
			print("closeCamera fail")
			self.image_source.contents.release(self.image_source)
			return -1
		self.image_source.contents.release(self.image_source)

	def activate(self):
		# connect to the camera
		acqCtrlInfo = GenicamAcquisitionControlInfo()
		acqCtrlInfo.pCamera = pointer(self.cam)
		self.acqCtrl = pointer(GenicamAcquisitionControl())
		n_ret = GENICAM_createAcquisitionControl(pointer(acqCtrlInfo), byref(self.acqCtrl))
		if n_ret != 0:
			print("create AcquisitionControl fail!")
			return -1

		# create the streaming source
		print('creating a stream source')
		streamSourceInfo = GenicamStreamSourceInfo()
		streamSourceInfo.channelId = 0
		streamSourceInfo.pCamera = pointer(self.cam)
		self.image_source = pointer(GenicamStreamSource())
		n_ret = GENICAM_createStreamSource(pointer(streamSourceInfo), byref(self.image_source))
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
		n_ret = GENICAM_createAcquisitionControl(pointer(acqCtrlInfo), byref(self.acqCtrl))
		if n_ret != 0:
			print("create AcquisitionControl fail!")
			self.image_source.contents.release(self.image_source)
			return -1
		n_ret = self.image_source.contents.detachGrabbing(self.image_source, self.frameCallbackFunc)
		if n_ret != 0:
			print("detachGrabbing fail!")
			self.image_source.contents.release(self.image_source)
			return -1

	def create_camera_instance(self):
		camera_count, camera_list = self.enumCameras()
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
		time.sleep(3)
		self.cam = camera_list[0]  # this is the actual camera
		# open the camera
		n_ret = self.openCamera()  # opens the camera
		if n_ret != 0:  # handles the camera open failure
			print("openCamera fail.")
		else:
			print("Camera Opened")
			# get some info about the camera
			system = pointer(GenicamCamera())
			n_ret = GENICAM_getSystemInstance(byref(system))

	def grab_image(self):
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
			self.deactivate()
			self.image_source.contents.release(self.image_source)
			return -1
		else:
			# print("SoftTrigger getFrame success BlockId = " + str(frame.contents.getBlockId(frame)))
			# print("get frame time: " + str(datetime.datetime.now()))
			trig_software_cmd_node.release(byref(trig_software_cmd_node))

			self.check_valid_frame(self.cam, frame, self.image_source)
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

		#print('dataSize', imageSize)
		#print('height', frame.contents.getImageHeight(frame))
		#print('width', frame.contents.getImageWidth(frame))
		#print('paddingX', frame.contents.getImagePaddingX(frame))
		#print('paddingY', frame.contents.getImagePaddingY(frame))
		#print('pixelFormat', frame.contents.getImagePixelFormat(frame))

		# Release driver image cache
		frame.contents.release(frame)
		rgbBuff = c_buffer(b'\0', convert_params.height * convert_params.width * 3)
		rgbSize = c_int()
		n_ret = IMGCNV_ConvertToRGB24(cast(frame_buff, c_void_p), byref(convert_params), cast(rgbBuff, c_void_p),
		                             byref(rgbSize))

		if n_ret != 0:
			print("image convert fail! errorCode = " + str(n_ret))
			# 释放相关资源 - Release related resources
			self.image_source.contents.release(self.image_source)
			return -1

		final = np.reshape(np.frombuffer(bytearray(string_at(rgbBuff,
		                                                     self.img_channels * self.img_height * self.img_width)),
		                                 dtype=np.uint8), (self.img_height, self.img_width, self.img_channels))
		return final

	def change_setting(self, setting, option):
		print('\n\n\nInstance is: {}'.format(type(option)))
		# option = option.encode()
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
		setting_char_EnumModeInfo = GenicamEnumNodeInfo()
		setting_char_EnumModeInfo.pCamera = pointer(self.cam)
		setting_char_EnumModeInfo.attrName = setting
		n_ret = GENICAM_createEnumNode(byref(setting_char_EnumModeInfo), byref(setting_char_EnumMode))
		if n_ret != 0:
			print("Unable to access {}".format(setting))
			# Release related resources
			self.image_source.contents.release(self.image_source)
			return -1
		# change setting_char_ mode to continuous
		print('Changing {} to {}'.format(setting, option))
		n_ret = setting_char_EnumMode.contents.setValueBySymbol(setting_char_EnumMode, option)
		if n_ret != 0:
			print('Failed!')
			# Release related resources
			setting_char_EnumMode.contents.release(setting_char_EnumMode)
			self.image_source.contents.release(self.image_source)  # this line dumps everything
			return -1
		else:
			print('Success!')
		setting_char_EnumMode.contents.release(setting_char_EnumMode)

	def settings_num(self, setting, int_option):  # almost straight from the contrastech demo
		setting_num_Node = pointer(GenicamDoubleNode())
		setting_num_NodeInfo = GenicamDoubleNodeInfo()
		setting_num_NodeInfo.pCamera = pointer(self.cam)
		setting_num_NodeInfo.attrName = setting
		n_ret = GENICAM_createDoubleNode(byref(setting_num_NodeInfo), byref(setting_num_Node))
		if n_ret != 0:
			print("create {} Node fail!".format(setting))
			return -1
		n_ret = setting_num_Node.contents.setValue(setting_num_Node, c_double(int_option))
		if n_ret != 0:
			print("set {} to {} fail!".format(setting, int_option))
			setting_num_Node.contents.release(setting_num_Node)
			return -1
		else:
			print("set {} to {} success.".format(setting, int_option))
		setting_num_Node.contents.release(setting_num_Node)
		return 0

	def settings_bool(self, setting, bool_option):
		setting_bool_Node = pointer(GenicamBoolNode())
		setting_bool_NodeInfo = GENICAM_BoolNodeInfo()
		setting_bool_NodeInfo.pCamera = pointer(self.cam)
		setting_bool_NodeInfo.attrName = setting
		n_ret = GENICAM_createBoolNode(byref(setting_bool_NodeInfo), byref(setting_bool_Node))
		if n_ret != 0:
			print("create {} Node fail!".format(setting))
			return -1
		n_ret = setting_bool_Node.contents.setValue(setting_bool_Node, bool(bool_option))
		if n_ret != 0:
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
		widthMaxNode = pointer(GenicamIntNode())
		widthMaxNodeInfo = GenicamIntNodeInfo()
		widthMaxNodeInfo.pCamera = pointer(camera)
		widthMaxNodeInfo.attrName = b"WidthMax"
		n_ret = GENICAM_createIntNode(byref(widthMaxNodeInfo), byref(widthMaxNode))
		if (n_ret != 0):
			print("create WidthMax Node fail!")
			return -1

		oriWidth = c_longlong()
		n_ret = widthMaxNode.contents.getValue(widthMaxNode, byref(oriWidth))
		if (n_ret != 0):
			print("widthMaxNode getValue fail!")
			# 释放相关资源 - Release related resources
			widthMaxNode.contents.release(widthMaxNode)
			return -1

		# 释放相关资源 - Release related resources
		widthMaxNode.contents.release(widthMaxNode)

		# 获取原始的高度
		heightMaxNode = pointer(GenicamIntNode())
		heightMaxNodeInfo = GenicamIntNodeInfo()
		heightMaxNodeInfo.pCamera = pointer(camera)
		heightMaxNodeInfo.attrName = b"HeightMax"
		n_ret = GENICAM_createIntNode(byref(heightMaxNodeInfo), byref(heightMaxNode))
		if (n_ret != 0):
			print("create HeightMax Node fail!")
			return -1

		oriHeight = c_longlong()
		n_ret = heightMaxNode.contents.getValue(heightMaxNode, byref(oriHeight))
		if (n_ret != 0):
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
		widthNode = pointer(GenicamIntNode())
		widthNodeInfo = GenicamIntNodeInfo()
		widthNodeInfo.pCamera = pointer(camera)
		widthNodeInfo.attrName = b"Width"
		n_ret = GENICAM_createIntNode(byref(widthNodeInfo), byref(widthNode))
		if (n_ret != 0):
			print("create Width Node fail!")
			return -1

		n_ret = widthNode.contents.setValue(widthNode, c_longlong(nWidth))
		if (n_ret != 0):
			print("widthNode setValue [%d] fail!" % (nWidth))
			# 释放相关资源 - Release related resources
			widthNode.contents.release(widthNode)
			return -1

		# 释放相关资源 - Release related resources
		widthNode.contents.release(widthNode)

		# 设置高度
		heightNode = pointer(GenicamIntNode())
		heightNodeInfo = GenicamIntNodeInfo()
		heightNodeInfo.pCamera = pointer(camera)
		heightNodeInfo.attrName = b"Height"
		n_ret = GENICAM_createIntNode(byref(heightNodeInfo), byref(heightNode))
		if (n_ret != 0):
			print("create Height Node fail!")
			return -1

		n_ret = heightNode.contents.setValue(heightNode, c_longlong(nHeight))
		if (n_ret != 0):
			print("heightNode setValue [%d] fail!" % (nHeight))
			# 释放相关资源 - Release related resources
			heightNode.contents.release(heightNode)
			return -1

		# 释放相关资源 - Release related resources
		heightNode.contents.release(heightNode)

		# 设置OffsetX
		OffsetXNode = pointer(GenicamIntNode())
		OffsetXNodeInfo = GenicamIntNodeInfo()
		OffsetXNodeInfo.pCamera = pointer(camera)
		OffsetXNodeInfo.attrName = b"OffsetX"
		n_ret = GENICAM_createIntNode(byref(OffsetXNodeInfo), byref(OffsetXNode))
		if (n_ret != 0):
			print("create OffsetX Node fail!")
			return -1

		n_ret = OffsetXNode.contents.setValue(OffsetXNode, c_longlong(OffsetX))
		if (n_ret != 0):
			print("OffsetX setValue [%d] fail!" % (OffsetX))
			# 释放相关资源 - Release related resources
			OffsetXNode.contents.release(OffsetXNode)
			return -1

		# 释放相关资源 - Release related resources
		OffsetXNode.contents.release(OffsetXNode)

		# 设置OffsetY
		OffsetYNode = pointer(GenicamIntNode())
		OffsetYNodeInfo = GenicamIntNodeInfo()
		OffsetYNodeInfo.pCamera = pointer(camera)
		OffsetYNodeInfo.attrName = b"OffsetY"
		n_ret = GENICAM_createIntNode(byref(OffsetYNodeInfo), byref(OffsetYNode))
		if (n_ret != 0):
			print("create OffsetY Node fail!")
			return -1

		n_ret = OffsetYNode.contents.setValue(OffsetYNode, c_longlong(OffsetY))
		if (n_ret != 0):
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
