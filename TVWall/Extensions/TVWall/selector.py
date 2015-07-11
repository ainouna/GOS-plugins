# -*- coding: utf-8 -*-
###################################################
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.config import config
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ProgressBar import ProgressBar
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.Renderer.Picon import getPiconName
from enigma import ePicLoad, ePoint, getDesktop, eTimer, ePixmap, eEPGCache, eServiceReference, iPlayableService, eVideoWidget
from os import path as os_path
from Screens.Screen import Screen
from Screens.EpgSelection import EPGSelection
from Screens.EventView import  EventViewEPGSelect
from ServiceReference import ServiceReference
from threading import Thread, currentThread
from time import localtime, time, strftime
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE, pathExists
from Tools.LoadPixmap import LoadPixmap
###################################################
MyPiconsList = []
MyList = []

class FillPiconsList(Thread):
    def __init__(self, session):
        Thread.__init__(self)
        #print"[TVWall]FillPiconsList"
        self.session = session
        #self.list = list

    def run(self):
        global MyPiconsList
        print "[TVWall]FillPiconsList:run"
        for idx in range( 0 , len(MyList) ):
            MyPiconsList.append(LoadPixmap(cached = True, path = getPiconName(MyList[idx][0])))
        print len(MyPiconsList)
        return
        
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
   
    def __init__(self, session, list, CurIdx = 0, sSL = None):
        self.currList = list
        self.currIdx = CurIdx
        self.sServiceList = sSL
        # numbers of items in self.currList
        self.numOfItems = len(self.currList)
        # initiate icons list
        self.pixmapList = []
        #self.LoadPixmapPath = config.plugins.TVWall.PiconsFolder.value

        sz_w = getDesktop(0).size().width() - 10
        sz_h = getDesktop(0).size().height() - 10
        if config.plugins.TVWall.usePIG.value == True:
            try:
                PIG_X = int(config.plugins.TVWall.PIGSize.value.split('x')[0])
                PIG_Y = int(config.plugins.TVWall.PIGSize.value.split('x')[1])
            except:
                pass
        else:
            try:
                PIG_X = int(config.plugins.TVWall.PIGSize.value.split('x')[0])
            except:
                pass
            PIG_Y = 0

        # default image size 220x132
        coverWidth = int(config.plugins.TVWall.IconsSize.value.split('x')[0])
        coverHeight = int(config.plugins.TVWall.IconsSize.value.split('x')[1])
        
        # marker size should be larger than img
        markerWidth = 10 + coverWidth
        markerHeight = 10 + coverHeight
        self.markerPixmap = LoadPixmap(cached = True, path = resolveFilename(SCOPE_PLUGINS, 'Extensions/TVWall/icons/marker%i.png' % coverWidth))
        
        # space/distance between images
        disWidth = markerWidth - coverWidth
        disHeight = markerHeight - coverHeight
        
        # position of first img = 0 + <overscan> + <size PIG> + <space between images>
        offsetCoverX = 30 + PIG_X + disWidth
        offsetCoverY = 30
        
        # position of first marker 
        offsetMarkerX = offsetCoverX - (markerWidth - coverWidth)/2
        offsetMarkerY = offsetCoverY - (markerHeight - coverHeight)/2

        #calculate rows/columns
        numOfCol = int((sz_w - 30 - PIG_X - 30)/markerWidth)
        numOfRow = int((sz_h - 20 - 20)/markerHeight)
        
        #recalculate disWidth and initial position to have picons nicely formatted
        disWidth = int( ((sz_w - 30 - PIG_X - 30) - numOfCol * markerWidth)/numOfCol )
        offsetMarkerX += disWidth
        # how to calculate position of image with indexes indxX, indxY:
        #posX = offsetCoverX + (coverWidth + disWidth) * indxX
        #posY = offsetCoverY + (coverHeight + disHeight) * indxY
        
        # how to calculate position of marker for image with posX, posY
        #markerPosX = posX - (markerWidth - coverWidth)/2
        #markerPosY = posY - (markerHeight - coverHeight)/2
        
        tmpX = coverWidth + disWidth
        tmpY = coverHeight + disHeight
        
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
        skin = """<screen name="SkypeWallWidget" position="center,center" title="" size="%d,%d">\n""" % (sz_w, sz_h) #wielkosc glownego okna
        if config.plugins.TVWall.usePIG.value == True:    
            skin += """<widget source="session.VideoPicture" position="30,30" size="%d,%d" render="Pig" backgroundColor="transparent" zPosition="1" />""" % (PIG_X, PIG_Y) #PIG size
        skin += """
            <widget name="marker"         position="%d,%d" size="%d,%d" zPosition="2" transparent="1" alphatest="blend" />
            <widget name="curChannelName" position="30,%d" size="%d,30" font="Regular;26" halign="center" valign="center" transparent="1" zPosition="1"/>
            <widget name="NowEventTitle"  position="30,%d" size="%d,28" font="Regular;24" halign="center" valign="center" transparent="1" zPosition="2" foregroundColor="#fcc000" />
            <widget name="NowEventStart"  position="30,%d" size="%d,28" font="Regular;24" halign="left"   valign="center" transparent="1" zPosition="2" foregroundColor="#fcc000" />
            <widget name="vzProgress"     position="30,%d" size="%d,3"  transparent="1" zPosition="5" borderColor="#00c1ea02"/>
            <widget name="NowDuration"    position="30,%d" size="%d,28" font="Regular;24" halign="right"  valign="center" transparent="1" zPosition="2" foregroundColor="#fcc000" />
            <widget name="NextEventTitle" position="30,%d" size="%d,28" font="Regular;24" halign="center"   valign="center" transparent="1" zPosition="2"/>
            <widget name="NextEventStart" position="30,%d" size="%d,28" font="Regular;24" halign="left"   valign="center" transparent="1" zPosition="2"/>
            <widget name="NextDuration"   position="30,%d" size="%d,28" font="Regular;24" halign="right"  valign="center" transparent="1" zPosition="2"/>

            
            """  %(
                offsetMarkerX, offsetMarkerY, # first marker position
                markerWidth, markerHeight,    # marker size
                30 + PIG_Y + 10, PIG_X, # widget name="curChannelName"
                30 + PIG_Y + 10 + 40, PIG_X, # widget name="NowEventTitle"
                30 + PIG_Y + 10 + 40 + 30, PIG_X, # widget name="NowEventStart"
                30 + PIG_Y + 10 + 40 + 30 + 30 + 5, PIG_X, # widget name="vzProgress"
                #30 + PIG_Y + 10 + 40 + 30 + 30 + 5, PIG_X, # eLabel
                30 + PIG_Y + 10 + 40 + 30, PIG_X, # widget name="NowDuration"
                30 + PIG_Y + 10 + 40 + 30 + 30 + 5 + 30, PIG_X, # widget name="NextEventTitle"
                30 + PIG_Y + 10 + 40 + 30 + 30 + 5 + 30 + 30, PIG_X, # widget name="NextEventStart"
                30 + PIG_Y + 10 + 40 + 30 + 30 + 5 + 30 + 30, PIG_X, # widget name="NextDuration"
                )
                
        for y in range(1,numOfRow+1):
            for x in range(1,numOfCol+1):
                skinCoverLine = """<widget name="chname_%s%s" position="%d,%d" size="%d,%d" font="Regular;20" halign="center" valign="center" transparent="1"/>""" % (x, y, 
                    (offsetCoverX + tmpX * (x - 1) ), # pos X image
                    (offsetCoverY + tmpY * (y - 1) ), # pos Y image
                    coverWidth, 
                    coverHeight
                )
                skin += '\n' + skinCoverLine
            for x in range(1,numOfCol+1):
                skinCoverLine = """<widget name="cover_%s%s" zPosition="4" position="%d,%d" size="%d,%d" transparent="1" alphatest="blend" />""" % (x, y, 
                    (offsetCoverX + tmpX * (x - 1) ), # pos X image
                    (offsetCoverY + tmpY * (y - 1) ), # pos Y image
                    coverWidth, 
                    coverHeight
                )
                skin += '\n' + skinCoverLine
        skin += '</screen>'
                
        self.skin = skin
            
        self.session = session
        Screen.__init__(self, session)
        
        self.session.nav.event.append(self.__event)
        
        if list == None or len(list) <= 0:
            self.close(None)
            
        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions", "ChannelSelectEPGActions"],
        {
            "ok": self.ok_pressed,
            "back": self.back_pressed,
            "left": self.keyLeft,
            "right": self.keyRight,
            "up": self.keyUp,
            "down": self.keyDown,
            "showEPGList": self.openSingleServiceEPG,
        }, -1)
        
        self["curChannelName"] = Label(self.currList[CurIdx][1])
        self["marker"] = Cover3()

        self["NowEventStart"] = Label()
        self["NextEventStart"] = Label()
        self["NowEventEnd"] = Label()
        self["NextEventEnd"] = Label()
        self["NowEventTitle"] = Label()
        self["NextEventTitle"] = Label()
        self["NowDuration"] = Label()
        self["NextDuration"] = Label()
        self["NowDescription"] = Label()
        self["NextDescription"] = Label()
        self["vzProgress"] = ProgressBar()
        
        chnameidx = -1
        #Preparing picons & channel names
        for y in range(1,self.numOfRow+1):
            for x in range(1,self.numOfCol+1):
                chnameidx += 1
                #name, in case of no picon
                chnameIndex = "chname_%s%s" % (x,y)
                self[chnameIndex] = Label(self.currList[chnameidx][1])
                #picons
                strIndex = "cover_%s%s" % (x,y)
                if config.plugins.TVWall.ScaleIcons.value == False:
                    self[strIndex] = Cover3()
                else:
                    self[strIndex] = Cover2()

        self.epgcache = eEPGCache.getInstance()
                
        self.zap = False
        if config.plugins.TVWall.ZapMode.value == "2ok":
            self.zap = True
            self.__event_tracker = ServiceEventTracker(screen=self,eventmap={
                iPlayableService.evStart: self.__evStart,
                iPlayableService.evVideoSizeChanged: self.__evVideoSizeChanged,
                iPlayableService.evEnd: self.__serviceStopped,
                iPlayableService.evStopped: self.__evStopped,
                })     

        self.onLayoutFinish.append(self.onStart)
        self.visible = True
        self.FillPicons = True
        
        self.dst_left = '0'
        self.dst_top = '0'
        self.dst_width = '2d0'
        self.dst_height = '240'
