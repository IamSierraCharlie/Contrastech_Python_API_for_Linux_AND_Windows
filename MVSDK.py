#!/usr/bin/env python
# coding: utf-8
'''
Created on 2017-10-18

@author: 
'''
from ctypes import *

#定义枚举类型
def enum(**enums):
    return type('Enum', (), enums)

#加载SDK动态库
# 32bit
#MVSDKdll = cdll.LoadLibrary("./dll/x86/libMVSDK.so")
# 64bit
MVSDKdll = cdll.LoadLibrary("./dll/x64/libMVSDK.so")

#SDK.h => define 宏定义
MAX_PARAM_CNT        = 1000
MAX_STRING_LENTH     = 256
MAX_PAYLOAD_TYPE_CNT = 20 

GVSP_PIX_MONO                          = 0x01000000
GVSP_PIX_RGB                           = 0x02000000
GVSP_PIX_COLOR                         = 0x02000000
GVSP_PIX_CUSTOM                        = 0x80000000
GVSP_PIX_COLOR_MASK                    = 0xFF000000

GVSP_PIX_OCCUPY1BIT                    = 0x00010000
GVSP_PIX_OCCUPY2BIT                    = 0x00020000
GVSP_PIX_OCCUPY4BIT                    = 0x00040000
GVSP_PIX_OCCUPY8BIT                    = 0x00080000
GVSP_PIX_OCCUPY12BIT                   = 0x000C0000
GVSP_PIX_OCCUPY16BIT                   = 0x00100000
GVSP_PIX_OCCUPY24BIT                   = 0x00180000
GVSP_PIX_OCCUPY32BIT                   = 0x00200000
GVSP_PIX_OCCUPY36BIT                   = 0x00240000
GVSP_PIX_OCCUPY48BIT                   = 0x00300000
GVSP_PIX_EFFECTIVE_PIXEL_SIZE_MASK     = 0x00FF0000
GVSP_PIX_EFFECTIVE_PIXEL_SIZE_SHIFT    = 16

GVSP_PIX_ID_MASK                       = 0x0000FFFF
GVSP_PIX_COUNT                         = 0x46

MAX_ATTR_NAME_LEN = 1024


#SDK.h => enum EPixelType
EPixelType = enum(
                pixelTypeUndefined = -1,
                gvspPixelMono1p = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY1BIT | 0x0037),
                gvspPixelMono2p = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY2BIT | 0x0038),
                gvspPixelMono4p = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY4BIT | 0x0039),
                gvspPixelMono8 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY8BIT | 0x0001),
                gvspPixelMono8S = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY8BIT | 0x0002),
                gvspPixelMono10 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY16BIT | 0x0003),
                gvspPixelMono10Packed = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY12BIT | 0x0004),
                gvspPixelMono12 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY16BIT | 0x0005),
                gvspPixelMono12Packed = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY12BIT | 0x0006),
                gvspPixelMono14 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY16BIT | 0x0025),
                gvspPixelMono16 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY16BIT | 0x0007),
            
                # Bayer Format
                gvspPixelBayGR8 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY8BIT | 0x0008),
                gvspPixelBayRG8 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY8BIT | 0x0009),
                gvspPixelBayGB8 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY8BIT | 0x000A),
                gvspPixelBayBG8 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY8BIT | 0x000B),
                gvspPixelBayGR10 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY16BIT | 0x000C),
                gvspPixelBayRG10 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY16BIT | 0x000D),
                gvspPixelBayGB10 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY16BIT | 0x000E),
                gvspPixelBayBG10 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY16BIT | 0x000F),
                gvspPixelBayGR12 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY16BIT | 0x0010),
                gvspPixelBayRG12 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY16BIT | 0x0011),
                gvspPixelBayGB12 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY16BIT | 0x0012),
                gvspPixelBayBG12 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY16BIT | 0x0013),
                gvspPixelBayGR10Packed = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY12BIT | 0x0026),
                gvspPixelBayRG10Packed = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY12BIT | 0x0027),
                gvspPixelBayGB10Packed = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY12BIT | 0x0028),
                gvspPixelBayBG10Packed = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY12BIT | 0x0029),
                gvspPixelBayGR12Packed = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY12BIT | 0x002A),
                gvspPixelBayRG12Packed = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY12BIT | 0x002B),
                gvspPixelBayGB12Packed = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY12BIT | 0x002C),
                gvspPixelBayBG12Packed = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY12BIT | 0x002D),
                gvspPixelBayGR16 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY16BIT | 0x002E),
                gvspPixelBayRG16 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY16BIT | 0x002F),
                gvspPixelBayGB16 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY16BIT | 0x0030),
                gvspPixelBayBG16 = (GVSP_PIX_MONO | GVSP_PIX_OCCUPY16BIT | 0x0031),
            
                # RGB Format
                gvspPixelRGB8 = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY24BIT | 0x0014),
                gvspPixelBGR8 = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY24BIT | 0x0015),
                gvspPixelRGBA8 = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY32BIT | 0x0016),
                gvspPixelBGRA8 = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY32BIT | 0x0017),
                gvspPixelRGB10 = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY48BIT | 0x0018),
                gvspPixelBGR10 = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY48BIT | 0x0019),
                gvspPixelRGB12 = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY48BIT | 0x001A),
                gvspPixelBGR12 = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY48BIT | 0x001B),
                gvspPixelRGB16 = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY48BIT | 0x0033),
                gvspPixelRGB10V1Packed = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY32BIT | 0x001C),
                gvspPixelRGB10P32 = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY32BIT | 0x001D),
                gvspPixelRGB12V1Packed = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY36BIT | 0X0034),
                gvspPixelRGB565P = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY16BIT | 0x0035),
                gvspPixelBGR565P = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY16BIT | 0X0036),
            
                # YVR Format
                gvspPixelYUV411_8_UYYVYY = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY12BIT | 0x001E),
                gvspPixelYUV422_8_UYVY = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY16BIT | 0x001F),
                gvspPixelYUV422_8 = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY16BIT | 0x0032),
                gvspPixelYUV8_UYV = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY24BIT | 0x0020),
                gvspPixelYCbCr8CbYCr = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY24BIT | 0x003A),
                gvspPixelYCbCr422_8 = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY16BIT | 0x003B),
                gvspPixelYCbCr422_8_CbYCrY = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY16BIT | 0x0043),
                gvspPixelYCbCr411_8_CbYYCrYY = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY12BIT | 0x003C),
                gvspPixelYCbCr601_8_CbYCr = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY24BIT | 0x003D),
                gvspPixelYCbCr601_422_8 = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY16BIT | 0x003E),
                gvspPixelYCbCr601_422_8_CbYCrY = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY16BIT | 0x0044),
                gvspPixelYCbCr601_411_8_CbYYCrYY = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY12BIT | 0x003F),
                gvspPixelYCbCr709_8_CbYCr = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY24BIT | 0x0040),
                gvspPixelYCbCr709_422_8 = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY16BIT | 0x0041),
                gvspPixelYCbCr709_422_8_CbYCrY = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY16BIT | 0x0045),
                gvspPixelYCbCr709_411_8_CbYYCrYY = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY12BIT | 0x0042),
            
                # RGB Planar
                gvspPixelRGB8Planar = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY24BIT | 0x0021),
                gvspPixelRGB10Planar = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY48BIT | 0x0022),
                gvspPixelRGB12Planar = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY48BIT | 0x0023),
                gvspPixelRGB16Planar = (GVSP_PIX_COLOR | GVSP_PIX_OCCUPY48BIT | 0x0024),
                
                # BayerRG10p和BayerRG12p格式，针对特定项目临时添加,请不要使用
                gvspPixelBayRG10p = 0x010A0058,
                gvspPixelBayRG12p = 0x010c0059,

                # mono1c格式，自定义格式
                gvspPixelMono1c = 0x012000FF,

                # mono1e格式，自定义格式，用来显示连通域
                gvspPixelMono1e = 0x01080FFF
                )

#SDK.h => enum GENICAM_ECameraAccessPermission
GENICAM_ECameraAccessPermission = enum(
                                        accessPermissionOpen                  = 0,        
                                        accessPermissionExclusive             = 1,   
                                        accessPermissionControl               = 2,  
                                        accessPermissionControlWithSwitchover = 3,    
                                        accessPermissionUnknown               = 254,       
                                        accessPermissionUndefined             = 255,
                                        )

