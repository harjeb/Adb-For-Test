#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Created on 2015年4月28日

@author: xuxu
'''

#图片处理，需要PIL库

import tempfile
import os
import shutil
from PIL import Image
import cv2
from adbUtils import ADB

PATH = lambda p: os.path.abspath(p)

class ImageUtils(object):

    def __init__(self, device_id=""):
        """
        初始化，获取系统临时文件存放目录
        """
        self.utils = ADB(device_id)
        self.tempFile = tempfile.gettempdir()

    def screenShot(self, device=''):
        """
        截取设备屏幕
        device 参数为 区分多模拟器时的id名,可以自行设定
        """
        temp = device + 'temp'
        self.utils.shell("screencap -p /sdcard/%s.png" % temp).wait()
        self.utils.adb("pull /sdcard/%s.png %s" % (temp, self.tempFile)).wait()

        return self

    def writeToFile(self, dirPath, imageName, form = "png"):
        """
        将截屏文件写到本地
        usage: screenShot().writeToFile("d:\\screen", "image")
        """
        if not os.path.isdir(dirPath):
            os.makedirs(dirPath)
        shutil.copyfile(PATH("%s/temp.png" %self.tempFile), PATH("%s/%s.%s" %(dirPath, imageName, form)))
        self.utils.shell("rm /data/local/tmp/temp.png")

    def loadImage(self, imageName):
        """
        加载本地图片
        usage: lodImage("d:\\screen\\image.png")
        """
        if os.path.isfile(imageName):
            load = Image.open(imageName)
            return load
        else:
            print("image is not exist")

    def subImage(self, box):
        """
        截取指定像素区域的图片
        usage: box = (100, 100, 600, 600)
              screenShot().subImage(box)
        """
        image = Image.open(PATH("%s/temp.png" %self.tempFile))
        newImage = image.crop(box)
        newImage.save(PATH("%s/temp.png" %self.tempFile))

        return self

    #http://testerhome.com/topics/202
    def sameAs(self,loadImage):
        """
        比较两张截图的相似度，完全相似返回True
        usage： load = loadImage("d:\\screen\\image.png")
                screen().subImage(100, 100, 400, 400).sameAs(load)
        """
        import math
        import operator

        image1 = Image.open(PATH("%s/temp.png" %self.tempFile))
        image2 = loadImage


        histogram1 = image1.histogram()
        histogram2 = image2.histogram()

        differ = math.sqrt(reduce(operator.add, list(map(lambda a,b: (a-b)**2, \
                                                         histogram1, histogram2)))/len(histogram1))
        if differ == 0:
            return True
        else:
            return False

    # calc center point
    def findpic(self, template, origin, value=0.8):
        """
        返回找到图片的中心点坐标
        template 为需要寻找的部分图片path
        origin 为全图path
        0.8 为 80%相似度
        usage：
            image = ImageUtils(devicename)
            loc = image.findpic(pic, origin)
        """
        img = cv2.imread(origin, 0)
        template = cv2.imread(template, 0)
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img,template,cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > value:
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            loc = (int((bottom_right[0]+top_left[0])/2), int((bottom_right[1]+top_left[1])/2))
            return loc
        else:
            print('Not found pic!!!')
            return None

    def exist(self, temp, origin, value=0.8):
        img = cv2.imread(origin, 0)
        template = cv2.imread(temp, 0)
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > value:
            return True
        else:
            return False

