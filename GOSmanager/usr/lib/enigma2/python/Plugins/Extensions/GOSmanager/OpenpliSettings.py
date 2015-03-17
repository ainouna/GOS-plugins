# -*- coding: utf-8 -*-
#######################################################################
#
#    Plugin for GOS
#    Coded by j00zek (c)2014
#
#######################################################################

from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Label import Label
from enigma import eEnv, eTimer
from os import symlink as os_symlink, remove as os_remove, fsync as os_fsync, rename as os_rename, walk as os_walk, listdir
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.HardwareInfo import HardwareInfo
from Tools.Directories import fileExists, resolveFilename, pathExists, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE
from Components.LanguageGOS import gosgettext as _

##############################################################

class openPLIsetup(Screen, ConfigListScreen):

    skin = """
    <screen name="openPLIsetup" position="center,center" size="640,340" title="openPLIsetup" >

            <widget name="config" position="10,10" size="620,290" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />
            <widget name="key_green" position="0,305" zPosition="2" size="200,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="green" />
            <widget name="key_red" position="220,305" zPosition="2" size="200,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="red" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)

        self.onChangedEntry = [ ]
        self.list = [ ]
        ConfigListScreen.__init__(self, self.list, session = session, on_change = self.changedEntry)
        self.setup_title = _("Interesting openPLI options")
        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "cancel": self.keyCancel,
                "green": self.keySave,
                "ok": self.keySave,
                "red": self.keyCancel,
            }, -2)

        self["key_green"] = Label(_("Save"))
        self["key_red"] = Label(_("Cancel"))

        self.MySetupFile = ""
        
        self.runSetup()
        
    def runSetup(self):
        #zmienne globalne z openPLI, generalnie powinny byc zdefiniowane w UsageConfig.py
        try: self.list.append(getConfigListEntry(_("GOS manager window style:"), config.plugins.GOSmanager.InitStyle))
        except: pass

        try: self.list.append(getConfigListEntry(_("Standby mode after power outage?"), config.usage.startup_to_standby))
        except: pass
        try: self.list.append(getConfigListEntry(_("Standby mode when no activity?"), config.usage.inactivity_timer))
        except: pass
        
        try: self.list.append(getConfigListEntry(_("Volume up/down step:"), config.usage.volumestep))
        except: pass
        
        try: self.list.append(getConfigListEntry(_("Volume controlled in TV:"), config.hdmicec.volume_forwarding))
        except: pass

        try: self.list.append(getConfigListEntry(_("EPG file:"), config.misc.epgcache_filename))
        except: pass
        
        try: self.list.append(getConfigListEntry(_("Fallback server enabled?"), config.usage.remote_fallback_enabled))
        except: pass
        
        try: self.list.append(getConfigListEntry(_("Fallback server URL (http://<url>:<port>):"), config.usage.remote_fallback))
        except: pass

        self["config"].list = self.list
        self["config"].setList(self.list)

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()
        
    def keyLeft(self):
        ConfigListScreen.keyLeft(self)

    def keyRight(self):
        ConfigListScreen.keyRight(self)

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
    
    def keyBlue(self):
        self.keySave
        self.myConsole.ePopen('/etc/init.d/gremotecontrol restart')

    def keySave(self):
        for x in self["config"].list:
            x[1].save()
        configfile.save()
        self.close()