#SDK.h => enum GENICAM_EProtocolType
GENICAM_EProtocolType = enum(
                             typeGigE = 0,
                             typeUsb3 = 1,
                             typeCL   = 2,
                             typePCIe = 3,
                             typeAll  = 255
                             )

#SDK.h => struct GENICAM_Camera 
class GENICAM_Camera(Structure):
    pass

GENICAM_Camera_addRef  = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_Camera)) #返回值 参数1 参数2 参数3 ......
GENICAM_Camera_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_Camera))
GENICAM_Camera_getType = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_Camera))
GENICAM_Camera_getName = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_Camera))
GENICAM_Camera_getKey  = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_Camera))
GENICAM_Camera_connect = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_Camera), c_int)
GENICAM_Camera_disConnect = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_Camera))
GENICAM_Camera_isConnect = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_Camera))
GENICAM_Camera_getInterfaceName = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_Camera))
GENICAM_Camera_getInterfaceType = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_Camera))
GENICAM_Camera_downLoadGenICamXML = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_Camera), c_char_p)
GENICAM_Camera_getVendorName = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_Camera))
GENICAM_Camera_getModelName = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_Camera))
GENICAM_Camera_getSerialNumber = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_Camera))
GENICAM_Camera_getDeviceVersion = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_Camera))
GENICAM_Camera_getManufactureInfo = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_Camera))

GENICAM_Camera._fields_ = [
                ('priv', c_void_p),
                ('addRef', GENICAM_Camera_addRef),
                ('release', GENICAM_Camera_release),
                ('getType', GENICAM_Camera_getType),
                ('getName', GENICAM_Camera_getName),
                ('getKey', GENICAM_Camera_getKey),
                ('connect', GENICAM_Camera_connect),
                ('disConnect', GENICAM_Camera_disConnect),
                ('isConnect', GENICAM_Camera_isConnect),
                ('getInterfaceName', GENICAM_Camera_getInterfaceName,),
                ('getInterfaceType', GENICAM_Camera_getInterfaceType),
                ('downLoadGenICamXML', GENICAM_Camera_downLoadGenICamXML),
                ('getVendorName', GENICAM_Camera_getVendorName),
                ('getModelName', GENICAM_Camera_getModelName),
                ('getSerialNumber', GENICAM_Camera_getSerialNumber),
                ('getDeviceVersion', GENICAM_Camera_getDeviceVersion),
                ('getManufactureInfo', GENICAM_Camera_getManufactureInfo),
                ('reserved', c_uint * 15),
                ]

#SDK.h => struct GENICAM_System 
class GENICAM_System(Structure):
    pass

GENICAM_System_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_System)) 
GENICAM_System_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_System))
GENICAM_System_discovery = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_System), POINTER(POINTER(GENICAM_Camera)), \
                                               POINTER(c_uint), c_int)
GENICAM_System_getCamera = eval('CFUNCTYPE')(POINTER(GENICAM_Camera), POINTER(GENICAM_System), c_char_p)
GENICAM_System_getVersion = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_System))

GENICAM_System._fields_ = [
                ('priv', c_void_p),
                ('addRef', GENICAM_System_addRef),
                ('release', GENICAM_System_release),
                ('discovery', GENICAM_System_discovery),
                ('getCamera', GENICAM_System_getCamera),
                ('getVersion', GENICAM_System_getVersion),
                ('reserved', c_uint * 26),
                ]

#SDK.h => GENICAM_getSystemInstance(GENICAM_System** ppSystem);
GENICAM_getSystemInstance = MVSDKdll.GENICAM_getSystemInstance

#SDK.h => enum GENICAM_EPayloadType
GENICAM_EPayloadType = enum(
                            payloadImage = 1,
                            payloadRawdata = 2,
                            payloadFile = 3,
                            payloadChunkData = 4,
                            payloadExtChunkData = 5,
                            payloadDevSpecBase = 0x8000,
                            payloadUndefined = 0x8001,
                           )

#SDK.h => struct GENICAM_Frame
class GENICAM_Frame(Structure):
    pass

GENICAM_Frame_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_Frame))
GENICAM_Frame_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_Frame))
GENICAM_Frame_clone = eval('CFUNCTYPE')(POINTER(GENICAM_Frame), POINTER(GENICAM_Frame))
GENICAM_Frame_reset = eval('CFUNCTYPE')(None, POINTER(GENICAM_Frame))
GENICAM_Frame_valid = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_Frame))
GENICAM_Frame_getImage = eval('CFUNCTYPE')(c_void_p, POINTER(GENICAM_Frame))
GENICAM_Frame_getFrameStatus = eval('CFUNCTYPE')(c_uint, POINTER(GENICAM_Frame))
GENICAM_Frame_getImageWidth = eval('CFUNCTYPE')(c_uint, POINTER(GENICAM_Frame))
GENICAM_Frame_getImageHeight = eval('CFUNCTYPE')(c_uint, POINTER(GENICAM_Frame))
GENICAM_Frame_getImageSize = eval('CFUNCTYPE')(c_uint, POINTER(GENICAM_Frame))
GENICAM_Frame_getImagePixelFormat = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_Frame))
GENICAM_Frame_getImageTimeStamp = eval('CFUNCTYPE')(c_ulonglong, POINTER(GENICAM_Frame))
GENICAM_Frame_getBlockId = eval('CFUNCTYPE')(c_ulonglong, POINTER(GENICAM_Frame))
GENICAM_Frame_getPayLoadTypes = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_Frame), c_int * MAX_PAYLOAD_TYPE_CNT, POINTER(c_uint))
GENICAM_Frame_getChunkCount = eval('CFUNCTYPE')(c_uint, POINTER(GENICAM_Frame))
GENICAM_Frame_getChunkDataByIndex = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_Frame), c_uint, POINTER(c_uint), \
                                                      c_char* MAX_STRING_LENTH * MAX_PARAM_CNT, POINTER(c_uint))
GENICAM_Frame_getImagePaddingX = eval('CFUNCTYPE')(c_uint, POINTER(GENICAM_Frame))
GENICAM_Frame_getImagePaddingY = eval('CFUNCTYPE')(c_uint, POINTER(GENICAM_Frame))

GENICAM_Frame._fields_ = [
                ('priv', c_void_p),
                ('addRef', GENICAM_Frame_addRef),
                ('release', GENICAM_Frame_release),
                ('clone', GENICAM_Frame_clone),
                ('reset', GENICAM_Frame_reset),
                ('valid', GENICAM_Frame_valid),
                ('getImage', GENICAM_Frame_getImage),
                ('getFrameStatus', GENICAM_Frame_getFrameStatus),
                ('getImageWidth', GENICAM_Frame_getImageWidth),
                ('getImageHeight', GENICAM_Frame_getImageHeight),
                ('getImageSize', GENICAM_Frame_getImageSize),
                ('getImagePixelFormat', GENICAM_Frame_getImagePixelFormat),
                ('getImageTimeStamp', GENICAM_Frame_getImageTimeStamp),
                ('getBlockId', GENICAM_Frame_getBlockId),
                ('getPayLoadTypes', GENICAM_Frame_getPayLoadTypes),
                ('getChunkCount', GENICAM_Frame_getChunkCount),
                ('getChunkDataByIndex', GENICAM_Frame_getChunkDataByIndex),
                ('getImagePaddingX', GENICAM_Frame_getImagePaddingX),
                ('getImagePaddingY', GENICAM_Frame_getImagePaddingY),
                ('reserved', c_uint * 13),
                ]


#SDK.h => enum  GENICAM_EGrabStrategy
GENICAM_EGrabStrategy = enum(
                             grabStrategySequential = 0,
                             grabStrategyLatestImage = 1,
                             grabStrategyUndefined = 2,
                             )

#SDK.h => void(*callbackFun)(GENICAM_Frame* pFrame) 回调函数原型
callbackFunc = eval('CFUNCTYPE')(None, POINTER(GENICAM_Frame))

#SDK.h => void(*callbackFunEx)(GENICAM_Frame* pFrame, void* pUser);
callbackFuncEx = eval('CFUNCTYPE')(None, POINTER(GENICAM_Frame), c_void_p)

