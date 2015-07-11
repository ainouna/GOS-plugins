# -*- coding: utf-8 -*-
#
#  TVWall by j00zek @2015
# 
###################################################
# Import lokalnych skryptow
###################################################
from Components.LanguageGOS import gosgettext as _
from selector import SelectorWidget #wybor kanalu po nazwie
###################################################
# Import niezbednych skryptow
###################################################
from Components.config import config
from ConfigMenu import ConfigMenu
from Screens.Screen import Screen
from enigma import eServiceCenter, eServiceReference, iServiceInformation, getDesktop
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from ServiceReference import ServiceReference
####################################################
# Wywołanie wtyczki w roznych miejscach
####################################################
from Plugins.Plugin import PluginDescriptor

def Plugins(**kwargs):
    list = [PluginDescriptor(name="TVWall", description=_("Emulates wall option introduced in Spark fw"), where = [PluginDescriptor.WHERE_PLUGINMENU], icon="icons/logo.png", fnc=main)] # always show in plugin menu
    list.append(PluginDescriptor(name="TVWall", description=_("Emulates wall option introduced in Spark fw"), where = PluginDescriptor.WHERE_MENU, fnc=startTVWallfromMenu))
    if config.plugins.TVWall.showinextensions.value:
        list.append (PluginDescriptor(name=_("TVWall"), description=_("Emulates wall option introduced in Spark fw"), where = [PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=main))
    return list

####################################################
# Uruchomienie wtyczki z Menu
####################################################
def startTVWallfromMenu(menuid, **kwargs):
    if menuid == "mainmenu" and config.plugins.TVWall.showinMainMenu.value == True:
        return [(_("TVWall"), main, "TVWall_main", None)]
    elif menuid != "system":
        return [ ]
    else:
        return [(_("TVWall config"), mainSetup, "TVWallconfig", None)]
    
def mainSetup(session,**kwargs):
    session.open(ConfigMenu) 
######################################################
# Kod glowny wtyczki
####################################################
def main(session,**kwargs):
    #servicelist = InfoBar.instance.servicelist
    try:
        #this run correctly from extensions menu
        session.open(TVWallWidget, kwargs["servicelist"])
    except:
        #plugin run from Plugins menu doesn't have visibility about servicelist, we need to initialize
        from Screens.InfoBar import InfoBar
        session.open(TVWallWidget, InfoBar.instance.servicelist)

class TVWallWidget(Screen):
    print("[TVWall] start")
   
    def __init__(self, session, servicelist = None):
        self.session = session
        Screen.__init__(self, session)
        self.started = 0
        # Ustawienia listy
        self.servicelist = servicelist
        self.curRef = ServiceReference(self.servicelist.getCurrentSelection())
        self.curChannel = self.servicelist.getCurrentSelection().toString()
        self.curBouquet = self.servicelist.getRoot()
        self.onShow.append(self.onStart)
        self.curIndex = 0

    def onStart(self):
        if self.started == 0:
            self.selectTVWallChannel()
            self.started = 1
        return

    def getListFromRef(self, ref): # pobieramy liste kanalow
        list = []

        serviceHandler = eServiceCenter.getInstance()
        services = serviceHandler.list(ref)
        bouquets = services and services.getContent("SN", True)

        for bouquet in bouquets:
            services = serviceHandler.list(eServiceReference(bouquet[0]))
            channels = services and services.getContent("SN", True)
            for channel in channels:
                if not channel[0].startswith("1:64:"): # Ignore marker
                    list.append((channel[0] , channel[1].replace('\xc2\x86', '').replace('\xc2\x87', '')))
            return list

    def selectTVWallChannel(self):
        #self.radio_list = self.getListFromRef(eServiceReference('1:7:2:0:0:0:0:0:0:0:(type == 2) FROM BOUQUET "bouquets.radio" ORDER BY bouquet'))
        self.tv_list = self.getListFromRef(eServiceReference('1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 195) || (type == 25) FROM BOUQUET "bouquets.tv" ORDER BY bouquet'))
        for idx in range(0,len(self.tv_list)): 
            if self.curChannel == self.tv_list[idx][0]:
                self.curIndex = idx
        self.session.openWithCallback(self.selectTVWallChannelCallback, SelectorWidget, list = self.tv_list, CurIdx = self.curIndex, sSL = self.servicelist)
        return
    
    def selectTVWallChannelCallback(self, ret): # jako ret dostajemy dane wybranego kanalu i nazwe
        self.myZap(ret)
        self.close()
        return

    def myZap(self, ret): # jako ret dostajemy dane wybranego kanalu i nazwe
        if ret:               
            print("[TVWall] Selected host" + ret[1] + " " + ret[0])
            service = eServiceReference(ret[0])
            self.servicelist.setCurrentSelection(service) #wybieramy serwis na liscie
            self.servicelist.zap(enable_pipzap = True) # i przelaczamy
        else:
            self.servicelist.setCurrentSelection(self.curRef.ref)
            print("[TVWall] Nothing selected")
        return
