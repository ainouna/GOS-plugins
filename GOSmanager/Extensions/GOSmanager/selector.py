# -*- coding: utf-8 -*-
#
#  GOS Selector
#
###################################################
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.config import config
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ProgressBar import ProgressBar
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from enigma import ePicLoad, ePoint, getDesktop, eTimer, ePixmap, eEPGCache, eServiceReference, iPlayableService
from Screens.Screen import Screen
from ServiceReference import ServiceReference
from threading import Thread, currentThread
from thread import start_new_thread, allocate_lock
from time import localtime, time, strftime
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE, pathExists
from Tools.LoadPixmap import LoadPixmap
from Components.LanguageGOS import gosgettext as _
###################################################

class Cover2(Pixmap):
    def __init__(self):
        Pixmap.__init__(self)
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.paintIconPixmapCB)
        self.paramsSet = False

    def onShow(self):
        Pixmap.onShow(self)

    def paintIconPixmapCB(self, picInfo=None):
        t = currentThread()
        ptr = self.picload.getData()
        if ptr != None:
            self.instance.setPixmap(ptr)
            self.show()

    def updateIcon(self, filename):
        t = currentThread()
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
        
class SelectorWidget(Screen):
    def __init__(self, session, list, CurIdx = 0, Mytitle = _("SelectItem") ):
        self.currList = list
        self.currIdx = CurIdx

        # numbers of items in self.currList
        self.numOfItems = len(self.currList)

        # default image size 220x132
        self.coverWidth = 150
        self.coverHeight = 150
        
        # marker size should be larger than img
        self.markerWidth = 30 + self.coverWidth
        self.markerHeight = 30 + self.coverHeight
        self.markerPixmap = LoadPixmap(resolveFilename(SCOPE_PLUGINS, 'Extensions/GOSmanager/icons/marker.png'))
        
        # space/distance between images
        #self.disWidth  = self.markerWidth - self.coverWidth + 5
        #self.disHeight = self.markerHeight - self.coverHeight + 5
        self.disWidth  = 20
        self.disHeight = 20
        
        # rows & columns calculation
        self.numOfCol = 0
        self.numOfRow = 0
        
        # position of first cover
        self.offsetCoverX = 20
        self.offsetCoverY  = 20

        if self.numOfItems > 12:
            self.numOfCol = 5
            self.numOfRow = 3
        elif self.numOfItems > 9:
            self.numOfCol = 4
            self.numOfRow = 3
        elif self.numOfItems > 6:
            self.numOfCol = 3
            self.numOfRow = 3
        elif self.numOfItems > 4:
            self.numOfCol = 3
            self.numOfRow = 2
        elif self.numOfItems == 3:
            self.numOfCol = 3
            self.numOfRow = 1
        elif self.numOfItems == 2:
            self.numOfCol = 2
            self.numOfRow = 1
        else:
            self.numOfCol = 2
            self.numOfRow = 2
            
        sz_w = self.numOfCol * ( self.coverWidth + self.disWidth  ) + self.offsetCoverX
        sz_h = self.numOfRow * ( self.coverHeight + self.disHeight ) + self.offsetCoverY 
        
        # position of first marker 
        offsetMarkerX = self.offsetCoverX - (self.markerWidth - self.coverWidth)/2
        offsetMarkerY = self.offsetCoverY  - (self.markerHeight - self.coverHeight)/2

        #calculate rows/columns
        
        # how to calculate position of image with indexes indxX, indxY:
        #posX = offsetCoverX + (self.coverWidth + self.disWidth ) * indxX
        #posY = offsetCoverY + (self.coverHeight + self.disHeight) * indxY
        
        # how to calculate position of marker for image with posX, posY
        #markerPosX = posX - (self.markerWidth - self.coverWidth)/2
        #markerPosY = posY - (self.markerHeight - self.coverHeight)/2
        
        tmpX = self.coverWidth + self.disWidth 
        tmpY = self.coverHeight + self.disHeight
        
        # numbers of lines
        self.numOfLines = self.numOfItems / self.numOfCol
        if self.numOfItems % self.numOfCol > 0:
            self.numOfLines += 1

        # numbers of pages
        self.numOfPages = self.numOfLines / self.numOfRow
        if self.numOfLines % self.numOfRow > 0:
            self.numOfPages += 1

        self.currPage = int(CurIdx /(self.numOfCol*self.numOfRow)) #idx=self.currPage * (self.numOfCol*self.numOfRow)
        self.currLine = int(CurIdx / self.numOfCol)

        self.dispX = CurIdx - self.currLine * self.numOfCol
        self.dispY = self.currLine - self.currPage * self.numOfRow
        