#SDK.h => struct GENICAM_StreamSource
class GENICAM_StreamSource(Structure):
    pass

GENICAM_StreamSource_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StreamSource))
GENICAM_StreamSource_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StreamSource))
GENICAM_StreamSource_startGrabbing = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StreamSource), c_ulonglong, c_int)
GENICAM_StreamSource_stopGrabbing = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StreamSource))
GENICAM_StreamSource_isGrabbing = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StreamSource))
GENICAM_StreamSource_getFrame = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StreamSource), POINTER(POINTER(GENICAM_Frame)), c_uint)
GENICAM_StreamSource_attachGrabbing = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StreamSource), callbackFunc)
GENICAM_StreamSource_detachGrabbing = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StreamSource), callbackFunc)
GENICAM_StreamSource_setBufferCount = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StreamSource), c_uint)
GENICAM_StreamSource_attachGrabbingEx = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StreamSource), callbackFuncEx, c_void_p)
GENICAM_StreamSource_detachGrabbingEx = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StreamSource), callbackFuncEx, c_void_p)

GENICAM_StreamSource._fields_ = [
                                ('priv', c_void_p),
                                ('addRef', GENICAM_StreamSource_addRef),
                                ('release', GENICAM_StreamSource_release),
                                ('startGrabbing', GENICAM_StreamSource_startGrabbing),
                                ('stopGrabbing', GENICAM_StreamSource_stopGrabbing),
                                ('isGrabbing', GENICAM_StreamSource_isGrabbing),
                                ('getFrame', GENICAM_StreamSource_getFrame),
                                ('attachGrabbing', GENICAM_StreamSource_attachGrabbing),
                                ('detachGrabbing', GENICAM_StreamSource_detachGrabbing),
                                ('setBufferCount', GENICAM_StreamSource_setBufferCount),
                                ('attachGrabbingEx', GENICAM_StreamSource_attachGrabbingEx),
                                ('detachGrabbingEx', GENICAM_StreamSource_detachGrabbingEx),
                                ('reserved', c_uint)
                                ]

#SDK.h => struct GENICAM_StreamSourceInfo
class GENICAM_StreamSourceInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('channeId', c_uint),
                ('reserved', c_uint),
                ]

#SDK.h => GENICAM_createStreamSource(const GENICAM_StreamSourceInfo* pStreamSourceInfo, GENICAM_StreamSource** ppStreamSource);
GENICAM_createStreamSource = MVSDKdll.GENICAM_createStreamSource

#SDK.h => EVType
EVType = enum(
             offLine = 0,
             onLine = 1,
             )

#SDK.h => struct GENICAM_SConnectArg
class GENICAM_SConnectArg(Structure):
    _fields_ = [
                ('m_event', c_int),
                ('reserve', c_uint * 15),
                ]

#SDK.h => struct GENICAM_SParamUpdataArg
class GENICAM_SParamUpdataArg(Structure):
    _fields_ = [
                ('isPoll', c_int),
                ('reserve', c_uint * 10),
                ('paramNames', c_char * MAX_STRING_LENTH * MAX_PARAM_CNT),
                ('referenceParamCnt', c_uint),
                ]
    
#SDK.h => enum GENICAM_EEventStatus
GENICAM_EEventStatus = enum(
                            streamEventNormal = 1,
                            streamEventLostFrame = 2,
                            streamEventLostPacket = 3,
                            streamEventImageError = 4,
                            streamEventStreamChannelError = 5,
                            )

#SDK.h => struct GENICAM_SStreamArg
class GENICAM_SStreamArg(Structure):
    _fields_ = [
                ('channel', c_uint),
                ('blockID', c_ulonglong),
                ('timestamp', c_ulonglong),
                ('eStreamEventStatus', c_int),
                ('status', c_uint),
                ('reserve', c_uint),
                ]

#SDK => 宏定义 消息通道事件ID列表
MSG_EVENT_ID_EXPOSURE_END           = 0x9001
MSG_EVENT_ID_FRAME_TRIGGER          = 0x9002
MSG_EVENT_ID_FRAME_START            = 0x9003
MSG_EVENT_ID_ACQ_START              = 0x9004
MSG_EVENT_ID_ACQ_TRIGGER            = 0x9005
MSG_EVENT_ID_DATA_READ_OUT          = 0x9006

#SDK.h => struct GENICAM_SMsgChannelArg
class GENICAM_SMsgChannelArg(Structure):
    _fields_ = [
                ('eventID', c_ushort),
                ('channelID', c_ushort),
                ('blockID', c_ulonglong),
                ('timeStamp', c_ulonglong),
                ('reserve', c_uint * 8),
                ('paramNames', c_char * MAX_STRING_LENTH * MAX_PARAM_CNT),
                ('referenceParamCnt', c_uint),
                ]
    
#SDK.h =>  void (*connectCallBack)(const GENICAM_SConnectArg* pConnectArg)
connectCallBack = eval('CFUNCTYPE')(None, POINTER(GENICAM_SConnectArg))

#SDK.h => void (*connectCallBackEx)(const GENICAM_SConnectArg* pConnectArg, void* pUser)
connectCallBackEx = eval('CFUNCTYPE')(None, POINTER(GENICAM_SConnectArg), c_void_p)

#SDK.h => void (*paramUpdateCallBack)(const GENICAM_SParamUpdataArg* pParamUpdateArg)
paramUpdateCallBack = eval('CFUNCTYPE')(None, POINTER(GENICAM_SParamUpdataArg))

#SDK.h => void (*paramUpdateCallBackEx)(const GENICAM_SParamUpdataArg* pParamUpdateArg, void* pUser)
paramUpdateCallBackEx = eval('CFUNCTYPE')(None, POINTER(GENICAM_SParamUpdataArg), c_void_p)

#SDK.h => void (*streamCallBack)(const GENICAM_SStreamArg* pStreamArg)
streamCallBack = eval('CFUNCTYPE')(None, POINTER(GENICAM_SStreamArg))

#SDK.h => void (*streamCallBackEx)(const GENICAM_SStreamArg* pStreamArg, void *pUser)
streamCallBackEx = eval('CFUNCTYPE')(None, POINTER(GENICAM_SStreamArg), c_void_p)

#SDK.h => void (*msgChannelCallBackEx)(const GENICAM_SMsgChannelArg* pMsgChannelArg, void *pUser)
msgChannelCallBackEx = eval('CFUNCTYPE')(None, POINTER(GENICAM_SMsgChannelArg), c_void_p)

#SDK.h => struct GENICAM_EventSubscribe
class GENICAM_EventSubscribe(Structure):
    pass

GENICAM_EventSubscribe_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EventSubscribe))
GENICAM_EventSubscribe_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EventSubscribe))
GENICAM_EventSubscribe_subscribeConnectArgs = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EventSubscribe), connectCallBack)
GENICAM_EventSubscribe_unsubscribeConnectArgs = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EventSubscribe), connectCallBack)
GENICAM_EventSubscribe_subscribeParamUpdate = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EventSubscribe), paramUpdateCallBack)
GENICAM_EventSubscribe_unsubscribeParamUpdate = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EventSubscribe), paramUpdateCallBack)
GENICAM_EventSubscribe_subscribeStreamArg = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EventSubscribe), streamCallBack)
GENICAM_EventSubscribe_unsubscribeStreamArg = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EventSubscribe), streamCallBack)
GENICAM_EventSubscribe_subscribeConnectArgsEx = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EventSubscribe), connectCallBackEx, c_void_p)
GENICAM_EventSubscribe_unsubscribeConnectArgsEx = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EventSubscribe), connectCallBackEx, c_void_p)
GENICAM_EventSubscribe_subscribeParamUpdateEx = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EventSubscribe), paramUpdateCallBackEx, c_void_p)
GENICAM_EventSubscribe_unsubscribeParamUpdateEx = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EventSubscribe), paramUpdateCallBackEx, c_void_p)
GENICAM_EventSubscribe_subscribeStreamArgEx = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EventSubscribe), streamCallBackEx, c_void_p)
GENICAM_EventSubscribe_unsubscribeStreamArgEx = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EventSubscribe), streamCallBackEx, c_void_p)
GENICAM_EventSubscribe_subscribeMsgChannelEx = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EventSubscribe), msgChannelCallBackEx, c_void_p)
GENICAM_EventSubscribe_unsubscribeMsgChannelEx = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EventSubscribe), msgChannelCallBackEx, c_void_p)

