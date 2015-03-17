# -*- coding: utf-8 -*-
#
#  Konfigurator dla iptv 2013
#  autor: j00zek, samsamsam
#

from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.Label import Label
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigDirectory, ConfigYesNo, Config, ConfigInteger, ConfigSubList, ConfigText, getConfigListEntry, configfile
from Components.ConfigList import ConfigListScreen
from libs.tools import removeAllIconsFromPath, IsHostEnabled
try:
    from Components.LanguageGOS import gosgettext as _ 
except:
    from libs.tools import TranslateTXT as _


class ConfigHostMenu(Screen, ConfigListScreen):
    skin = """
    <screen name="IPTV config" position="center,center" size="540,140" title="" backgroundColor="#31000000" >

            <widget name="config" position="10,10" size="520,95" zPosition="1" transparent="0" backgroundColor="#31000000" scrollbarMode="showOnDemand" />
            <widget name="key_green" position="0,105" zPosition="2" size="100,35" valign="center" halign="right" font="Regular;22" transparent="1" foregroundColor="green" />
            <widget name="key_blue" position="100,105" zPosition="2" size="50,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="blue" />
            <widget name="key_red" position="150,105" zPosition="2" size="100,35" valign="center" halign="right" font="Regular;22" transparent="1" foregroundColor="red" />

    </screen>"""
    
    def __init__(self, session, hostName):
        Screen.__init__(self, session)
        
        self.onChangedEntry = [ ]
        self.list = [ ]
        ConfigListScreen.__init__(self, self.list, session = session, on_change = self.changedEntry)
        self.hostName = hostName
        self.setup_title = _("Configuration of %s") % self.hostName

        self["key_green"] = Label(_("Save"))
        self["key_red"] = Label(_("Cancel"))
        self["key_blue"] = Label(_('Virtual Keyboard'))

        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "cancel": self.keyCancel,
                "green": self.keySave,
                "ok": self.keySave,
                "red": self.keyCancel,
                "blue": self.keyVirtualKeyBoard,
            }, -2)

        self.host = __import__('forums.forum' + hostName, globals(), locals(), ['GetConfigList'], -1)
        self.runSetup()
        self.onLayoutFinish.append(self.layoutFinished)
        
    def layoutFinished(self):
        self.setTitle(_("Configuration of %s") % self.hostName)

    def runSetup(self):
        self.list = self.host.GetConfigList()
        self["config"].list = self.list
        self["config"].setList(self.list)

    def keySave(self):
        for x in self["config"].list:
            x[1].save()
        configfile.save()
        
        self.close()

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()
        
    def changeSubOptions(self):
        self.runSetup()
        
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
                self.session.openWithCallback(self.keyVirtualKeyBoardCallBack, VirtualKeyBoard, title = (_("Select value")), text = text)
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
            