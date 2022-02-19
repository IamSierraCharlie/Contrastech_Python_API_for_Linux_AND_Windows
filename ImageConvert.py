#!/usr/bin/env python
# coding: utf-8
import os
from ctypes import *

# 加载ImageConvert库
# 32bit
#ImageConvertdll = cdll.LoadLibrary("./dll/x86/libImageConvert.so")
# 64bit
if os.name == 'nt':  # for windows
    print('loaded dll for windows')
    ImageConvertdll = cdll.LoadLibrary("C:\\Program Files\\iCentral\iCentral\\Application\\x64\\ImageConvert.dll")
else:
    print('loaded dll for linux')
    ImageConvertdll = cdll.LoadLibrary("/opt/iCentral/iCentral/lib/libImageConvert.so")


def enum(**enums):
    return type('Enum', (), enums)


# ImageConvert.h => enum tagIMGCNV_EErr
IMGCNV_EErr = enum(
                      IMGCNV_SUCCESS=0,
                      IMGCNV_ILLEGAL_PARAM=1,
                      IMGCNV_ERR_ORDER=2,
                      IMGCNV_NO_MEMORY=3,
                      IMGCNV_NOT_SUPPORT=4,
                      )


# ImageConvert.h => struct tagIMGCNV_SOpenParam
class IMGCNV_SOpenParam(Structure):
    _fields_ = [
                ('width', c_int),
                ('height', c_int),
                ('paddingX', c_int),
                ('paddingY', c_int),
                ('dataSize', c_int),
                ('pixelFormat', c_uint),
                ]

# ImageConvert.h => IMGCNV_ConvertToBGR24(unsigned char* pSrcData, IMGCNV_SOpenParam* pOpenParam, unsigned char*
# pDstData, int* pDstDataSize)
IMGCNV_ConvertToBGR24 = ImageConvertdll.IMGCNV_ConvertToBGR24

# ImageConvert.h => IMGCNV_ConvertToRGB24(unsigned char* pSrcData, IMGCNV_SOpenParam* pOpenParam, unsigned char*
# pDstData, int* pDstDataSize)
IMGCNV_ConvertToRGB24 = ImageConvertdll.IMGCNV_ConvertToRGB24

# ImageConvert.h => IMGCNV_ConvertToMono8(unsigned char* pSrcData, IMGCNV_SOpenParam* pOpenParam, unsigned char*
# pDstData, int* pDstDataSize)
IMGCNV_ConvertToMono8 = ImageConvertdll.IMGCNV_ConvertToMono8
