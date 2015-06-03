# -*- coding: utf-8 -*-
#
#  @j00zek 2015
# 
###################################################
# local imports
###################################################
from Components.LanguageGOS import gosgettext as _
###################################################
# Import foreign scrits
###################################################
from Components.Console import Console
from Components.Language import language
from Components.config import *
#from Screens.Console import Console as Screens_Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, pathExists, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE
from os import path as os_path, listdir as os_listdir, system as os_system
from urllib2 import Request, urlopen, URLError, HTTPError
import tarfile
from time import sleep

####################################################
# Wywołanie wtyczki w roznych miejscach
####################################################
from Plugins.Plugin import PluginDescriptor

def Plugins(**kwargs):
    #list = [PluginDescriptor(name="GosManager", description=_("Gratelia OS manager","plugin-GOSmanager"), where = [PluginDescriptor.WHERE_PLUGINMENU], icon="icons/logo.png", fnc=main)] # always show in plugin menu
    list = [PluginDescriptor(name=_("Graterlia OS manager","plugin-GOSmanager"), where = PluginDescriptor.WHERE_EXTENSIONSMENU, needsRestart = False, fnc=main)]
    return list
######################################################
# main code
####################################################
config.plugins.GOSmanager = ConfigSubsection()
config.plugins.GOSmanager.InitStyle = ConfigSelection(default = "list", choices = [("list", _("list")), ("icons", _("icons"))])

def main(session,**kwargs):
    session.open(GOSmanagerWidget)