#            <eLabel                       position="30,%d" size="%d,3"                zPosition="4" backgroundColor="#f4f4f4"/>
        skin = """<screen name="SelectorWidget" position="center,center" title="%s" size="%d,%d">\n""" % (Mytitle, sz_w, sz_h + 24) #wielkosc glownego okna
        skin += """<widget name="marker"           position="%d,%d" size="%d,%d" zPosition="2" transparent="1" alphatest="blend" />\n""" % (
                offsetMarkerX, offsetMarkerY, # first marker position
                self.markerWidth, self.markerHeight,    # marker size
                )
        skin += """<widget name="SelectedItemDescr" position="0,%d" size="%d,22" font="Regular;20" halign="center" valign="center" transparent="1" zPosition="1"/>\n""" % (
                sz_h , sz_w) 
                
        for y in range(1,self.numOfRow+1):
            for x in range(1,self.numOfCol+1):
                skinCoverLine = """<widget name="cover_%s%s" zPosition="4" position="%d,%d" size="%d,%d" transparent="1" alphatest="blend" />""" % (x, y, 
                    (self.offsetCoverX + tmpX * (x - 1) ), # pos X image
                    (self.offsetCoverY + tmpY * (y - 1) ), # pos Y image
                    self.coverWidth, 
                    self.coverHeight
                )
                skin += '\n' + skinCoverLine
        skin += '</screen>'
                
        self.skin = skin
            
        self.session = session
        Screen.__init__(self, session)
        
        self.session.nav.event.append(self.__event)
        
        if list == None or len(list) <= 0:
            self.close(None)
            
        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions"],
        {
            "ok": self.ok_pressed,
            "back": self.back_pressed,
            "left": self.keyLeft,
            "right": self.keyRight,
            "up": self.keyUp,
            "down": self.keyDown,
        }, -1)
        
        self["SelectedItemDescr"] = Label(_(self.currList[CurIdx][0]))
        self["marker"] = Cover3()

        chnameidx = -1
        for y in range(1,self.numOfRow+1):
            for x in range(1,self.numOfCol+1):
                chnameidx += 1
                #picons
                strIndex = "cover_%s%s" % (x,y)
                self[strIndex] = Cover2()

        self.onLayoutFinish.append(self.onStart)
        self.visible = True
           
#######################################################################################################################
    def onStart(self):
        self["marker"].setPixmap( self.markerPixmap )
        self.calcMarkerPosY()
        self.calcMarkerPosX()
        self.updateIcons()
        self.moveMarker()
        return
        
#######################################################################################################################
    #Calculate marker position Y
    def calcMarkerPosY(self):
        
        if self.currLine >  (self.numOfLines - 1):
            self.currLine = 0
        elif self.currLine < 0:
            self.currLine = (self.numOfLines - 1)
        
        # calculate new page number 
        newPage = self.currLine / self.numOfRow
        if newPage != self.currPage:
            self.currPage = newPage
            self.updateIcons()
        
        # calculate dispY pos 
        self.dispY = self.currLine - self.currPage * self.numOfRow 
        
        # if we are in last line dispX pos 
        # must be also corrected
        if self.currLine ==  (self.numOfLines - 1):
            self.numItemsInLine = self.numOfItems - ((self.numOfLines - 1) * self.numOfCol) 
            if self.dispX > (self.numItemsInLine - 1):
                self.dispX = self.numItemsInLine - 1
            
        return
        

#######################################################################################################################
    #Calculate marker position X
    def calcMarkerPosX(self):
        if self.currLine == self.numOfLines - 1:
            #calculate num of item in last line
            self.numItemsInLine = self.numOfItems - ((self.numOfLines - 1) * self.numOfCol) 
        else:
            self.numItemsInLine = self.numOfCol

        if self.dispX > (self.numItemsInLine - 1):
            self.dispX = 0
        elif self.dispX < 0:
            self.dispX = self.numItemsInLine - 1

        return
        
#######################################################################################################################
    def updateIcons(self):
        pageidx = self.currPage * (self.numOfCol*self.numOfRow)
        idx = 0
        for y in range(1,self.numOfRow+1):
            for x in range(1,self.numOfCol+1):
                strIndex = "cover_%s%s" % (x,y)
                #print("updateIcon for self[%s]" % strIndex)
                if pageidx + idx < self.numOfItems:
                    self[strIndex].updateIcon( self.currList[idx][1] )
                    self[strIndex].show()
                    idx += 1
                else:
                    self[strIndex].hide()
    
    def moveMarker(self):

        # calculate position of image
        imgPosX = self.offsetCoverX + (self.coverWidth + self.disWidth) * self.dispX
        imgPosY = self.offsetCoverY + (self.coverHeight + self.disHeight) * self.dispY

        # calculate postion of marker for current image
        x = imgPosX - (self.markerWidth - self.coverWidth)/2
        y = imgPosY - (self.markerHeight - self.coverHeight)/2
        
        #x =  30 + self.dispX * 180
        #y = 130 + self.dispY * 125
        self["marker"].instance.move(ePoint(x,y))
        
        idx = self.currLine * self.numOfCol +  self.dispX
        self["SelectedItemDescr"].setText(_(self.currList[idx][0]))
        
        return

#######################################################################################################################
    def back_pressed(self):
        self.close(None)
        return
    
    def hideWindow(self):
        self.visible = False
        self.hide()

    def showWindow(self):
        self.visible = True
        self.show()

    def Error(self, error = None):
        pass
        
    def __event(self, ev):
        pass
        
    def ok_pressed(self):
        idx = self.currLine * self.numOfCol +  self.dispX
        if idx < self.numOfItems:
            #print "[GOSmanager:selector:ok_pressed] selected " + str(self.currList[idx][0])
            self.close(self.currList[idx])
        else:
            self.close(None)
        return

    def __del__(self):       
        return
        
    def __onClose(self):
        return
        
    def keyRight(self):
        self.dispX += 1
        self.calcMarkerPosX()
        self.moveMarker()
        return
    def keyLeft(self):
        self.dispX -= 1
        self.calcMarkerPosX()
        self.moveMarker()
        return

    def keyDown(self):
        self.currLine += 1
        self.calcMarkerPosY()
        self.moveMarker()
        return
    def keyUp(self):
        self.currLine -= 1
        self.calcMarkerPosY()
        self.moveMarker()
        return
    