GENICAM_EventSubscribe._fields_ = [
                                  ('priv', c_void_p),
                                  ('addRef', GENICAM_EventSubscribe_addRef),
                                  ('release', GENICAM_EventSubscribe_release),
                                  ('subscribeConnectArgs', GENICAM_EventSubscribe_subscribeConnectArgs),
                                  ('unsubscribeConnectArgs', GENICAM_EventSubscribe_unsubscribeConnectArgs),
                                  ('subscribeParamUpdate', GENICAM_EventSubscribe_subscribeParamUpdate),
                                  ('unsubscribeParamUpdate', GENICAM_EventSubscribe_unsubscribeParamUpdate),
                                  ('subscribeStreamArg', GENICAM_EventSubscribe_subscribeStreamArg),
                                  ('unsubscribeStreamArg', GENICAM_EventSubscribe_unsubscribeStreamArg),
                                  ('subscribeConnectArgsEx', GENICAM_EventSubscribe_subscribeConnectArgsEx),
                                  ('unsubscribeConnectArgsEx', GENICAM_EventSubscribe_unsubscribeConnectArgsEx),                                  
                                  ('subscribeParamUpdateEx', GENICAM_EventSubscribe_subscribeParamUpdateEx),
                                  ('unsubscribeParamUpdateEx', GENICAM_EventSubscribe_unsubscribeParamUpdateEx),
                                  ('subscribeStreamArgEx', GENICAM_EventSubscribe_subscribeStreamArgEx),
                                  ('unsubscribeStreamArgEx', GENICAM_EventSubscribe_unsubscribeStreamArgEx),
                                  ('subscribeMsgChannelEx', GENICAM_EventSubscribe_subscribeMsgChannelEx),
                                  ('unsubscribeMsgChannelEx', GENICAM_EventSubscribe_unsubscribeMsgChannelEx),
                                  ('reserve', c_uint * 15),
                                  ]

#SDK.h => struct GENICAM_EventSubscribeInfo
class GENICAM_EventSubscribeInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('reserved', c_uint * 31),
                ]

#SDK.h => GENICAM_createEventSubscribe(const GENICAM_EventSubscribeInfo* pEventSubscribeInfo, GENICAM_EventSubscribe** ppEventSubscribe)
GENICAM_createEventSubscribe = MVSDKdll.GENICAM_createEventSubscribe

#SDK.h => struct GENICAM_GigECamera
class GENICAM_GigECamera(Structure):
    pass

GENICAM_GigECamera_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_GigECamera))
GENICAM_GigECamera_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_GigECamera))
GENICAM_GigECamera_getIpAddress = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_GigECamera))
GENICAM_GigECamera_getSubnetMask = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_GigECamera))
GENICAM_GigECamera_getGateway = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_GigECamera))
GENICAM_GigECamera_getMacAddress = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_GigECamera))
GENICAM_GigECamera_forceIpAddress = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_GigECamera), c_char_p, c_char_p, c_char_p)
GENICAM_GigECamera_getAccessPermission = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_GigECamera))
GENICAM_GigECamera_getProtocolVersion = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_GigECamera))
GENICAM_GigECamera_getIPConfiguration = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_GigECamera))

GENICAM_GigECamera._fields_ = [
                               ('priv', c_void_p),
                               ('addRef', GENICAM_GigECamera_addRef),
                               ('release', GENICAM_GigECamera_release),
                               ('getIpAddress', GENICAM_GigECamera_getIpAddress),
                               ('getSubnetMask', GENICAM_GigECamera_getSubnetMask),
                               ('getGateway', GENICAM_GigECamera_getGateway),
                               ('getMacAddress', GENICAM_GigECamera_getMacAddress),
                               ('forceIpAddress', GENICAM_GigECamera_forceIpAddress),
                               ('getAccessPermission', GENICAM_GigECamera_getAccessPermission),
                               ('getProtocolVersion', GENICAM_GigECamera_getProtocolVersion),
                               ('getIPConfiguration', GENICAM_GigECamera_getIPConfiguration),
                               ('reserve', c_uint * 21),
                               ]

#SDK.h => struct GENICAM_GigECameraInfo
class GENICAM_GigECameraInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('reserved', c_uint * 31),
                ]

#SDK.h => createGigECamera(GENICAM_GigECameraInfo* pGigECameraInfo, GENICAM_GigECamera** ppGigECamera)
GENICAM_createGigECamera = MVSDKdll.GENICAM_createGigECamera

#SDK.h => struct GENICAM_GigEInterface
class GENICAM_GigEInterface(Structure):
    pass

GENICAM_GigEInterface_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_GigEInterface))
GENICAM_GigEInterface_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_GigEInterface))
GENICAM_GigEInterface_getDescription = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_GigEInterface))
GENICAM_GigEInterface_getIpAddress = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_GigEInterface))
GENICAM_GigEInterface_getSubnetMask = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_GigEInterface))
GENICAM_GigEInterface_getGateway = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_GigEInterface))
GENICAM_GigEInterface_getMacAddress = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_GigEInterface))

GENICAM_GigEInterface._fields_ = [
                                  ('priv', c_void_p),
                                  ('addRef', GENICAM_GigEInterface_addRef),
                                  ('release', GENICAM_GigEInterface_release),
                                  ('getDescription', GENICAM_GigEInterface_getDescription),
                                  ('getIpAddress', GENICAM_GigEInterface_getIpAddress),
                                  ('getSubnetMask', GENICAM_GigEInterface_getSubnetMask),
                                  ('getGateway', GENICAM_GigEInterface_getGateway),
                                  ('getMacAddress', GENICAM_GigEInterface_getMacAddress),
                                  ('reserve', c_uint * 24),
                                  ]

#SDK.h => struct GENICAM_GigEInterfaceInfo
class GENICAM_GigEInterfaceInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('reserved', c_uint * 31),
                ]

#SDK.h => GENICAM_createGigEInterface(GENICAM_GigEInterfaceInfo*pGigEInterfaceInfo, GENICAM_GigEInterface** ppGigEInterface)
GENICAM_createGigEInterface = MVSDKdll.GENICAM_createGigEInterface

#SDK.h => struct GENICAM_UsbCamera
class GENICAM_UsbCamera(Structure):
    pass

GENICAM_UsbCamera_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_UsbCamera))
GENICAM_UsbCamera_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_UsbCamera))
GENICAM_UsbCamera_getConfigurationValid = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_UsbCamera))
GENICAM_UsbCamera_getGenCPVersion = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_UsbCamera))
GENICAM_UsbCamera_getU3VVersion = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_UsbCamera))
GENICAM_UsbCamera_getDeviceGUID = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_UsbCamera))
GENICAM_UsbCamera_getFamilyName = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_UsbCamera))
GENICAM_UsbCamera_getU3VSerialNumber = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_UsbCamera))
GENICAM_UsbCamera_isLowSpeedSupported = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_UsbCamera))
GENICAM_UsbCamera_isFullSpeedSupported = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_UsbCamera))
GENICAM_UsbCamera_isHighSpeedSupported = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_UsbCamera))
GENICAM_UsbCamera_isSuperSpeedSupported = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_UsbCamera))
GENICAM_UsbCamera_getSpeed = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_UsbCamera))
GENICAM_UsbCamera_getMaxPower = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_UsbCamera))
GENICAM_UsbCamera_isDriverInstalled = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_UsbCamera))

GENICAM_UsbCamera._fields_ = [
                              ('priv', c_void_p),
                              ('addRef', GENICAM_UsbCamera_addRef),
                              ('release', GENICAM_UsbCamera_release),
                              ('getConfigurationValid', GENICAM_UsbCamera_getConfigurationValid),
                              ('getGenCPVersion', GENICAM_UsbCamera_getGenCPVersion),
                              ('getU3VVersion', GENICAM_UsbCamera_getU3VVersion),
                              ('getDeviceGUID', GENICAM_UsbCamera_getDeviceGUID),
                              ('getFamilyName', GENICAM_UsbCamera_getFamilyName),
                              ('getU3VSerialNumber', GENICAM_UsbCamera_getU3VSerialNumber),
                              ('isLowSpeedSupported', GENICAM_UsbCamera_isLowSpeedSupported),
                              ('isFullSpeedSupported', GENICAM_UsbCamera_isFullSpeedSupported),
                              ('isHighSpeedSupported', GENICAM_UsbCamera_isHighSpeedSupported),
                              ('isSuperSpeedSupported', GENICAM_UsbCamera_isSuperSpeedSupported),
                              ('getSpeed', GENICAM_UsbCamera_getSpeed),
                              ('getMaxPower', GENICAM_UsbCamera_getMaxPower),
                              ('isDriverInstalled', GENICAM_UsbCamera_isDriverInstalled),
                              ('reserve', c_uint * 16),
                              ]

