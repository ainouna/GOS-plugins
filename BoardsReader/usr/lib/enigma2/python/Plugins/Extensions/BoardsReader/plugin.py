# -*- coding: utf-8 -*-
#
#  BoardsReader 2015 by j00zek 2015
# 

wersja="0.2.0"

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

#import string
from enigma import getDesktop
from Components.config import config, Config
from Screens.MessageBox import MessageBox
from Components.Sources.StaticText import StaticText

try:
    from Components.LanguageGOS import gosgettext as _ 
except:
    from libs.tools import TranslateTXT as _
  
from libs.tools import FreeSpace as iptvtools_FreeSpace, \
                      mkdirs as iptvtools_mkdirs, \
                      GetHostsList

from ConfigMenu import ConfigMenu
from os import path as os_path

####################################################
# Wywołanie wtyczki w roznych miejscach
####################################################
def Plugins(**kwargs):
    list = [PluginDescriptor(name=_("Boards Reader"), where = [PluginDescriptor.WHERE_PLUGINMENU], icon="logo.png", fnc=main)] # always show in plugin menu
    list.append(PluginDescriptor(name=_("Boards Reader"), where = PluginDescriptor.WHERE_MENU, fnc=startBoardsReaderfromMenu))
    if config.plugins.BoardReader.showinextensions.value:
        list.append (PluginDescriptor(name=_("Boards Reader"), where = [PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=main))
    return list

####################################################
# Konfiguracja wtyczki
####################################################
def startBoardsReaderfromMenu(menuid, **kwargs):
    #if menuid == "system":
        #return [(_("Configure Boards Client"), mainSetup, "BoardsReader_config", None)]
    #el
    if menuid == "mainmenu" and config.plugins.BoardReader.showinMainMenu.value == True:
        return [(_("Boards Reader"), main, "BoardsReader_main", None)]
    else:
        return []
    
def mainSetup(session,**kwargs):
    session.open(ConfigMenu) 

####################################################
#                   For BoardsReader components
####################################################
from libs.asynccall import AsyncMethod
from MyList import MyListComponent


#####################################################
#                     For hosts
#####################################################
# interface for hosts
from ihost import IHost, CDisplayListItem, RetHost, CUrlItem
######################################################
from iconmanager import IconManager
from libs.cover import Cover

######################################################
#                   For mainThreadQueue
######################################################
from enigma import eTimer
from libs.asynccall import CFunctionProxyQueue
######################################################
gMainFunctionsQueue = None

def main(session,**kwargs):
    session.open(BoardReaderWidget)

class BoardReaderWidget(Screen):
    Plugin_PATH = resolveFilename(SCOPE_PLUGINS, 'Extensions/BoardsReader/')
    sz_w = getDesktop(0).size().width() - 390
    sz_h = getDesktop(0).size().height() - 195
    print("[BoardReader] desktop size %dx%d wersja[%s]\n" % (sz_w+90, sz_h+100, wersja) )
    if sz_h < 500:
        sz_h += 4
    skin = """
        <screen name="BoardReaderWidget" position="center,center" title="%s %s" size="%d,%d">
         <ePixmap position="5,9" zPosition="4" size="30,30" pixmap="%s/icons/red.png" transparent="1" alphatest="on" />
         <widget render="Label" source="key_red" position="45,9" size="140,27" zPosition="5" valign="center" halign="left" backgroundColor="black" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
         <widget name="headertext" position="5,47" zPosition="1" size="%d,23" font="Regular;20" transparent="1"/>
            <widget name="statustext" position="5,240" zPosition="1" size="%d,90" font="Regular;20" halign="center" valign="center" transparent="0"/>
            <widget name="list" position="5,100" zPosition="2" size="%d,%d" scrollbarMode="showOnDemand" transparent="0"/>
            <widget name="console" position="165,%d" zPosition="1" size="%d,140" font="Regular;20" transparent="1"/>
            <widget name="cover" zPosition="2" position="5,%d" size="122,140" alphatest="blend" />     
            <widget name="playerlogo" zPosition="4" position="%d,20" size="120,40" alphatest="blend" />
            <ePixmap zPosition="4" position="5,%d" size="%d,5" pixmap="%s" transparent="1" />
        </screen>""" %(
            _("BoardsReader v."),
            wersja, # wersja wtyczki
            sz_w, sz_h, # size
            Plugin_PATH,# icons
            sz_w - 135, # size headertext
            sz_w - 100, # size statustext
            sz_w - 10, sz_h - 255, # size list
            sz_h - 95, # position console
            sz_w - 155, # size console
            sz_h - 125, # position cover
            sz_w - 125, # position logo
            sz_h - 130, # position line bottom
            sz_w / 2, # size line bottom
            resolveFilename(SCOPE_PLUGINS, 'Extensions/BoardsReader/icons/line.png'),
            )
   
    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)

        self.session.nav.event.append(self.__event)

        self["key_red"] = StaticText(_("Exit"))

        self["list"] = MyListComponent()
        self["list"].connectSelChanged(self.onSelectionChanged)
        self["statustext"] = Label(_("Downloading list..."))
        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions"],
        {
            "ok": self.ok_pressed,
            "back": self.back_pressed,
            "red": self.red_pressed,
        }, -1)     

        self["headertext"] = Label()
        self["console"] = Label()
        
        self["cover"] = Cover()
        self["cover"].hide()
        
        self["playerlogo"] = Cover()
        
        self.showMessageNoFreeSpaceForIcon = False
        self.iconManager = None
        if not os_path.exists("/tmp/BoardsReaderCache/"):
            iptvtools_mkdirs("/tmp/BoardsReaderCache/")
        if iptvtools_FreeSpace("/tmp/BoardsReaderCache/",10):
            self.iconManager = IconManager(self.checkIconCallBack, True)
        else:
            self.showMessageNoFreeSpaceForIcon = True
            self.iconManager = IconManager(self.checkIconCallBack, False)
  
        self.onClose.append(self.__onClose)
        #self.onLayoutFinish.append(self.selectHost)
        self.onShow.append(self.onStart)
        
        #Defs
        self.searchPattern = ''
        self.searchType = None
        
        self.changeIcon = True
        
        self.started = 0
        self.workThread = None
        
        self.host = None
        self.hostName = ''
        
        self.nextSelIndex = 0
        self.currSelIndex = 0
        
        self.prevSelList = []
        self.categoryList = []
      
        self.currList = []
        self.currSelectedItemName = ""

        self.visible = True
        
    
        #################################################################
        #                      Inits for Proxy Queue
        #################################################################
       
        # register function in main Queue
        global gMainFunctionsQueue
        gMainFunctionsQueue = CFunctionProxyQueue()
        gMainFunctionsQueue.unregisterAllFunctions()
        gMainFunctionsQueue.clearQueue()
            
        gMainFunctionsQueue.registerFunction(self.reloadList)
        gMainFunctionsQueue.registerFunction(self.checkIconCallBack)
        gMainFunctionsQueue.registerFunction(self.updateCover)
        gMainFunctionsQueue.registerFunction(self.displayIcon)
        
        #main Queue
        self.mainTimer = eTimer()
        self.mainTimer.timeout.get().append(self.processProxyQueue)
        # every 100ms Proxy Queue will be checked  
        self.mainTimer.start(100)
        #################################################################
        
    #end def __init__(self, session):
        
    def __del__(self):       
        return
        
    def __onClose(self):
        self.session.nav.event.remove(self.__event)
        
        try:
            if self.mainTimer.Enabled():
                self.mainTimer.stop()
            global gMainFunctionsQueue
            gMainFunctionsQueue.unregisterAllFunctions()
            gMainFunctionsQueue.clearQueue()
            gMainFunctionsQueue = None
        except:
            pass
        return

        
    def processProxyQueue(self):
        global gMainFunctionsQueue
        gMainFunctionsQueue.processQueue()
        
        return
        
        
    def isNotInWorkThread(self):
        return self.workThread == None or not self.workThread.Thread.isAlive()
 
    def red_pressed(self):
        self.close()
        return

    # method called from IconManager when a new icon has been dowlnoaded
    def checkIconCallBack(self, ret):
        print("checkIconCallBack")
 
        # ret - url for icon wich has been dowlnoaded
        global gMainFunctionsQueue
        
        #the proxy Queue will be used to call function from mainThread
        gMainFunctionsQueue.addToQueue("displayIcon", ret)
        return
        
        
    def displayIcon(self, ret = None):
        # check if displays icon is enabled in options
        if None == self.iconManager :
            return
        
        if False == self.changeIcon:
            return
        
        selItem = self.getSelItem()
        # when ret is != None the method is called from IconManager 
        # and in this variable the url for icon which was downloaded 
        # is returned 
        if ret != None and selItem != None:
            # if icon for other than selected item has been downloaded 
            # the displayed icon will not be changed
            if ret != selItem.iconimage:
                return
            
        # Display icon
        if selItem and selItem.iconimage != '' and self.iconManager:
            self["cover"].hide()
            # check if we have this icon and get the path to this icon on disk
            iconPath = self.iconManager.getIconPathFromAAueue(selItem.iconimage)
            print( 'displayIcon -> getIconPathFromAAueue: ' + selItem.iconimage )
            if iconPath != '':
                print( 'updateIcon: ' + iconPath )
                self["cover"].decodeCover(iconPath, self.decodeCoverCallBack, "cover")
                self.changeIcon = False
        else:
            self["cover"].hide()
        return

            
    def decodeCoverCallBack(self, ret):
        print("decodeIconIfNeedeCallBack")
        
        global gMainFunctionsQueue
        #the proxy Queue will be used to call function from mainThread
        gMainFunctionsQueue.addToQueue("updateCover", ret)
        
        return
            
    def updateCover(self, retDict):
        # retDict - return dictionary  {Ident, Pixmap, FileName, Changed}
        print('updateCover')
        if retDict:
            print("updateCover retDict for Ident: %s " % retDict["Ident"])
            if retDict["Changed"]:
                self[retDict["Ident"]].updatePixmap(retDict["Pixmap"], retDict["FileName"])
            else:
                print("updateCover pixel map not changed")
                
            if 'cover' == retDict["Ident"]:
                #check if we have icon for right item on list
                selItem = self.getSelItem()
                if selItem and selItem.iconimage != '':
                    # check if we have this icon and get the path to this icon on disk
                    iconPath = self.iconManager.getIconPathFromAAueue(selItem.iconimage)
                    if iconPath == retDict["FileName"]:
                        # now we are sure that we have right icon, so let show it
                        self[retDict["Ident"]].show()
            else:
                self[retDict["Ident"]].show()
        else:
            print("updateCover retDict empty")
            
        return

                
    def changeBottomPanel(self):
        self.changeIcon = True
        self.displayIcon()
        
        selItem = self.getSelItem()
        if selItem and selItem.description != '':
            data = selItem.description
            sData = data.replace('\n','')
            self["console"].setText(sData)
        else:
            self["console"].setText('')
            
        return
                
    
    def onSelectionChanged(self):
        self.changeBottomPanel()
        
        return

 
    def back_pressed(self):
        try:
            if not self.isNotInWorkThread():
                self.workThread.Thread._Thread__stop()
                self["statustext"].setText(_("Action cancelled!"))
                return
        except:
            return
            
        if self.visible:
                       
            if len(self.prevSelList) > 0:
                self.nextSelIndex = self.prevSelList.pop()
                self.categoryList.pop()
                print( "back_pressed prev sel index %s" % self.nextSelIndex )
                self.requestListFromHost('Previous')
            else:
                #There is no prev categories, so exit
                #self.close()
                self.selectHost()
        else:
            self.showWindow()
            
        return

    def ok_pressed(self):
        if self.visible:
            sel = None
            try:
                sel = self["list"].l.getCurrentSelection()[0]
            except:
                print( "ok_pressed except" )
                self.getRefreshedCurrList()
                return
            if sel is None:
                print( "ok_pressed sel is None" )
                self.getInitialList()
                return
            elif len(self.currList) <= 0:
                print( "ok_pressed list is empty" )
                self.getRefreshedCurrList()
                return
            else:
                print( "ok_pressed selected item: %s" % (sel.name) )
                
                self.currSelectedItemName = sel.name             
                item = self.getSelItem()
                
                #Get current selection
                currSelIndex = self["list"].getCurrentIndex()
                #remember only prev categories
                if item.type == CDisplayListItem.TYPE_CATEGORY:
                        print( "ok_pressed selected TYPE_CATEGORY" )
                        self.currSelIndex = currSelIndex
                        self.requestListFromHost('ForItem', currSelIndex, '')
                if item.type == CDisplayListItem.TYPE_SEARCH:
                        print( "ok_pressed selected TYPE_SEARCH" )
                        self.currSelIndex = currSelIndex
                        self.requestListFromHost('ForSearch', currSelIndex, '')
                elif item.type == CDisplayListItem.TYPE_NEWTHREAD or \
                        item.type == CDisplayListItem.TYPE_OLDTHREAD or \
                        item.type == CDisplayListItem.TYPE_LOCKEDTHREAD or \
                        item.type == CDisplayListItem.TYPE_HOTTHREAD or \
                        item.type == CDisplayListItem.TYPE_NEWHOTTHREAD or \
                        item.type == CDisplayListItem.TYPE_THREAD:

                        print( "ok_pressed selected TYPE_*THREAD" )
                        self.currSelIndex = currSelIndex
                        ThreadContent, mainURL, ThreadURL = self.host.getFullThread(self.currSelIndex)
                        print("ThreadContent:" + ThreadContent)
                        from libs.ThreadView import ThreadView
                        self.session.openWithCallback(self.LeaveThreadView, ThreadView, ThreadContent, mainURL, ThreadURL)
        else:
            self.showWindow()
            
        return
    #end ok_pressed(self):
    
    def LeaveThreadView(self):
        pass
    
    def getSelIndex(self):
        currSelIndex = self["list"].getCurrentIndex()
        return currSelIndex

    def getSelItem(self):
        currSelIndex = self["list"].getCurrentIndex()
        if len(self.currList) <= currSelIndex:
            print( "ERROR: getSelItem there is no item with index: %d, listOfItems.len: %d" % (currSelIndex, len(self.currList)) )
            return
        return self.currList[currSelIndex]
        
    def getSelectedItem(self):
        sel = None
        try:
            sel = self["list"].l.getCurrentSelection()[0]
        except:return None
        return sel
        
    def onStart(self):
        if self.started == 0:
            self.selectHost()
            self.started = 1
        return
        
    def selectHost(self):
    
        self.host = None
        self.hostName = ''
        self.nextSelIndex = 0
        self.prevSelList = []
        self.categoryList = []
        self.currList = []
        self.currSelectedItemName = ""

        options = [] 
        hostsList = GetHostsList()
        for hostName in hostsList:
            hostEnabled  = False
            try:
                exec('if config.plugins.BoardReader.host' + hostName + '.value: hostEnabled = True')
            except:
                hostEnabled = False
            if True == hostEnabled:
                _temp = __import__('forums.forum' + hostName, globals(), locals(), ['gettytul'], -1)
                title = _temp.gettytul()
                picon = self.Plugin_PATH + _temp.getpicon()
                print('host name "%s, title %s, picon %s"' % (hostName,title,picon))
                options.extend(((title, hostName,picon),))
        options.sort()
     
        options.extend(((_("BoardsReader configuration"), "config", self.Plugin_PATH + 'icons/MENU-config.png'),))

        if config.plugins.BoardReader.SelectFromList.value == 'list':
            from libs.listselector import ListSelectorWidget
            self.session.openWithCallback(self.selectHostCallback, ListSelectorWidget, list = options, mytitle = _('BoardsReader v.') + wersja )
        else:
            from libs.piconselector import PiconSelectorWidget
            self.session.openWithCallback(self.selectHostCallback, PiconSelectorWidget, list = options, mytitle = _('BoardsReader v.') + wersja )
        return
    
    def selectHostCallback(self, ret):
        hasIcon = False
        if ret:               
            print("[BoardsReader] Returned host " + ret[1])
            if ret[1] == "config":
                self.session.openWithCallback(self.selectHost, ConfigMenu)
                return
            else:
                self.hostName = ret[1]
                _temp = __import__('forums.forum' + self.hostName, globals(), locals(), ['MyHost'], -1)
                self.host = _temp.MyHost()
                
            if self.showMessageNoFreeSpaceForIcon and hasIcon:
                self.showMessageNoFreeSpaceForIcon = False
                self.session.open(MessageBox, "Brak wolnego miejsca w katalogu /tmp/BoardsReaderCache/. \nNowe ikony nie beda ściągane. \nAby nowe ikony były dostępne wymagane jest 10MB wolnego miejsca.", type = MessageBox.TYPE_INFO, timeout = 10 )
        else:
            self.close()
            return
        
        #############################################
        #            change logo for player
        #############################################
        self["playerlogo"].hide()
        
        hRet= self.host.getLogoPath()
        if hRet.status == RetHost.OK and  len(hRet.value):
            logoPath = hRet.value[0]
                
            if logoPath != '':
                print( 'Logo Path: ' + logoPath )
                self["playerlogo"].decodeCover(logoPath, \
                                               self.decodeCoverCallBack, \
                                               "playerlogo")
        #############################################
        
        # request initial list from host        
        self.getInitialList()
        
        return
        
    #end selectHostCallback(self, ret):

    def is_stream(self, url):
        if url[:7] == 'rtmp://':
            return True
        if url[:7] == 'rtsp://':
            return True
        if url[:6] == 'mms://':
            return True
        elif url[-5:] == '.m3u8':
            return True
        elif url[-7:] == '.stream':
            return True
        else:
            return False

    def requestListFromHost(self, type, currSelIndex = -1, videoUrl = ''):
        
        if self.isNotInWorkThread():
            self["list"].hide()
            
            if type != 'ForVideoLinks' and type != 'ResolveURL':
                #hide bottom panel
                self["cover"].hide()
                self["console"].setText('')
                
            if type == 'ForItem' or type == 'ForSearch':
                self.prevSelList.append(self.currSelIndex)
                if type == 'ForSearch':
                    self.categoryList.append('Wyniki wyszukiwania')
                else:
                    self.categoryList.append(self.currSelectedItemName) 
                #new list, so select first index
                self.nextSelIndex = 0
            
            selItem = None
            if currSelIndex > -1 and len(self.currList) > currSelIndex:
                selItem = self.currList[currSelIndex]
            
            if type == 'Refresh':
                self["statustext"].setText("Odświeżam...............")
                self.workThread = AsyncMethod(self.host.getCurrentList, self.callbackGetList)(1)
            elif type == 'Initial':
                self["statustext"].setText(_("Downloading list..."))
                self.workThread = AsyncMethod(self.host.getInitList, self.callbackGetList)()
            elif type == 'Previous':
                self["statustext"].setText(_("Downloading list..."))
                self.workThread = AsyncMethod(self.host.getPrevList, self.callbackGetList)()
            elif type == 'ForItem':
                self["statustext"].setText(_("Downloading list..."))
                self.workThread = AsyncMethod(self.host.getListForItem, self.callbackGetList)(currSelIndex, 0, selItem)
            elif type == 'ForSearch':
                self["statustext"].setText(_("Searching..."))
                self.workThread = AsyncMethod(self.host.getSearchResults, self.callbackGetList)(currSelIndex, 0, selItem)
            else:
                print( 'requestListFromHost unknown list type: ' + type )
                        
        return
    
    #end requestListFromHost(self, type, currSelIndex = -1, videoUrl = ''):
            
    def callbackGetList(self, ret):
        print( "plugin:callbackGetList" )
        
        global gMainFunctionsQueue
        #the proxy Queue will be used to call function from mainThread
        gMainFunctionsQueue.addToQueue("reloadList", ret)
        
        return

    def reloadList(self, ret):
        print( "plugin:reloadList" )
        
        # ToDo: check ret.status if not OK do something :P
        if ret.status != RetHost.OK:
            print( "++++++++++++++++++++++ callbackRefreshXML ret.status = %s" % ret.status )

        self.currList = ret.value
        
        self["list"].setList([ (x,) for x in self.currList])
        
        
        ####################################################
        #                   iconManager
        ####################################################
        iconList = []
        # fill icon List for icon manager 
        # if an user whant to see icons
        if self.iconManager:
            for it in self.currList:
                if it.iconimage != '':
                    iconList.append(it.iconimage)
        
        if len(iconList):
            # List has been changed so clear old Queue
            self.iconManager.clearDQueue()
            # a new list of icons should be downloaded
            self.iconManager.addToDQueue(iconList)
        #####################################################
        
        
        self["headertext"].setText(self.getCategoryPath())
            
        if len(self.currList) <= 0:
            if ret.message and ret.message != '':
                self["statustext"].setText("%s \n\nNaciśnij OK, aby odświeżyć" % ret.message)
            else:
                self["statustext"].setText("Brak elementów do wyświetlenia.\nNaciśnij OK, aby odświeżyć")
            self["list"].hide()
        else:
            #restor previus selection
            if len(self.currList) > self.nextSelIndex:
                self["list"].moveToIndex(self.nextSelIndex)
            else:
                #selection will not be change so manualy call
                self.changeBottomPanel()
            
            self["statustext"].setText("")            
            self["list"].show()
    #end reloadList(self, ret):
    
    def getCategoryPath(self):
        str = self.hostName
        
        for cat in self.categoryList:
            str += ' > ' + cat
        return str
    
    def getRefreshedCurrList(self):
        self.requestListFromHost('Refresh')
        return
    
    def getInitialList(self):
        self.prevSelList = []
        self.categoryList = []
        self.currList = []
        self.currSelectedItemName = ""
        self["headertext"].setText(self.getCategoryPath())
        
        self.requestListFromHost('Initial')
        return
        

    def hideWindow(self):
        self.visible = False
        self.hide()

    def showWindow(self):
        self.visible = True
        self.show()          

    def Error(self, error = None):
        if error is not None:
            try:
                self["list"].hide()
                self["statustext"].setText(str(error.getErrorMessage()))
            except: pass
        
    def __event(self, ev):
        pass
