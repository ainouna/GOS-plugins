# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Components.ActionMap import ActionMap, HelpableActionMap
from enigma import ePoint
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap
from Components.Label import Label
from Components.config import config
from Components.Pixmap import Pixmap

class Cover3(Pixmap):
    def __init__(self):
        Pixmap.__init__(self)
        
    def onShow(self):
        Pixmap.onShow(self)

    def setPixmap(self, ptr):
        self.instance.setPixmap(ptr)
        
class PiconSelectorWidget(Screen):
   
    def __init__(self, session, list, mytitle = 'PiconSelectorWidget' ):
        #print("PlayerSelectorWidget length of list: %i" % len(list))
        numOfRow = 1
        numOfCol = 3
        
        # position of first img
        offsetCoverX = 25
        offsetCoverY = 80
        
        # image size
        coverWidth = 100
        coverHeight = 100
        
        # space/distance between images
        disWidth = int(coverWidth / 3 )
        disHeight = int(coverHeight / 4)
        
        # marker size should be larger than img
        markerWidth = 45 + coverWidth
        markerHeight = 45 + coverHeight
        
        # position of first marker 
        offsetMarkerX = offsetCoverX - (markerWidth - coverWidth)/2
        offsetMarkerY = offsetCoverY - (markerHeight - coverHeight)/2
        
        tmpX = coverWidth + disWidth
        tmpY = coverHeight + disHeight
        
        skin = """
<screen name="PiconSelectorWidgetScreen" position="center,center" title="PiconSelectorWidget" size="416,205">
    <widget name="statustext" position="10,0" zPosition="1" size="429,70" font="Regular;26" halign="center" valign="center" transparent="1"/>
    <widget name="marker" zPosition="2" position="3,58" size="145,145" transparent="1" alphatest="on" />
	<widget name="cover_11" zPosition="4" position="25,80" size="100,100" transparent="1" alphatest="on" />
	<widget name="cover_21" zPosition="4" position="158,80" size="100,100" transparent="1" alphatest="on" />
	<widget name="cover_31" zPosition="4" position="291,80" size="100,100" transparent="1" alphatest="on" />
</screen>
            """
        
        self.skin = skin
            
        self.session = session
        Screen.__init__(self, session)
        
        self.session.nav.event.append(self.__event)
        
        if list == None or len(list) <= 0:
            self.close(None)
            
        self.currList = list
        self.title = mytitle
        # numbers of items in self.currList
        self.numOfItems = len(self.currList)
        self.IconsSize = 100
        self.MarkerSize = self.IconsSize + 45
        
        # load icons
        self.pixmapList = []
        for idx in range(0,self.numOfItems):
            self.pixmapList.append( LoadPixmap(self.currList[idx][2]) )

        self.markerPixmap = LoadPixmap(resolveFilename(SCOPE_PLUGINS, 'Extensions/BoardsReader/icons/MENU-marker.png'))
        
        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions"],
        {
            "ok": self.ok_pressed,
            "back": self.back_pressed,
            "left": self.keyLeft,
            "right": self.keyRight,
            "up": self.keyUp,
            "down": self.keyDown,
        }, -1)
        
        self.numOfRow = numOfRow
        self.numOfCol = numOfCol
        # position of first cover
        self.offsetCoverX = offsetCoverX
        self.offsetCoverY = offsetCoverY
        # space/distance between images
        self.disWidth = disWidth
        self.disHeight = disHeight
        # image size
        self.coverWidth = coverWidth
        self.coverHeight = coverHeight
        # marker size should be larger than img
        self.markerWidth = markerWidth
        self.markerHeight = markerHeight

        self["marker"] = Cover3()
        
        for y in range(1,self.numOfRow+1):
            for x in range(1,self.numOfCol+1):
                strIndex = "cover_%s%s" % (x,y)
                self[strIndex] = Cover3()
                
        self["statustext"] = Label(self.currList[0][0])

        # numbers of lines
        self.numOfLines = self.numOfItems / self.numOfCol
        if self.numOfItems % self.numOfCol > 0:
            self.numOfLines += 1

        # numbers of pages
        self.numOfPages = self.numOfLines / self.numOfRow
        if self.numOfLines % self.numOfRow > 0:
            self.numOfPages += 1

        self.currPage = 0
        self.currLine = 0

        self.dispX = 0
        self.dispY = 0
    
        self.onLayoutFinish.append(self.onStart)
        self.visible = True
        
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
        
    def onStart(self):
        self.setTitle(_(self.title))
        self["marker"].setPixmap( self.markerPixmap )
        self.updateIcons()
        return
        
    def updateIcons(self):
        idx = self.currPage * (self.numOfCol*self.numOfRow)
        for y in range(1,self.numOfRow+1):
            for x in range(1,self.numOfCol+1):
                strIndex = "cover_%s%s" % (x,y)
                print("updateIcon for self[%s]" % strIndex)
                if idx < self.numOfItems:
                    #self[strIndex].updateIcon( resolveFilename(SCOPE_PLUGINS, 'Extensions/BoardsReader/icons/PlayerSelector/' + self.currList[idx][1] + '.png'))
                    self[strIndex].setPixmap(self.pixmapList[idx])
                    self[strIndex].show()
                    idx += 1
                else:
                    self[strIndex].hide()
                    
    
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
        self["statustext"].setText(self.currList[idx][0])
        return

    def back_pressed(self):
        self.close(None)
        return

    def ok_pressed(self):
        idx = self.currLine * self.numOfCol +  self.dispX
        if idx < self.numOfItems:
            print "selected" + str(self.currList[idx][1])
            self.close(self.currList[idx])
        else:
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