class GOSmanagerWidget(Screen):
    print("[GOSmanager] starts\n")
   
    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self.started = 0
        # Ustawienia listy
        self.myList = []
        self.onShow.append(self.onStart)
        self.curIndex = 0
        self.myExtensions=resolveFilename(SCOPE_PLUGINS, 'Extensions')
        self.myPath= self.myExtensions + '/GOSmanager'
        self.myItemsPath = self.myPath + '/icons/Menu'
        try:
            self.myLang = language.getLanguage().split('_')[0]
        except:
            self.myLang = "en"
        print "GOS %s/locale/%s/MainMenu" % ( self.myPath , self.myLang )
        if pathExists( "%s/locale/%s/MainMenu/GOSopkg.png" % ( self.myPath , self.myLang ) ) is True: #opkg jest najwazniejsze wiec po nim sprawdzamy
            self.SubTreesPath= "%s/locale/%s/MainMenu" % ( self.myPath , self.myLang )
        else:
            self.SubTreesPath= "%s/locale/en/MainMenu" % self.myPath

    def CloseMe(self, ret = False): 
        self.close() 
        return 

    def onStart(self):
        if self.started == 0:
            self.started = 1
            #odpalmy najpierw pobieranie waznych rzeczy a pozniej kontynuujemy, tak jako opcja
            with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
            self.onStartcont() 
        return

    def onStartcont(self):
        if pathExists( "%s/locale/en/MainMenu" % self.myPath) is False: # jak brakuje angielskiego, to musimy zaintalowac
            self.session.openWithCallback(self.CloseMe, MessageBox,_("GOS manager improperly installed, exiting !!!","plugin-GOSmanager"),  type = MessageBox.TYPE_INFO, timeout = 10)      
        else:
            self.prepareListForSelector()
        
    def prepareListForSelector(self, ret = 0):
        self.myList = []
        files = []
        for file in os_listdir(self.SubTreesPath):
            if file.endswith(".png"):
                if file == "MenuOScam.png":
                    if pathExists( "%s/AlternativeSoftCamManager/plugin.pyo" % self.myExtensions) is False:
                        files.append(file)
                else:
                    files.append(file)
        files.sort()
        for file in files:
            print os_path.join(self.SubTreesPath, file)
            self.myList.append( ( file[:-4] , os_path.join(self.SubTreesPath, file), os_path.join(self.myItemsPath , file) ) )
        #print self.myList
        if len(self.myList) >= 1:
            if config.plugins.GOSmanager.InitStyle.value == 'icons':
                from selector import SelectorWidget #wybor kanalu po nazwie
                self.session.openWithCallback(self.SelectorCallback, SelectorWidget, list = self.myList, CurIdx = self.curIndex, Mytitle = _("Select option","plugin-GOSmanager") )
            else:
                from listselector import ListSelectorWidget #wybor kanalu po nazwie
                self.session.openWithCallback(self.SelectorCallback, ListSelectorWidget, list = self.myList, Mytitle = _("Select option","plugin-GOSmanager") )
        else:
            self.close()
        return

    def runMenu(self, menuName = "Menu", MenuFolder = "" ):
        os_system( "%s/_MenuGenerator.sh %s" % (MenuFolder, MenuFolder) )
        if pathExists("%s/_MenuItems" % MenuFolder ) is True:
            from GOSmenu import myMenu
            self.session.openWithCallback(self.prepareListForSelector(), myMenu, MenuFolder = MenuFolder)      
        else:
            self.session.openWithCallback(self.prepareListForSelector, MessageBox,_("No config file for %s","plugin-GOSmanager") % menuName,  type = MessageBox.TYPE_INFO)      

    def SelectorCallback(self, ret): # jako ret dostajemy nazwe wybranego itemu w 0
        if ret:
            if ret[0] == "GOSsettings":
                from GOSsettings import GOSsetupMenu
                self.session.openWithCallback(self.prepareListForSelector(), GOSsetupMenu)      
            elif ret[0] == "GOSkeymap":
                from GOSkeymap import GOSkeymapMenu
                self.session.openWithCallback(self.prepareListForSelector(), GOSkeymapMenu)      
            elif ret[0] == "GOSuserscripts":
                from GOSuserscripts import UserScripts
                self.session.openWithCallback(self.prepareListForSelector(), UserScripts)      
            elif ret[0][0:4] == "Menu":
                if pathExists("%s/%s/_MenuGenerator.sh" % (self.myPath, ret[0]) ) is True:
                    self.runMenu(ret[0] , "%s/%s" % (self.myPath, ret[0]) )
                else:
                    self.session.openWithCallback(self.prepareListForSelector, MessageBox,_("Menu not available","plugin-GOSmanager"),  type = MessageBox.TYPE_INFO)      
            elif ret[0] == "GOShddmanager":
                from GOShddmanager import GOShddmanager
                self.session.openWithCallback(self.prepareListForSelector(), GOShddmanager)      
            elif ret[0] == "GOSopkg":
                from GOSopkg import GOSopkg
                self.session.openWithCallback(self.prepareListForSelector(), GOSopkg)      
            elif ret[0] == "GOSMenuChannels":
                from GOSMenuChannels import GOSMenuChannels
                self.session.openWithCallback(self.prepareListForSelector(), GOSMenuChannels)      
            elif ret[0].lower() == "openplisettings":
                from OpenpliSettings import openPLIsetup
                self.session.openWithCallback(self.prepareListForSelector(), openPLIsetup)      

            elif ret[0] == "pluginIPTVPlayer":
                if pathExists(self.myExtensions + "/IPTVPlayer") is True:
                    from Plugins.Extensions.IPTVPlayer.plugin import IPTVPlayerWidget
                    self.session.openWithCallback(self.CloseMe, IPTVPlayerWidget)
                else:
                    self.session.openWithCallback(self.prepareListForSelector, MessageBox,_("Install IPTVPlayer plugin through OPKG first","plugin-GOSmanager"),  type = MessageBox.TYPE_INFO)
            elif ret[0] == "pluginUserSkin":
                if pathExists(self.myExtensions + "/UserSkin") is True:
                    from Plugins.Extensions.UserSkin.plugin import UserSkin_Menu
                    self.session.openWithCallback(self.CloseMe, UserSkin_Menu)
                else:
                    self.session.openWithCallback(self.prepareListForSelector, MessageBox,_("Install UserSkin plugin through OPKG first","plugin-GOSmanager"),  type = MessageBox.TYPE_INFO)
            elif ret[0].lower().find("pluginbrowser") > -1:
                from Screens.PluginBrowser import PluginBrowser
                self.session.openWithCallback(self.prepareListForSelector(), PluginBrowser)      
            #elif ret[0].lower().find("extensions") > -1:
            else:
                self.session.openWithCallback(self.prepareListForSelector, MessageBox,_("Plugin not available yet","plugin-GOSmanager"),  type = MessageBox.TYPE_INFO)      
        else:
            self.close()
            return
            