#SDK.h => struct GENICAM_UsbCameraInfo
class GENICAM_UsbCameraInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('reserved', c_uint * 31),
                ]

#SDK.h => GENICAM_createUsbCamera(GENICAM_UsbCameraInfo* pUsbCameraInfo, GENICAM_UsbCamera** ppUsbCamera);
GENICAM_createUsbCamera = MVSDKdll.GENICAM_createUsbCamera

#SDK.h => struct GENICAM_UsbInterface
class GENICAM_UsbInterface(Structure):
    pass

GENICAM_UsbInterface_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_UsbInterface))
GENICAM_UsbInterface_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_UsbInterface))
GENICAM_UsbInterface_getDescription = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_UsbInterface))
GENICAM_UsbInterface_getVendorID = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_UsbInterface))
GENICAM_UsbInterface_getDeviceID = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_UsbInterface))
GENICAM_UsbInterface_getSubsystemID = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_UsbInterface))
GENICAM_UsbInterface_getRevision = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_UsbInterface))
GENICAM_UsbInterface_getSpeed = eval('CFUNCTYPE')(c_char_p, POINTER(GENICAM_UsbInterface))

GENICAM_UsbInterface._fields_ = [
                                 ('priv', c_void_p),
                                 ('addRef', GENICAM_UsbInterface_addRef),
                                 ('release', GENICAM_UsbInterface_release),
                                 ('getDescription', GENICAM_UsbInterface_getDescription),
                                 ('getVendorID', GENICAM_UsbInterface_getVendorID),
                                 ('getDeviceID', GENICAM_UsbInterface_getDeviceID),
                                 ('getSubsystemID', GENICAM_UsbInterface_getSubsystemID),
                                 ('getRevision', GENICAM_UsbInterface_getRevision),
                                 ('getSpeed', GENICAM_UsbInterface_getSpeed),
                                 ('reserve', c_uint * 23),
                                 ]

#SDK.h => struct GENICAM_UsbInterfaceInfo
class GENICAM_UsbInterfaceInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('reserved', c_uint * 31),                
                ]

#SDK.h => GENICAM_createUsbInterface(GENICAM_UsbInterfaceInfo*pUsbInterfaceInfo, GENICAM_UsbInterface** ppUsbInterface);
GENICAM_createUsbInterface = MVSDKdll.GENICAM_createUsbInterface

#SDK.h => struct GENICAM_IntNode
class GENICAM_IntNode(Structure):
    pass

GENICAM_IntNode_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_IntNode))
GENICAM_IntNode_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_IntNode))
GENICAM_IntNode_getValue = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_IntNode), POINTER(c_longlong))
GENICAM_IntNode_setValue = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_IntNode), c_longlong)
GENICAM_IntNode_getMinVal = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_IntNode), POINTER(c_longlong))
GENICAM_IntNode_getMaxVal = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_IntNode), POINTER(c_longlong))
GENICAM_IntNode_isValid = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_IntNode))
GENICAM_IntNode_isAvailable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_IntNode))
GENICAM_IntNode_isReadable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_IntNode))
GENICAM_IntNode_isWriteable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_IntNode))
GENICAM_IntNode_getIncrement = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_IntNode), POINTER(c_longlong))

GENICAM_IntNode._fields_ = [
                            ('priv', c_void_p),
                            ('addRef', GENICAM_IntNode_addRef),
                            ('release', GENICAM_IntNode_release),
                            ('getValue', GENICAM_IntNode_getValue),
                            ('setValue', GENICAM_IntNode_setValue),
                            ('getMinVal', GENICAM_IntNode_getMinVal),
                            ('getMaxVal', GENICAM_IntNode_getMaxVal),
                            ('isValid', GENICAM_IntNode_isValid),
                            ('isAvailable', GENICAM_IntNode_isAvailable),
                            ('isReadable', GENICAM_IntNode_isReadable),
                            ('isWriteable', GENICAM_IntNode_isWriteable),
                            ('getIncrement', GENICAM_IntNode_getIncrement),
                            ('reserve', c_uint * 20),
                            ]

#SDK.h => struct GENICAM_IntNodeInfo
class GENICAM_IntNodeInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('attrName', c_char * MAX_ATTR_NAME_LEN),
                ('reserved', c_uint * 31),
                ]
    
#SDK.h => GENICAM_createIntNode(GENICAM_IntNodeInfo* pIntNodeInfo, GENICAM_IntNode** ppIntNode)
GENICAM_createIntNode = MVSDKdll.GENICAM_createIntNode

#SDK.h => struct GENICAM_DoubleNode
class GENICAM_DoubleNode(Structure):
    pass

GENICAM_DoubleNode_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_DoubleNode))
GENICAM_DoubleNode_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_DoubleNode))
GENICAM_DoubleNode_getValue = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_DoubleNode), POINTER(c_double))
GENICAM_DoubleNode_setValue = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_DoubleNode), c_double)
GENICAM_DoubleNode_getMinVal = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_DoubleNode), POINTER(c_double))
GENICAM_DoubleNode_getMaxVal = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_DoubleNode), POINTER(c_double))
GENICAM_DoubleNode_isValid = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_DoubleNode))
GENICAM_DoubleNode_isAvailable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_DoubleNode))
GENICAM_DoubleNode_isReadable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_DoubleNode))
GENICAM_DoubleNode_isWriteable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_DoubleNode))

GENICAM_DoubleNode._fields_ = [
                               ('priv', c_void_p),
                               ('addRef', GENICAM_DoubleNode_addRef),
                               ('release', GENICAM_DoubleNode_release),
                               ('getValue', GENICAM_DoubleNode_getValue),
                               ('setValue', GENICAM_DoubleNode_setValue),
                               ('getMinVal', GENICAM_DoubleNode_getMinVal),
                               ('getMaxVal', GENICAM_DoubleNode_getMaxVal),
                               ('isValid', GENICAM_DoubleNode_isValid),
                               ('isAvailable', GENICAM_DoubleNode_isAvailable),
                               ('isReadable', GENICAM_DoubleNode_isReadable),
                               ('isWriteable', GENICAM_DoubleNode_isWriteable),
                               ('reserve', c_uint * 21),
                               ]

#SDK.h => struct GENICAM_DoubleNodeInfo
class GENICAM_DoubleNodeInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('attrName', c_char * MAX_ATTR_NAME_LEN),
                ('reserved', c_uint * 31),
                ]

#SDK.h => GENICAM_createDoubleNode(GENICAM_DoubleNodeInfo* pDoubleNodeInfo, GENICAM_DoubleNode** ppDoubleNode)
GENICAM_createDoubleNode = MVSDKdll.GENICAM_createDoubleNode

#SDK.h => struct GENICAM_EnumNode
class GENICAM_EnumNode(Structure):
    pass

GENICAM_EnumNode_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EnumNode))
GENICAM_EnumNode_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EnumNode))
GENICAM_EnumNode_getValueSymbol = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EnumNode), c_char_p, POINTER(c_uint))
GENICAM_EnumNode_setValueBySymbol = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EnumNode), c_char_p)
GENICAM_EnumNode_getEnumSymbolList = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EnumNode), POINTER(c_char * 256), POINTER(c_uint)) #???
GENICAM_EnumNode_isValid = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EnumNode))
GENICAM_EnumNode_isAvailable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EnumNode))
GENICAM_EnumNode_isReadable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EnumNode))
GENICAM_EnumNode_isWriteable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_EnumNode))

GENICAM_EnumNode._fields_ = [
                ('priv', c_void_p),
                ('addRef', GENICAM_EnumNode_addRef),
                ('release', GENICAM_EnumNode_release),
                ('getValueSymbol', GENICAM_EnumNode_getValueSymbol),
                ('setValueBySymbol', GENICAM_EnumNode_setValueBySymbol),
                ('getEnumSymbolList', GENICAM_EnumNode_getEnumSymbolList),
                ('isValid', GENICAM_EnumNode_isValid),
                ('isAvailable', GENICAM_EnumNode_isAvailable),
                ('isReadable', GENICAM_EnumNode_isReadable),
                ('isWriteable', GENICAM_EnumNode_isWriteable),
                ('reserve', c_uint * 22),   
                ]

