# -*- coding: utf-8 -*-
# @j00zek 2014 dla Graterlia
#
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from GOSconsole import GOSconsole
from enigma import ePicLoad, ePoint, getDesktop, eTimer, ePixmap, eEPGCache, eServiceReference, iPlayableService
from os import listdir, system as os_system, popen as os_popen
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Tools.Directories import resolveFilename, pathExists
from Components.LanguageGOS import gosgettext as _

############################################
class Cover2(Pixmap):
    def __init__(self):
        Pixmap.__init__(self)
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.paintIconPixmapCB)
        self.paramsSet = False

    def onShow(self):
        Pixmap.onShow(self)

    def paintIconPixmapCB(self, picInfo=None):
        #t = currentThread()
        ptr = self.picload.getData()
        if ptr != None:
            self.instance.setPixmap(ptr)
            self.show()

    def updateIcon(self, filename):
        #t = currentThread()
        if not self.paramsSet:
            self.picload.setPara((self.instance.size().width(), self.instance.size().height(), 1, 1, False, 1, "#00000000"))
            self.paramsSet = True
        self.picload.startDecode(filename)
############################################

class myMenu(Screen,):
    def __init__(self, session, MenuFolder = "" , MenuFile = '_MenuItems'):
        
        self.myList = []
        self.list = []
        self.myPath = MenuFolder
        self.MenuFile = MenuFile
        self.SkryptOpcji = ""
        self.PIC = ""
        picHeight = 0
        if pathExists("%s/_MenuGenerator.sh" % self.myPath) is True:
            os_system( "%s/_MenuGenerator.sh %s" % (self.myPath, self.myPath) )
        MyTitle = ""
        if pathExists("%s/%s" % (self.myPath,self.MenuFile) ) is True:
            with open ("%s/%s" % (self.myPath,self.MenuFile), "r") as myMenufile:
                for MenuItem in myMenufile:
                    MenuItem = MenuItem.rstrip('\n') 
                    if not MenuItem or MenuItem[0] == '#': #omijamy komentarze
                        continue
                    if MenuItem[0:5] == "MENU|":
                        MyTitle = MenuItem.replace("MENU|","")
                    elif MenuItem[0:4] == "PIC|":
                        if pathExists( MenuItem.replace("PIC|","") ) is True:
                            self.PIC = MenuItem.replace("PIC|","")
                            picHeight = 236
                    elif MenuItem[0:5] == "ITEM|":
                        #teraz nierzemy pod uwage tylko te linie co mają odpowiednią ilość |
                        #print MenuItem
                        skladniki = MenuItem.replace("ITEM|","").split('|')
                        if len(skladniki) != 3:
                            continue
                        (NazwaOpcji, TypOpcji,  self.SkryptOpcji) = skladniki
                        if NazwaOpcji != "":
                            NazwaOpcji = _(NazwaOpcji)
                        self.myList.append( (NazwaOpcji, TypOpcji,  self.SkryptOpcji) )
                        self.list.append( NazwaOpcji )
                myMenufile.close()

        ListWidth = 480
        ListHeight = (len(self.list) + 1) * 22
        if ListHeight + 30 + picHeight > 600:
            ListHeight = 600 - 30 - picHeight
        
        skin  = """<screen name="myMenu" position="center,center" size="%d,%d" title="%s" >\n""" % (ListWidth, ListHeight + 30 + picHeight, _(MyTitle) )
        skin += """<widget name="list" position="0,0" size="%d,%d" scrollbarMode="showOnDemand" />\n""" % (ListWidth, ListHeight + 30)
        skin += """<widget name="cover" zPosition="4" position="0,%d" size="420,236" transparent="1" alphatest="blend" />""" % (ListHeight + 30)
        skin += """</screen>"""

        self["cover"] = Cover2()

        self.skin = skin
        self.session = session
        Screen.__init__(self, session)

        self["list"] = MenuList(self.list)
        
        self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.run, "cancel": self.close}, -1)

        self.onLayoutFinish.append(self.onStart)
        self.visible = True

    def onStart(self):
        self["cover"].hide()
        if self.PIC != "" and pathExists( self.PIC ) is True:
            self["cover"].updateIcon( self.PIC )
            self["cover"].show()
    
    def YESNO(self, decyzja):
        if decyzja is False:
            return
        os_system("%s"  %  self.SkryptOpcji)

    def run(self):
        selecteditem = self["list"].getCurrent()
        if selecteditem is not None:
            for opcja in self.myList:
                if opcja[0] == selecteditem:
                    self.SkryptOpcji = opcja[2]
                    if opcja[1] == "CONSOLE":
                        self.session.openWithCallback(self.endrun ,GOSconsole, title = "%s" % selecteditem, cmdlist = [ ('%s' %  self.SkryptOpcji) ])
                    if opcja[1] == "YESNO":
                        self.session.openWithCallback(self.YESNO ,MessageBox,_("Execute %s?") % selecteditem, MessageBox.TYPE_YESNO)
                        #self.session.openWithCallback(self.endrun ( skrypt =  self.SkryptOpcji ) , GOSconsole, title = "%s" % selecteditem, cmdlist = [ ('%s' %  self.SkryptOpcji) ]  )
                    if opcja[1] == "SILENT":
                        os_system("%s"  %  self.SkryptOpcji)
                        self.endrun()
                    elif opcja[1] == "RUN":
                        os_system("%s"  %  self.SkryptOpcji)
                        self.session.openWithCallback(self.endrun,MessageBox,_("%s executed!") %( selecteditem ), MessageBox.TYPE_INFO, timeout=5)
                    elif opcja[1] == "MSG":
                        msgline = ""
                        popenret = os_popen( self.SkryptOpcji)
                        for readline in popenret.readlines():
                            msgline += readline
                        self.session.openWithCallback(self.endrun,MessageBox, "%s" %( msgline ), MessageBox.TYPE_INFO, timeout=15)
                            

    def endrun(self, ret =0):
        #odświerzamy menu
        os_system( "%s/_MenuGenerator.sh %s" % (self.myPath, self.myPath) )
        self.reloadLIST()
        self.onStart()
        return
        
    def reloadLIST(self):
        #czyścimy listę w ten dziwny sposób, aby GUI działało, bo nie zmienimy objektów ;)
        while len(self.list) > 0:
            del self.myList[-1]
            del self.list[-1]
        if pathExists("%s/%s" % (self.myPath,self.MenuFile)  ) is True:
            self["list"].hide()
            with open ("%s/%s" % (self.myPath,self.MenuFile), "r") as myMenufile:
                for MenuItem in myMenufile:
                    MenuItem = MenuItem.rstrip('\n') 
                    if not MenuItem or MenuItem[0] == '#': #omijamy komentarze
                        continue
                    #interesują nas tylko pozycje menu
                    if MenuItem[0:5] == "ITEM|":
                        #teraz bierzemy pod uwage tylko te linie co mają odpowiednią ilość |
                        #print MenuItem
                        skladniki = MenuItem.replace("ITEM|","").split('|')
                        if len(skladniki) == 3:
                            (NazwaOpcji, TypOpcji, SkryptOpcji) = skladniki
                            if NazwaOpcji != "":
                                NazwaOpcji = _(NazwaOpcji)
                            self.myList.append( (NazwaOpcji, TypOpcji, SkryptOpcji) )
                            self.list.append( NazwaOpcji )
                myMenufile.close()
            myIdx = self["list"].getSelectionIndex()
            if myIdx > len(self.list) -1:
                self["list"].moveToIndex(len(self.list) -1)
            self["list"].show()

