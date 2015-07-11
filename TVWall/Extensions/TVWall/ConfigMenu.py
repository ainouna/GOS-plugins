# -*- coding: utf-8 -*-
#
#  author: j00zek 2015
#
from Screens.Screen import Screen
from Components.ActionMap import ActionMap #, HelpableActionMap
from Components.Label import Label
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigDirectory, ConfigYesNo, Config, ConfigInteger, ConfigSubList, ConfigText, getConfigListEntry, configfile
from Components.ConfigList import ConfigListScreen
from Components.LanguageGOS import gosgettext as _

config.plugins.TVWall = ConfigSubsection()
config.plugins.TVWall.showinextensions = ConfigYesNo(default = True)
config.plugins.TVWall.showinMainMenu = ConfigYesNo(default = False)
#icons
#config.plugins.TVWall.PiconsFolder = ConfigDirectory(default = "/usr/local/share/enigma2/picon/")
config.plugins.TVWall.IconsSize = ConfigSelection(default = "220x132",choices=[("100x60", "Picon 100x60"),("220x132", "XPicon 220x132")]) 
config.plugins.TVWall.PreloadPicons = ConfigYesNo(default = False)
config.plugins.TVWall.ScaleIcons = ConfigYesNo(default = False)
config.plugins.TVWall.usePIG = ConfigYesNo(default = True)
config.plugins.TVWall.PIGSize = ConfigSelection(default = "417x243",choices=[("285x166", "285x166"),("370x216", "370x216"),("417x243", "417x243")]) 

config.plugins.TVWall.ZapMode = ConfigSelection(default = "2ok",choices=[("ok", "Zap immediatelly"),("2ok", "Preview->Zap")]) 
config.plugins.TVWall.AutoPreview = ConfigSelection(default = "2",choices=[("0", "disabled"),("2", "after 2s"),("5", "after 5s"),("10", "after 10s")]) 
class ConfigMenu(Screen, ConfigListScreen):

    skin = """
    <screen name="TVWall_config" position="center,center" size="540,240" title="AQQ" >
            <widget name="config" position="10,10" size="520,205" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />
            <widget name="key_green" position="30,205" zPosition="2" size="100,35" valign="center" halign="left" font="Regular;22" transparent="1" foregroundColor="green" />
            <widget name="key_red" position="410,205" zPosition="2" size="100,35" valign="center" halign="right" font="Regular;22" transparent="1" foregroundColor="red" />
    </screen>"""
    
    def __init__(self, session):
        print "[TVWall] ConfigMenu:__init__"
        Screen.__init__(self, session)
        
        self.onChangedEntry = [ ]
        self.list = [ ]
        ConfigListScreen.__init__(self, self.list, session = session, on_change = self.changedEntry)
        self.setup_title = "Settings config"

        self["key_green"] = Label(_("Save"))
        self["key_red"] = Label(_("Cancel"))
        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "cancel": self.keyCancel,
                "green": self.keySave,
                "ok": self.keyOK,
                "red": self.keyCancel,
            }, -2)

        self.runSetup()
        self.onLayoutFinish.append(self.layoutFinished)
        
    def layoutFinished(self):
        print "[TVWall] ConfigMenu:layoutFinished"
        self.setTitle(_("TVWall config"))

    def runSetup(self):
        print "[TVWall] ConfigMenu:runSetup"

        #self.list.append(getConfigListEntry(_("Picons folder (press OK):"), config.plugins.TVWall.PiconsFolder))
        self.list.append(getConfigListEntry(_("Picons size:"), config.plugins.TVWall.IconsSize))
        self.list.append(getConfigListEntry(_("Preload picons:"), config.plugins.TVWall.PreloadPicons))
        #self.list.append(getConfigListEntry(_("Scale Picons? (slower)"), config.plugins.TVWall.ScaleIcons))

        self.list.append(getConfigListEntry(_("Zap mode:"), config.plugins.TVWall.ZapMode))
        self.list.append(getConfigListEntry(_("AutoPreview delay:"), config.plugins.TVWall.usePIG))

        self.list.append(getConfigListEntry(_("Show PIG (miniTV) window?"), config.plugins.TVWall.usePIG))
        self.list.append(getConfigListEntry(_("PIG size/Descr width:"), config.plugins.TVWall.PIGSize))
        self.list.append(getConfigListEntry(_("Show plugin on the Extensions menu?"), config.plugins.TVWall.showinextensions))
        self.list.append(getConfigListEntry(_("Show plugin in main menu?"), config.plugins.TVWall.showinMainMenu))
        
        self["config"].list = self.list
        self["config"].setList(self.list)

    def keySave(self):
        self.save()
        self.close()
    
    def save(self):
        for x in self["config"].list:
            x[1].save()
        configfile.save()
        
    def keyOK(self):
        curIndex = self["config"].getCurrentIndex()
        currItem = self["config"].list[curIndex][1]
        if isinstance(currItem, ConfigDirectory):
            def SetDirPathCallBack(curIndex, newPath):
                if None != newPath: self["config"].list[curIndex][1].value = newPath
            from Plugins.Extensions.GOSmanager.filebrowserwidget import DirectorySelectorWidget
            from Tools.BoundFunction import boundFunction
            self.session.openWithCallback(boundFunction(SetDirPathCallBack, curIndex), DirectorySelectorWidget, currDir=currItem.value, title=_("Select directory"))

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()
        
    def changeSubOptions(self):
        return
        
    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.changeSubOptions()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.changeSubOptions()

    def changedEntry(self):
        for x in self.onChangedEntry:
            x() 
            
    def keyVirtualKeyBoard(self):
        try:
            if isinstance( self["config"].getCurrent()[1], ConfigText ):
                from Screens.VirtualKeyBoard import VirtualKeyBoard
                text = self["config"].getCurrent()[1].value
                self.session.openWithCallback(self.keyVirtualKeyBoardCallBack, VirtualKeyBoard, title = (_("Enter value")), text = text)
        except:
            pass
            
    def keyVirtualKeyBoardCallBack(self, callback):
        try:
            if callback:  
                self["config"].getCurrent()[1].value = callback
            else:
                pass
        except:
            pass
            