#SDK.h => struct GENICAM_EnumNodeInfo
class GENICAM_EnumNodeInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('attrName', c_char * MAX_ATTR_NAME_LEN),
                ('reserved', c_uint * 31),
                ]

#SDK.h => GENICAM_createEnumNode(GENICAM_EnumNodeInfo* pEnumNodeInfo, GENICAM_EnumNode** ppEnumNode)
GENICAM_createEnumNode = MVSDKdll.GENICAM_createEnumNode

#SDK.h => struct GENICAM_BoolNode
class GENICAM_BoolNode(Structure):
    pass

GENICAM_BoolNode_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_BoolNode))
GENICAM_BoolNode_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_BoolNode))
GENICAM_BoolNode_getValue = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_BoolNode), POINTER(c_uint))
GENICAM_BoolNode_setValue = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_BoolNode), c_uint)
GENICAM_BoolNode_isValid = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_BoolNode))
GENICAM_BoolNode_isAvailable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_BoolNode))
GENICAM_BoolNode_isReadable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_BoolNode))
GENICAM_BoolNode_isWriteable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_BoolNode))

GENICAM_BoolNode._fields_ = [
                            ('priv', c_void_p),
                            ('addRef', GENICAM_BoolNode_addRef),
                            ('release', GENICAM_BoolNode_release),
                            ('getValue', GENICAM_BoolNode_getValue),
                            ('setValue', GENICAM_BoolNode_setValue),
                            ('isValid', GENICAM_BoolNode_isValid),
                            ('isAvailable', GENICAM_BoolNode_isAvailable),
                            ('isReadable', GENICAM_BoolNode_isReadable),
                            ('isWriteable', GENICAM_BoolNode_isWriteable),
                            ('reserve', c_uint * 23),
                            ]

#SDK.h => struct GENICAM_BoolNodeInfo
class GENICAM_BoolNodeInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('attrName', c_char * MAX_ATTR_NAME_LEN),
                ('reserved', c_uint * 31),
                ]
    
#SDK.h => GENICAM_createBoolNode(GENICAM_BoolNodeInfo* pBoolNodeInfo, GENICAM_BoolNode** ppBoolNode)
GENICAM_createBoolNode = MVSDKdll.GENICAM_createBoolNode

#SDK.h => struct GENICAM_CmdNode
class GENICAM_CmdNode(Structure):
    pass

GENICAM_CmdNode_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_CmdNode))
GENICAM_CmdNode_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_CmdNode))
GENICAM_CmdNode_execute = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_CmdNode))
GENICAM_CmdNode_isValid = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_CmdNode))
GENICAM_CmdNode_isAvailable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_CmdNode))
GENICAM_CmdNode_isReadable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_CmdNode))
GENICAM_CmdNode_isWriteable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_CmdNode))

GENICAM_CmdNode._fields_ = [
                            ('priv', c_void_p),
                            ('addRef', GENICAM_CmdNode_addRef),
                            ('release', GENICAM_CmdNode_release),
                            ('execute', GENICAM_CmdNode_execute),
                            ('isValid', GENICAM_CmdNode_isValid),
                            ('isAvailable', GENICAM_CmdNode_isAvailable),
                            ('isReadable', GENICAM_CmdNode_isReadable),
                            ('isWriteable', GENICAM_CmdNode_isWriteable),
                            ('reserve', c_uint * 24),
                            ]

#SDK.h => struct GENICAM_CmdNodeInfo
class GENICAM_CmdNodeInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('attrName', c_char * MAX_ATTR_NAME_LEN),
                ('reserved', c_uint * 31),
                ]

#SDK.h => GENICAM_createCmdNode(GENICAM_CmdNodeInfo* pCmdNodeInfo, GENICAM_CmdNode** ppCmdNode)
GENICAM_createCmdNode = MVSDKdll.GENICAM_createCmdNode

#SDK.h => struct GENICAM_StringNode
class GENICAM_StringNode(Structure):
    pass

GENICAM_StringNode_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StringNode))
GENICAM_StringNode_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StringNode))
GENICAM_StringNode_getValue = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StringNode), c_char_p, POINTER(c_uint))
GENICAM_StringNode_setValue = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StringNode), c_char_p)
GENICAM_StringNode_isValid = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StringNode))
GENICAM_StringNode_isAvailable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StringNode))
GENICAM_StringNode_isReadable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StringNode))
GENICAM_StringNode_isWriteable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_StringNode))

GENICAM_StringNode._fields_ = [
                               ('priv', c_void_p),
                               ('addRef', GENICAM_StringNode_addRef),
                               ('release', GENICAM_StringNode_release),
                               ('getValue', GENICAM_StringNode_getValue),
                               ('setValue', GENICAM_StringNode_setValue),
                               ('isValid', GENICAM_StringNode_isValid),
                               ('isAvailable', GENICAM_StringNode_isAvailable),
                               ('isReadable', GENICAM_StringNode_isReadable),
                               ('isWriteable', GENICAM_StringNode_isWriteable),
                               ('reserve', c_uint * 23),
                               ]

#SDK.h => struct GENICAM_StringNodeInfo
class GENICAM_StringNodeInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('attrName', c_char * MAX_ATTR_NAME_LEN),
                ('reserved', c_uint * 31),
                ]

#SDK.h => GENICAM_createStringNode(GENICAM_StringNodeInfo* pStringNodeInfo, GENICAM_StringNode** ppStringNode)
GENICAM_createStringNode = MVSDKdll.GENICAM_createStringNode

#SDK.h => struct GENICAM_AcquisitionControl
class GENICAM_AcquisitionControl(Structure):
    pass

GENICAM_AcquisitionControl_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_AcquisitionControl))
GENICAM_AcquisitionControl_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_AcquisitionControl))
GENICAM_AcquisitionControl_acquisitionFrameCount = eval('CFUNCTYPE')(GENICAM_IntNode, POINTER(GENICAM_AcquisitionControl))
GENICAM_AcquisitionControl_acquisitionFrameRate = eval('CFUNCTYPE')(GENICAM_DoubleNode, POINTER(GENICAM_AcquisitionControl))
GENICAM_AcquisitionControl_acquisitionFrameRateEnable = eval('CFUNCTYPE')(GENICAM_BoolNode, POINTER(GENICAM_AcquisitionControl))
GENICAM_AcquisitionControl_acquisitionMode = eval('CFUNCTYPE')(GENICAM_EnumNode, POINTER(GENICAM_AcquisitionControl))
GENICAM_AcquisitionControl_exposureAuto = eval('CFUNCTYPE')(GENICAM_EnumNode, POINTER(GENICAM_AcquisitionControl))
GENICAM_AcquisitionControl_exposureMode = eval('CFUNCTYPE')(GENICAM_EnumNode, POINTER(GENICAM_AcquisitionControl))
GENICAM_AcquisitionControl_exposureTime = eval('CFUNCTYPE')(GENICAM_DoubleNode, POINTER(GENICAM_AcquisitionControl))
GENICAM_AcquisitionControl_triggerActivation = eval('CFUNCTYPE')(GENICAM_EnumNode, POINTER(GENICAM_AcquisitionControl))
GENICAM_AcquisitionControl_triggerDelay = eval('CFUNCTYPE')(GENICAM_DoubleNode, POINTER(GENICAM_AcquisitionControl))
GENICAM_AcquisitionControl_triggerMode = eval('CFUNCTYPE')(GENICAM_EnumNode, POINTER(GENICAM_AcquisitionControl))
GENICAM_AcquisitionControl_triggerSelector = eval('CFUNCTYPE')(GENICAM_EnumNode, POINTER(GENICAM_AcquisitionControl))
GENICAM_AcquisitionControl_triggerSource = eval('CFUNCTYPE')(GENICAM_EnumNode, POINTER(GENICAM_AcquisitionControl))
GENICAM_AcquisitionControl_triggerSoftware = eval('CFUNCTYPE')(GENICAM_CmdNode, POINTER(GENICAM_AcquisitionControl))
    