#######################################################################################################################
    def onStart(self):
        #global MyPiconsList
        #if len(MyPiconsList) != self.numOfItems:
        global MyList
        MyList = self.currList
        #self.Timer = eTimer()
        #self.Timer.callback.append(self.startfillpixmapListThread)
        #self.Timer.start(100, 1)
        self["marker"].setPixmap( self.markerPixmap )
        self.calcMarkerPosY()
        self.calcMarkerPosX()
        self.updateIcons()
        self.moveMarker()
        return
        
    def startfillpixmapListThread(self):
        piconsThread = Thread( target = self.fillpixmapList )
        piconsThread.start()

    def fillpixmapList(self):
        for idx in range(0,self.numOfItems):
            self.pixmapList.append(LoadPixmap(getPiconName(self.currList[idx][0])))
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
#######################################################################################################################################        
    def updateIcons(self):
        pageidx = self.currPage * (self.numOfCol*self.numOfRow)
        idx = 0
        for y in range(1,self.numOfRow+1):
            for x in range(1,self.numOfCol+1):
                chnameIndex = "chname_%s%s" % (x,y)
                strIndex = "cover_%s%s" % (x,y)
                if pageidx + idx < self.numOfItems:
                    PiconPath = getPiconName(self.currList[pageidx+idx][0])
                    print("updateIcon for self[%s], channel %s, picon %s" % (strIndex, self.currList[pageidx+idx][1],PiconPath))
                    if config.plugins.TVWall.PreloadPicons.value == True:
                        try:
                            self[strIndex].setPixmap(MyPiconsList[pageidx + idx])
                        except:
                            print "[TVWall]updateIcons:exception"
                            self[strIndex].setPixmap(LoadPixmap(cached = True, path = PiconPath))
                    else:
                        self[strIndex].setPixmap(LoadPixmap(cached = True, path = PiconPath))
                    #if icon available, don't display channel name
                    if os_path.exists(PiconPath) and not PiconPath.endswith("picon_default.png"):
                        self[strIndex].show()
                        self[chnameIndex].setText("")
                    else:
                        print "picon for %s not exists" % self.currList[pageidx+idx][1]
                        self[strIndex].hide()
                        self[chnameIndex].setText(self.currList[pageidx+idx][1])
                    idx += 1
                else:
                    self[strIndex].hide()
                    self[chnameIndex].setText("")
    
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
        self["curChannelName"].setText(self.currList[idx][1])
        
        current = ServiceReference(self.currList[idx][0])
        nowepg, nowstart, nowend, nowname, nowduration, nowdesc, percentnow = self.getEPGNowNext(current.ref,0)
        nextepg, nextstart, nextend, nextname, nextduration, nextdesc, percentnext = self.getEPGNowNext(current.ref,1)
        self["NowEventStart"].setText(nowstart)
        self["NextEventStart"].setText(nextstart)
        self["NowEventEnd"].setText(nowend)
        self["NextEventEnd"].setText(nextend)
        self["NowEventTitle"].setText(nowname)
        self["NextEventTitle"].setText(nextname)
        self["NowDuration"].setText(nowduration)
        self["NextDuration"].setText(nextduration)
        self["NowDescription"].setText(nowdesc)
        self["NextDescription"].setText(nextdesc)
        self["vzProgress"].setValue(percentnow)
        if config.plugins.TVWall.ZapMode.value == "2ok": self.zap = True
        return

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
        
    def getEPGNowNext(self, ref, modus):
        # get now || next event
        if self.epgcache is not None:
            event = self.epgcache.lookupEvent(['IBDCTE', (ref.toString(), modus, -1)])
            if event:
                if event[0][4]:
                    t = localtime(event[0][1])
                    begin = event[0][1]
                    duration = event[0][2]
                    now = int(time())
                    if modus == 0:
                        eventduration =_("+%d min") % (((event[0][1] + duration) - time()) / 60)
                        percent = int((now - begin) * 100 / duration)
                        eventname = event[0][4]
                        eventstart = strftime("%H:%M", localtime(begin))
                        eventend = strftime("%H:%M", localtime(begin + duration))
                        eventtimename = ("%02d:%02d   %s") % (t[3],t[4], event[0][4])
                        eventdesc = event[0][5]
                    elif modus == 1:
                        eventduration =_("%d min") % (duration / 60)
                        percent = 0
                        eventname = event[0][4]
                        eventstart = strftime("%H:%M", localtime(begin))
                        eventend = strftime("%H:%M", localtime(begin + duration))
                        eventtimename = ("%02d:%02d   %s") % (t[3],t[4], event[0][4])
                        eventdesc = event[0][5]
                    return eventtimename, eventstart, eventend, eventname, eventduration, eventdesc, percent
                else:
                    return _("No EPG data"), "", "", _("No EPG data"), "", "", ""
        return _("No EPG data"), "", "", _("No EPG data"), "", "", ""

    def openSingleServiceEPG(self):
        # show EPGList
        idx = self.currLine * self.numOfCol +  self.dispX
        current = ServiceReference(self.currList[idx][0])
        service = eServiceReference(self.currList[idx][0])
        self.sServiceList.setCurrentSelection(service)
        self.session.open(EPGSelection, current.ref)
        
    def openEventView(self):
        # stop exitTimer
        # if self.exitTimer.isActive():
        #    self.exitTimer.stop()
        # show EPG Event
        idx = self.currLine * self.numOfCol +  self.dispX
        epglist = [ ]
        self.epglist = epglist
        service = ServiceReference(self.currList[idx][0])
        ref = service.ref
        evt = self.epgcache.lookupEventTime(ref, -1)
        if evt:
            epglist.append(evt)
        evt = self.epgcache.lookupEventTime(ref, -1, 1)
        if evt:
            epglist.append(evt)
        if epglist:
            self.session.openWithCallback(self.EventViewEPGSelectCallBack, EventViewEPGSelect, epglist[0], service, self.eventViewCallback, self.openSingleServiceEPG, self.openSimilarList)

    def EventViewEPGSelectCallBack(self):
        # if enabled, start ExitTimer
        # self.resetExitTimer()
        pass

    def eventViewCallback(self, setEvent, setService, val):
        epglist = self.epglist
        if len(epglist) > 1:
            tmp = epglist[0]
            epglist[0] = epglist[1]
            epglist[1] = tmp
            setEvent(epglist[0])

    def openSimilarList(self, eventid, refstr):
        self.session.open(EPGSelection, refstr, None, eventid)
        
    def __evStopped(self):
        self.dst_left = open("/proc/stb/vmpeg/0/dst_left").readline().strip()
        self.dst_top = open("/proc/stb/vmpeg/0/dst_top").readline().strip()
        self.dst_width = open("/proc/stb/vmpeg/0/dst_width").readline().strip()
        self.dst_height = open("/proc/stb/vmpeg/0/dst_height").readline().strip()
        print('[TV Wall] __evStopped, sizes: %s,%s,%s,%s' % (self.dst_left,self.dst_top,self.dst_width,self.dst_height) )

    def __serviceStopped(self):
        print "[TV Wall] __serviceStopped"

    def __evVideoSizeChanged(self):
        print "[TV Wall] __evVideoSizeChanged"
    
    def __evStart(self, vsX = '12', vsY= '1c', vsW='ea', vsH='c1'):
        if self.FillPicons == True and config.plugins.TVWall.PreloadPicons.value == True:
            self.FillPicons = False
            piconsThread = FillPiconsList(self.session)
            piconsThread.start()

        print('[TV Wall] __evUpdatedInfo: echo "%s,%s,%s,%s">/proc/stb/vmpeg/0/dst_all' % (self.dst_left,self.dst_top,self.dst_width,self.dst_height) )
        with open('/proc/stb/vmpeg/0/dst_all', "w") as f: f.write("%s %s %s %s\n" % (self.dst_left,self.dst_top,self.dst_width,self.dst_height))
    
    def ok_pressed(self):
        idx = self.currLine * self.numOfCol +  self.dispX
        if idx < self.numOfItems:
            print "[TVWall:selector:ok_pressed] selected " + str(self.currList[idx][0])
            if self.zap == True and idx != self.currIdx:
                print("[TVWall] preview host %s" % self.currList[idx][1] )
                service = eServiceReference(self.currList[idx][0])
                self.sServiceList.setCurrentSelection(service) #wybieramy serwis na liscie
                self.sServiceList.zap(enable_pipzap = True) # i przelaczamy 
                self.zap = False
                self.currIdx = idx
            else:
                self.close(self.currList[idx])
        else:
            self.close(None)
        return
