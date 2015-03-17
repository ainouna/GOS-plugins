# -*- coding: utf-8 -*-

###################################################
# LOCAL import
###################################################
from libs.asynccall import AsyncMethod
from libs.crypto.hash.md5Hash import MD5
from libs.tools import mkdirs as iptvtools_mkdirs, \
                      checkIconName, \
                      removeAllIconsFromPath, \
                      getModifyDeltaDateInDays, \
                      FreeSpace as iptvtools_FreeSpace
###################################################
# FOREIGN import
###################################################
import urllib2, threading
from binascii import hexlify
from os import path as os_path, listdir, remove as removeFile
from Components.config import config

class IconManager:
    DOWNLOADED_IMAGE_PATH = "/tmp/BoardsReaderCache/"

    def __init__(self, updateFun = None, downloadNew = True):
        # download queue
        self.queueDQ = []
        self.lockDQ = threading.Lock()
        self.workThread = None
        
        # already available
        self.queueAA = []
        self.lockAA = threading.Lock()
        
        #this function will be called after a new icon will be available
        self.updateFun = updateFun
        
        if not os_path.exists(self.DOWNLOADED_IMAGE_PATH):
            iptvtools_mkdirs(self.DOWNLOADED_IMAGE_PATH)
        
        #load available icon from disk
        self.loadHistoryFromDisk()
        
        self.stopThread = False
        
        self.checkSpace = 0 # if 0 the left space on disk will be checked
        self.downloadNew = downloadNew
        
        pass
        
    def __del__(self):
        self.clearDQueue()
        self.clearAAueue()
        removeAllIconsFromPath(self.DOWNLOADED_IMAGE_PATH)
        
    def stopWorkThread(self):
        self.lockDQ.acquire()
        
        if self.workThread != None and self.workThread.Thread.isAlive():
            self.stopThread = True
        
        self.lockDQ.release()
        
    def runWorkThread(self):
        if self.workThread == None or not self.workThread.Thread.isAlive():
            self.workThread = AsyncMethod(self.processDQ)()
        
    def clearDQueue(self):
        self.lockDQ.acquire()
        self.queueDQ = []
        self.lockDQ.release()
        
    def addToDQueue(self, addQueue=[]):
        self.lockDQ.acquire()
        self.queueDQ.extend(addQueue)
        #self.queueDQ.append(addQueue)
        self.runWorkThread()
        self.lockDQ.release()
        
    ###############################################################
    #                                AA queue
    ###############################################################
    def loadHistoryFromDisk(self):
        path = self.DOWNLOADED_IMAGE_PATH + "/"
        removeAllIconsFromPath(path)
        
        list = listdir(path)
        for item in list:
            if checkIconName(item):
                filePath = path + item
                if delta > 0 and delta <= getModifyDeltaDateInDays(filePath):
                    try:
                        removeFile(filePath)
                    except:
                        print("ERROR: while removing file %s" % filePath)
                else:
                    self.queueAA.append(item)

    def addItemToAAueue(self, item):
        self.lockAA.acquire()
        self.queueAA.append(item)
        self.lockAA.release()
        
    def clearAAueue(self):
        self.lockAA.acquire()
        self.queueAA = []
        self.lockAA.release()
        
    def isItemInAAueue(self, item, hashed = 0):
        if hashed == 0:
            hashAlg = MD5()
            name = hashAlg(item)
            file = hexlify(name) + '.jpg'
        else:
            file = item
        
        ret = False
        #without locking. Is it safety?
        #self.lockAA.acquire()
        if file in self.queueAA:
            ret = True
        #self.lockAA.release()
        
        return ret
       
    def getIconPathFromAAueue(self, item):
        hashAlg = MD5()
        name = hashAlg(item)
        filename = hexlify(name) + '.jpg'
        
        if self.isItemInAAueue(filename, 1):
            path = self.DOWNLOADED_IMAGE_PATH + "/"
            file_path = "%s%s" % (path, filename)
            return file_path
        else:
            return ''
        
    def processDQ(self):
        print "processDQ: Thread started"
        
        while 1:
            die = 0
            url = ''
            
            #getFirstFromDQueue
            self.lockDQ.acquire()
            
            if False == self.stopThread:
                if len(self.queueDQ):
                    url = self.queueDQ.pop(0)
                else:
                    self.workThread = None
                    die = 1
            else:
                self.stopThread = False
                self.workThread = None
                die = 1
            
            self.lockDQ.release()
            
            if die:
                return
            
            print "processDQ url: [%s]" % url
            if url != '':
                hashAlg = MD5()
                name = hashAlg(url)
                file = hexlify(name) + '.jpg'
                
                
                #check if this image is not already available in cache AA list
                if self.isItemInAAueue(file, 1):
                    continue
                else:
                    #check if this image is not already available in cache on disk
                    #maybe all name of images from  DOWNLOADED_IMAGE_PATH should be read
                    #at start of manager, so checing is not needed
                    #if 0:
                    #    continue
                    pass
                
                if self.download_img(url, file):
                    self.addItemToAAueue(file)
                    if None != self.updateFun:
                        self.updateFun(url)
                    pass
                
                # add to AA list

    def download_img(self, img_url, filename):
        # if at start there was NOT enough space on disk 
        # new icon will not be downloaded
        if False == self.downloadNew:
            return False
    
        if len(self.DOWNLOADED_IMAGE_PATH) < 4:
            print('download_img: wrong path for IPTVCache')
            return False
            
        path = self.DOWNLOADED_IMAGE_PATH + '/'
        
        # if at start there was enough space on disk 
        # we will check if we still have free space 
        if 0 >= self.checkSpace:
            print('download_img: checking space on device')
            if not iptvtools_FreeSpace(path, 10):
                print('download_img: not enough space for new icons, new icons will not be downloaded any more')
                self.downloadNew = False
                return False
            else:
                # for another 50 check again
                self.checkSpace = 50
        else:
            self.checkSpace -= 1
            
        try:
            image_on_web = urllib2.urlopen(img_url)
            if image_on_web.headers.maintype == 'image':
                buf = image_on_web.read()
                
                file_path = "%s%s" % (path, filename)
                print file_path
                downloaded_image = file(file_path, "wb")
                downloaded_image.write(buf)
                downloaded_image.close()
                image_on_web.close()
            else:
                print("download_img not image")
                return False    
        except:
            print("download_img exception")
            return False
        return True
    
    