GENICAM_AcquisitionControl._fields_ = [
                                       ('priv', c_void_p),
                                       ('addRef', GENICAM_AcquisitionControl_addRef),
                                       ('release', GENICAM_AcquisitionControl_release),
                                       ('acquisitionFrameCount', GENICAM_AcquisitionControl_acquisitionFrameCount),
                                       ('acquisitionFrameRate', GENICAM_AcquisitionControl_acquisitionFrameRate),
                                       ('acquisitionFrameRateEnable', GENICAM_AcquisitionControl_acquisitionFrameRateEnable),
                                       ('acquisitionMode', GENICAM_AcquisitionControl_acquisitionMode),
                                       ('exposureAuto', GENICAM_AcquisitionControl_exposureAuto),
                                       ('exposureMode', GENICAM_AcquisitionControl_exposureMode),
                                       ('exposureTime', GENICAM_AcquisitionControl_exposureTime),
                                       ('triggerActivation', GENICAM_AcquisitionControl_triggerActivation),
                                       ('triggerDelay', GENICAM_AcquisitionControl_triggerDelay),
                                       ('triggerMode', GENICAM_AcquisitionControl_triggerMode),
                                       ('triggerSelector', GENICAM_AcquisitionControl_triggerSelector),
                                       ('triggerSource', GENICAM_AcquisitionControl_triggerSource),
                                       ('triggerSoftware', GENICAM_AcquisitionControl_triggerSoftware),
                                       ('reserve', c_uint * 17),
                                       ]

#SDK.h => struct GENICAM_AcquisitionControlInfo
class GENICAM_AcquisitionControlInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('reserved', c_uint * 31),
                ]
    
#SDK.h => GENICAM_createAcquisitionControl(GENICAM_AcquisitionControlInfo*pAcquisitionControlInfo, GENICAM_AcquisitionControl** ppAcquisitionControl)
GENICAM_createAcquisitionControl = MVSDKdll.GENICAM_createAcquisitionControl

#SDK.h => enum GENICAM_EConfigSet
GENICAM_EConfigSet = enum(
                         userSet1 = 1,
                         userSet2 = 2,
                         userSetInvalid = 3,
                         )

#SDK.h => struct GENICAM_UserSetControl
class GENICAM_UserSetControl(Structure):
    pass

GENICAM_UserSetControl_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_UserSetControl))
GENICAM_UserSetControl_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_UserSetControl))
GENICAM_UserSetControl_restoreDefault = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_UserSetControl))
GENICAM_UserSetControl_setCurrentUserSet = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_UserSetControl), c_int)
GENICAM_UserSetControl_saveUserSet = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_UserSetControl), c_int)
GENICAM_UserSetControl_getCurrentUserSet = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_UserSetControl))
GENICAM_UserSetControl_isAvailable = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_UserSetControl))

GENICAM_UserSetControl._fields_ = [
                                   ('priv', c_void_p),
                                   ('addRef', GENICAM_UserSetControl_addRef),
                                   ('release', GENICAM_UserSetControl_release),
                                   ('restoreDefault', GENICAM_UserSetControl_restoreDefault),
                                   ('setCurrentUserSet', GENICAM_UserSetControl_setCurrentUserSet),
                                   ('saveUserSet', GENICAM_UserSetControl_saveUserSet),
                                   ('getCurrentUserSet', GENICAM_UserSetControl_getCurrentUserSet),
                                   ('isAvailable', GENICAM_UserSetControl_isAvailable),
                                   ('reserve', c_uint * 24),
                                   ]

#SDK.h => struct GENICAM_UserSetControlInfo
class GENICAM_UserSetControlInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('reserved', c_uint * 31),
                ]

#SDK.h => GENICAM_createUserSetControl(GENICAM_UserSetControlInfo* pUserSetControlInfo, GENICAM_UserSetControl** ppUserSetControl)
GENICAM_createUserSetControl = MVSDKdll.GENICAM_createUserSetControl

#SDK.h => struct GENICAM_ISPControl
class GENICAM_ISPControl(Structure):
    pass

GENICAM_ISPControl_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_ISPControl))
GENICAM_ISPControl_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_ISPControl))
GENICAM_ISPControl_brightness = eval('CFUNCTYPE')(GENICAM_IntNode, POINTER(GENICAM_ISPControl))
GENICAM_ISPControl_sharpness = eval('CFUNCTYPE')(GENICAM_IntNode, POINTER(GENICAM_ISPControl))
GENICAM_ISPControl_sharpnessAuto = eval('CFUNCTYPE')(GENICAM_BoolNode, POINTER(GENICAM_ISPControl))
GENICAM_ISPControl_sharpnessEnable = eval('CFUNCTYPE')(GENICAM_EnumNode, POINTER(GENICAM_ISPControl))
GENICAM_ISPControl_contrast = eval('CFUNCTYPE')(GENICAM_IntNode, POINTER(GENICAM_ISPControl))
GENICAM_ISPControl_hue = eval('CFUNCTYPE')(GENICAM_IntNode, POINTER(GENICAM_ISPControl))
GENICAM_ISPControl_saturation = eval('CFUNCTYPE')(GENICAM_IntNode, POINTER(GENICAM_ISPControl))

GENICAM_ISPControl._fields_ = [
                               ('priv', c_void_p),
                               ('addRef', GENICAM_ISPControl_addRef),
                               ('release', GENICAM_ISPControl_release),
                               ('brightness', GENICAM_ISPControl_brightness),
                               ('sharpness', GENICAM_ISPControl_sharpness),
                               ('sharpnessAuto', GENICAM_ISPControl_sharpnessAuto),
                               ('sharpnessEnable', GENICAM_ISPControl_sharpnessEnable),
                               ('contrast', GENICAM_ISPControl_contrast),
                               ('hue', GENICAM_ISPControl_hue),
                               ('saturation', GENICAM_ISPControl_saturation),
                               ('reserved', c_uint * 22),
                               ]

#SDK.h => struct GENICAM_ISPControlInfo
class GENICAM_ISPControlInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('reserved', c_uint * 31),
                ]
     
#SDK.h => GENICAM_createISPControl(GENICAM_ISPControlInfo* pISPControlInfo, GENICAM_ISPControl** ppISPControl)
GENICAM_createISPControl = MVSDKdll.GENICAM_createISPControl 
 
#SDK.h => struct GENICAM_AnalogControl
class GENICAM_AnalogControl(Structure):
    pass
 
GENICAM_AnalogControl_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_AnalogControl))
GENICAM_AnalogControl_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_AnalogControl))
GENICAM_AnalogControl_blackLevelSelector = eval('CFUNCTYPE')(GENICAM_EnumNode, POINTER(GENICAM_AnalogControl))
GENICAM_AnalogControl_blackLevelAuto = eval('CFUNCTYPE')(GENICAM_EnumNode, POINTER(GENICAM_AnalogControl))
GENICAM_AnalogControl_blackLevel = eval('CFUNCTYPE')(GENICAM_IntNode, POINTER(GENICAM_AnalogControl))
GENICAM_AnalogControl_gainAuto = eval('CFUNCTYPE')(GENICAM_EnumNode, POINTER(GENICAM_AnalogControl))
GENICAM_AnalogControl_gainRaw = eval('CFUNCTYPE')(GENICAM_DoubleNode, POINTER(GENICAM_AnalogControl))
GENICAM_AnalogControl_gamma = eval('CFUNCTYPE')(GENICAM_DoubleNode, POINTER(GENICAM_AnalogControl))
GENICAM_AnalogControl_balanceRatioSelector = eval('CFUNCTYPE')(GENICAM_EnumNode, POINTER(GENICAM_AnalogControl))
GENICAM_AnalogControl_balanceWhiteAuto = eval('CFUNCTYPE')(GENICAM_EnumNode, POINTER(GENICAM_AnalogControl))
GENICAM_AnalogControl_balanceRatio = eval('CFUNCTYPE')(GENICAM_DoubleNode, POINTER(GENICAM_AnalogControl))

