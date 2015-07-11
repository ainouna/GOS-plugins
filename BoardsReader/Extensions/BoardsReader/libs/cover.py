# -*- coding: utf-8 -*-

###################################################
# LOCAL import
###################################################
from asynccall import AsyncMethod

###################################################
# FOREIGN import
###################################################
from Tools.LoadPixmap import LoadPixmap
from Components.Pixmap import Pixmap
from enigma import ePicLoad

import threading

# only one icon can be decoded at time
gCoverLock = threading.Lock()
gPicLoad = ePicLoad()

class Cover(Pixmap):
    def __init__(self):
        Pixmap.__init__(self)       
        self.currIconPath = ''
        self.waitIconPath = ''

    def onShow(self):      
        Pixmap.onShow(self)
        
    # this function should be called only from mainThread
    # filename - path to image wich will be decoded
    # callBackFun - the function wich will be called after decoding
    # if decoding will be finished with success
    def decodeCover(self, filename, callBackFun, ident):
        
        #checki if decoding is needed
        if filename != self.currIconPath and filename != self.waitIconPath:
            self.waitIconPath = filename
            #run new thread
            AsyncMethod(self.decode, self.decodeCallBack)(filename, callBackFun, ident, self.instance.size().width(), self.instance.size().height())
        else:
            print "Cover: Not Neeed 1"
            callBackFun(  {"Changed": False, "FileName": filename, "Ident": ident}  )
        return
    
    # this method should be called only from mainThread
    # ptrPixmap - decoded pixelmap to set
    # filename  - path to image corresponding to pixelmap 
    def updatePixmap(self, ptrPixmap, filename):
        if ptrPixmap != None:
            self.currIconPath = filename
            self.instance.setPixmap(ptrPixmap)

    # this function is called in localThread
    def decode(self, filename, callBackFun, ident, width, height):
        retDict = None
        # get lock only one thread can operate on the icon
        print "Cover: decodeIcon before lock"
        global gCoverLock
        gCoverLock.acquire()
        
        try:
            print "Cover: decodeIcon after lock"
            global gPicLoad
            
            gPicLoad.setPara((width, height, 1, 1, False, 1, "#00000000"))
            ret = gPicLoad.startDecode(filename, 0, 0, 0)
            print "Cover: startDecode ret [%s]" % str(ret)
            if not ret:
                print("icon has decoded sucesfull")
                
                ptr = gPicLoad.getData()
                if ptr != None:
                    retDict = {"Pixmap": ptr, "FileName": filename, "CallBackFun": callBackFun, "Ident": ident}
                else:
                    print "Cover: getData ERROR"
            else:
                print "Cover: decode ERROR"
        except:
            pass
        
        return retDict
        
    # this function is called in localThread
    def decodeCallBack(self, retDict):
        print "Cover: decodeCallBack"
        global gCoverLock
        gCoverLock.release()
        
        if None != retDict:
            #call callBackFunction
            retDict["CallBackFun"](  {"Changed": True, "Pixmap": retDict["Pixmap"], "FileName": retDict["FileName"], "Ident": retDict["Ident"]}  )
        return
        
class Cover2(Pixmap):
    def __init__(self):
        Pixmap.__init__(self)
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.paintIconPixmapCB)
        self.paramsSet = False

    def onShow(self):
        Pixmap.onShow(self)

    def paintIconPixmapCB(self, picInfo=None):
        t = threading.currentThread()
        print "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO: " + t.name
        ptr = self.picload.getData()
        if ptr != None:
            self.instance.setPixmap(ptr)
            self.show()

    def updateIcon(self, filename):
        t = threading.currentThread()
        print "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB: " + t.name
        if not self.paramsSet:
            self.picload.setPara((self.instance.size().width(), self.instance.size().height(), 1, 1, False, 1, "#00000000"))
            self.paramsSet = True
        self.picload.startDecode(filename)
        
class Cover3(Pixmap):
    def __init__(self):
        Pixmap.__init__(self)
        
    def onShow(self):
        Pixmap.onShow(self)

    def setPixmap(self, ptr):
        self.instance.setPixmap(ptr)
        