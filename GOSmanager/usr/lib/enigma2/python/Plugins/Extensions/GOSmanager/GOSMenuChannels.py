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
from Components.Console import Console
from Components.Label import Label
from GOSconsole import GOSconsole
#from os import symlink as os_symlink, remove as os_remove, fsync as os_fsync, rename as os_rename, walk as os_walk, listdir, mkdir as os_mkdir, chmod as os_chmod
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.Directories import fileExists, resolveFilename, pathExists, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE
from Components.LanguageGOS import gosgettext as _

config.plugins.GOS = ConfigSubsection()
config.plugins.GOS.separator = NoSave(ConfigNothing())

config.plugins.GOS.chlistServerIP = ConfigText(default = "192.168.1.5", fixed_size = False)
config.plugins.GOS.chlistServerLogin = ConfigText(default = "root", fixed_size = False)
config.plugins.GOS.chlistServerPass = ConfigText(default = "root", fixed_size = False)
config.plugins.GOS.chlistServerHidden = ConfigYesNo(default = False)
config.plugins.GOS.j00zekBouquetsID = ConfigSelection(default = "NA", choices = [("NA", _("Not selected")), ("49186", "NC+ HotBird & Astra"), ("49188", "NC+ HotBird")])
config.plugins.GOS.j00zekBouquetsClearLameDB = ConfigYesNo(default = False)
##############################################################

class GOSMenuChannels(Screen, ConfigListScreen):

    skin = """
    <screen name="GOSMenuChannels" position="center,center" size="640,500" title="GOSMenuChannels" >

            <widget name="config" position="10,10" size="620,450" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />
            <widget name="key_red" position="0,465" zPosition="2" size="140,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="red" />
            <widget name="key_green" position="160,465" zPosition="2" size="140,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="green" />
            <widget name="key_yellow" position="320,465" zPosition="2" size="140,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="blue" />
            <widget name="key_blue" position="500,465" zPosition="2" size="140,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="blue" />

    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)

        self.onChangedEntry = [ ]
        self.list = [ ]
        ConfigListScreen.__init__(self, self.list, session = session, on_change = self.changedEntry)
        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "cancel": self.keyCancel,
                "green": self.keySave,
                "ok": self.keySave,
                "red": self.keyCancel,
                "blue": self.keyBlue,
                "yellow": self.keyYellow,
            }, -2)

        self["key_green"] = Label(_("Save"))
        self["key_red"] = Label(_("Cancel"))
        self["key_blue"] = Label(_("Synchronize"))
        self["key_yellow"] = Label(_("Update bouquet"))
        
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(_("Graterlia channels list synchronization"))
        self.runSetup()

    def runSetup(self):
        self.list = [ ]
        self.list.append(getConfigListEntry(_("Synchronize in background?"), config.plugins.GOS.chlistServerHidden))
        self.list.append(getConfigListEntry(_("Get channels list from:"), config.plugins.GOS.chlistServerIP))
        self.list.append(getConfigListEntry(_("Login as:"), config.plugins.GOS.chlistServerLogin))
        self.list.append(getConfigListEntry(_("Password:"), config.plugins.GOS.chlistServerPass))
        self.list.append(getConfigListEntry(_("Quickly update bouquet for:"), config.plugins.GOS.j00zekBouquetsID))
        self.list.append(getConfigListEntry(_("Clear lamedb:"), config.plugins.GOS.j00zekBouquetsClearLameDB))
        self["config"].list = self.list
        self["config"].setList(self.list)
    
    def changedEntry(self):
        for x in self.onChangedEntry:
            x()

    def keyYellow(self):
        if config.plugins.GOS.j00zekBouquetsID.value != 'NA':
            from GOSconsole import GOSconsole
            j00zekBouquets = "%s %s %s" % (resolveFilename(SCOPE_PLUGINS, 'Extensions/GOSmanager/components/j00zekBouquets'), \
                config.plugins.GOS.j00zekBouquetsID.value, config.plugins.GOS.j00zekBouquetsClearLameDB.value)
                
            self.session.openWithCallback(self.GOSconsoleEndRun ,GOSconsole, title = "j00zekBouquets...", cmdlist = [ ('%s' % j00zekBouquets ) ])

    def keyBlue(self):
        self.session.openWithCallback(self.keyBlueYESNO ,MessageBox,_("Synchronize with %s now?") % config.plugins.GOS.chlistServerIP.value, MessageBox.TYPE_YESNO)
        
    def keyBlueYESNO(self, ret):
        if ret is True:
		mySynchroScript="%s %s %s %s" % (resolveFilename(SCOPE_PLUGINS, 'Extensions/GOSmanager/components/CHlistSynchro.sh'),config.plugins.GOS.chlistServerIP.value,config.plugins.GOS.chlistServerLogin.value,config.plugins.GOS.chlistServerPass.value)
		if config.plugins.GOS.chlistServerHidden.value == False:
			self.session.openWithCallback(self.GOSconsoleEndRun ,GOSconsole, title = _("Graterlia channels list synchronization"), cmdlist = [ (mySynchroScript)])
		else:
			#myConsole = Console()
			Console().ePopen(mySynchroScript , self.ePopenEndRun )
        return
        
    def keySave(self): #openpliPC - F2 emuluje green
        for x in self["config"].list:
            x[1].save()
        configfile.save()
        self.close()

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()
        
    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        #if self["config"].getCurrent()[1] == config.plugins.GOS.opkg:
        #    self.runSetup()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        #if self["config"].getCurrent()[1] == config.plugins.GOS.opkg:
        #    self.runSetup()

    def ePopenEndRun(self, data,retval,extra_args):
        pass

    def GOSconsoleEndRun(self, ret =0):
        return