GENICAM_AnalogControl._fields_ = [
                                  ('priv', c_void_p),
                                  ('addRef', GENICAM_AnalogControl_addRef),
                                  ('release', GENICAM_AnalogControl_release),
                                  ('blackLevelSelector', GENICAM_AnalogControl_blackLevelSelector),
                                  ('blackLevelAuto', GENICAM_AnalogControl_blackLevelAuto),
                                  ('blackLevel', GENICAM_AnalogControl_blackLevel),
                                  ('gainAuto', GENICAM_AnalogControl_gainAuto),
                                  ('gainRaw', GENICAM_AnalogControl_gainRaw),
                                  ('gamma', GENICAM_AnalogControl_gamma),
                                  ('balanceRatioSelector', GENICAM_AnalogControl_balanceRatioSelector),
                                  ('balanceWhiteAuto', GENICAM_AnalogControl_balanceWhiteAuto),
                                  ('balanceRatio', GENICAM_AnalogControl_balanceRatio),
                                  ('reserve', c_uint * 20),
                                  ]

#SDK.h => struct GENICAM_AnalogControlInfo
class GENICAM_AnalogControlInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('reserved', c_uint * 31),
                ]

#SDK.h => GENICAM_createAnalogControl(GENICAM_AnalogControlInfo* pAnalogControlInfo, GENICAM_AnalogControl** ppAnalogControl)
GENICAM_createAnalogControl = MVSDKdll.GENICAM_createAnalogControl

#SDK.h => struct GENICAM_DeviceControl
class GENICAM_DeviceControl(Structure):
    pass

GENICAM_DeviceControl_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_DeviceControl))   
GENICAM_DeviceControl_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_DeviceControl))
GENICAM_DeviceControl_deviceUserID = eval('CFUNCTYPE')(GENICAM_StringNode, POINTER(GENICAM_DeviceControl))

GENICAM_DeviceControl._fields_ = [
                                  ('priv', c_void_p),
                                  ('addRef', GENICAM_DeviceControl_addRef),
                                  ('release', GENICAM_DeviceControl_release),
                                  ('deviceUserID', GENICAM_DeviceControl_deviceUserID),
                                  ('reserve', c_uint * 28),
                                  ]

#SDK.h => struct GENICAM_DeviceControlInfo
class GENICAM_DeviceControlInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('reserved', c_uint * 31),                
                ]

#SDK.h => GENICAM_createDeviceControl(GENICAM_DeviceControlInfo* pDeviceControlInfo, GENICAM_DeviceControl** ppDeviceControl)
GENICAM_createDeviceControl = MVSDKdll.GENICAM_createDeviceControl

#SDK.h => struct GENICAM_DigitalIOControl
class GENICAM_DigitalIOControl(Structure):
    pass

GENICAM_DigitalIOControl_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_DigitalIOControl))
GENICAM_DigitalIOControl_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_DigitalIOControl))
GENICAM_DigitalIOControl_lineSelector = eval('CFUNCTYPE')(GENICAM_EnumNode, POINTER(GENICAM_DigitalIOControl))
GENICAM_DigitalIOControl_lineDebouncerTimeAbs = eval('CFUNCTYPE')(GENICAM_DoubleNode, POINTER(GENICAM_DigitalIOControl))
GENICAM_DigitalIOControl_userOutputSelector = eval('CFUNCTYPE')(GENICAM_EnumNode, POINTER(GENICAM_DigitalIOControl))
GENICAM_DigitalIOControl_userOutputValue = eval('CFUNCTYPE')(GENICAM_BoolNode, POINTER(GENICAM_DigitalIOControl))

GENICAM_DigitalIOControl._fields_ = [
                                     ('priv', c_void_p),
                                     ('addRef', GENICAM_DigitalIOControl_addRef),
                                     ('release', GENICAM_DigitalIOControl_release),
                                     ('lineSelector', GENICAM_DigitalIOControl_lineSelector),
                                     ('lineDebouncerTimeAbs', GENICAM_DigitalIOControl_lineDebouncerTimeAbs),
                                     ('userOutputSelector', GENICAM_DigitalIOControl_userOutputSelector),
                                     ('userOutputValue', GENICAM_DigitalIOControl_userOutputValue),
                                     ('reserve', c_uint * 25),
                                     ]

#SDK.h => struct GENICAM_DigitalIOControlInfo
class GENICAM_DigitalIOControlInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('reserved', c_uint * 31),
                ]

#SDK.h => GENICAM_createDigitalIOControl(GENICAM_DigitalIOControlInfo* pDigitalIOControlInfo, GENICAM_DigitalIOControl** ppDigitalIOControl)
GENICAM_createDigitalIOControl = MVSDKdll.GENICAM_createDigitalIOControl

#SDK.h => struct GENICAM_TransportLayerControl
class GENICAM_TransportLayerControl(Structure):
    pass

GENICAM_TransportLayerControl_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_TransportLayerControl))
GENICAM_TransportLayerControl_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_TransportLayerControl))
GENICAM_TransportLayerControl_gevSCPD = eval('CFUNCTYPE')(GENICAM_IntNode, POINTER(GENICAM_TransportLayerControl))

GENICAM_TransportLayerControl._fields_ = [
                                          ('priv', c_void_p),
                                          ('addRef', GENICAM_TransportLayerControl_addRef),
                                          ('release', GENICAM_TransportLayerControl_release),
                                          ('gevSCPD', GENICAM_TransportLayerControl_gevSCPD),
                                          ('reserve', c_uint * 28),
                                          ]

#SDK.h => struct GENICAM_TransportLayerControlInfo
class GENICAM_TransportLayerControlInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('reserved', c_uint * 31),
                ]

#SDK.h => GENICAM_createTransportLayerControl(GENICAM_TransportLayerControlInfo* pTransportControlInfo, GENICAM_TransportLayerControl** ppTransportControl)
GENICAM_createTransportLayerControl = MVSDKdll.GENICAM_createTransportLayerControl

  
#SDK.h => struct GENICAM_ImageFormatControl
class GENICAM_ImageFormatControl(Structure):
    pass

GENICAM_ImageFormatControl_addRef = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_ImageFormatControl))
GENICAM_ImageFormatControl_release = eval('CFUNCTYPE')(c_int, POINTER(GENICAM_ImageFormatControl))
GENICAM_ImageFormatControl_height = eval('CFUNCTYPE')(GENICAM_IntNode, POINTER(GENICAM_ImageFormatControl))
GENICAM_ImageFormatControl_width = eval('CFUNCTYPE')(GENICAM_IntNode, POINTER(GENICAM_ImageFormatControl))
GENICAM_ImageFormatControl_offsetX = eval('CFUNCTYPE')(GENICAM_IntNode, POINTER(GENICAM_ImageFormatControl))
GENICAM_ImageFormatControl_offsetY = eval('CFUNCTYPE')(GENICAM_IntNode, POINTER(GENICAM_ImageFormatControl))
GENICAM_ImageFormatControl_pixelFormat = eval('CFUNCTYPE')(GENICAM_EnumNode, POINTER(GENICAM_ImageFormatControl))
GENICAM_ImageFormatControl_reverseX = eval('CFUNCTYPE')(GENICAM_BoolNode, POINTER(GENICAM_ImageFormatControl))
GENICAM_ImageFormatControl_reverseY = eval('CFUNCTYPE')(GENICAM_BoolNode, POINTER(GENICAM_ImageFormatControl))
  
GENICAM_ImageFormatControl._fields_ = [
                                       ('priv', c_void_p),
                                       ('addRef', GENICAM_ImageFormatControl_addRef),
                                       ('release', GENICAM_ImageFormatControl_release),
                                       ('height', GENICAM_ImageFormatControl_height),
                                       ('width', GENICAM_ImageFormatControl_width),
                                       ('offsetX', GENICAM_ImageFormatControl_offsetX),
                                       ('offsetY', GENICAM_ImageFormatControl_offsetY),
                                       ('pixelFormat', GENICAM_ImageFormatControl_pixelFormat),
                                       ('reverseX', GENICAM_ImageFormatControl_reverseX),
                                       ('reverseY', GENICAM_ImageFormatControl_reverseY),
                                       ('reserve', c_uint * 22),
                                       ]  

#SDK.h => struct GENICAM_ImageFormatControlInfo
class GENICAM_ImageFormatControlInfo(Structure):
    _fields_ = [
                ('pCamera', POINTER(GENICAM_Camera)),
                ('reserved', c_uint * 31),
                ]

#SDK.h => GENICAM_createImageFormatControl(GENICAM_ImageFormatControlInfo* pImageFormatControlInfo, GENICAM_ImageFormatControl** ppImageFormatControl)
GENICAM_createImageFormatControl = MVSDKdll.GENICAM_createImageFormatControl
