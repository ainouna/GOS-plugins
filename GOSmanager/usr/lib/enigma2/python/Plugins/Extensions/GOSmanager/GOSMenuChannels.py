# -*- coding: utf-8 -*-
#######################################################################
#
#    Plugin for GOS
#    Coded by j00zek (c)2014/2015
#
#######################################################################

from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Console import Console
from Components.Label import Label
from GOSconsole import GOSconsole
from os import remove as os_remove #symlink as os_symlink, remove as os_remove, fsync as os_fsync, rename as os_rename, walk as os_walk, listdir, mkdir as os_mkdir, chmod as os_chmod
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.Directories import fileExists, resolveFilename, pathExists, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE
from Components.LanguageGOS import gosgettext as _

config.plugins.GOS = ConfigSubsection()
config.plugins.GOS.separator = NoSave(ConfigNothing())

config.plugins.GOS.chlistEnableTunersSynchro = ConfigYesNo(default = False)
config.plugins.GOS.chlistServerIP = ConfigText(default = "192.168.1.5", fixed_size = False)
config.plugins.GOS.chlistServerLogin = ConfigText(default = "root", fixed_size = False)
config.plugins.GOS.chlistServerPass = ConfigText(default = "root", fixed_size = False)
config.plugins.GOS.chlistServerHidden = ConfigYesNo(default = False)
config.plugins.GOS.chlistEnableSatSynchro = ConfigYesNo(default = True)
config.plugins.GOS.j00zekBouquetsID = ConfigSelection(default = "49188PL", choices = [("NA", _("Not selected")), ("49186", "NC+ HotBird & Astra"), ("49188", "NC+ HotBird"), ("49188PL", "NC+ HotBird-PL")])
config.plugins.GOS.j00zekBouquetsClearLameDB = ConfigYesNo(default = False)
if pathExists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/AutoBouquetsMaker')) is True:
    config.plugins.GOS.j00zekBouquetsAction = ConfigSelection(default = "prov", choices = [("prov", _("Create bouquet with provider order")), ("CustomLCN", _("Update ABM CustomLCN definition")), ("1st", _("Refresh 1st bouquet on the list"))])
else:
    config.plugins.GOS.j00zekBouquetsAction = ConfigSelection(default = "prov", choices = [("prov", _("Create bouquet with provider order")), ("1st", _("Refresh 1st bouquet on the list"))])
config.plugins.GOS.j00zekBouquetsAuto =ConfigSelection(default = "manual", choices = [("monthly", _("auto-monthly")), ("weekly", _("auto-weekly")), ("daily", _("auto-daily")), ("manual", _("manual"))])

##############################################################

class GOSMenuChannels(Screen, ConfigListScreen):

    skin = """
    <screen name="GOSMenuChannels" position="center,center" size="640,500" title="GOSMenuChannels" >

            <widget name="config" position="10,10" size="620,450" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />
            <widget name="key_red" position="0,465" zPosition="2" size="100,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="red" />
            <widget name="key_green" position="105,465" zPosition="2" size="100,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="green" />
            <widget name="key_yellow" position="210,465" zPosition="2" size="210,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="yellow" />
            <widget name="key_blue" position="425,465" zPosition="2" size="215,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="blue" />

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
        self["key_blue"] = Label(_("Synchronize from tuner"))
        self["key_yellow"] = Label(_("Synchronize from sat"))
        
        self.prev_running_service = self.session.nav.getCurrentlyPlayingServiceReference()
        
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(_("Graterlia channels list synchronization"))
        self.runSetup()

    def runSetup(self):
        self.list = [ ]
        #self.list.append(getConfigListEntry(_("Synchronize in background?"), config.plugins.GOS.chlistServerHidden))
        self.list.append(getConfigListEntry(_("--- Local synchronization ---"), config.plugins.GOS.separator))
        self.list.append(getConfigListEntry(_("Get channels list from tuner:"), config.plugins.GOS.chlistServerIP))
        self.list.append(getConfigListEntry(_("Login as:"), config.plugins.GOS.chlistServerLogin))
        self.list.append(getConfigListEntry(_("Password:"), config.plugins.GOS.chlistServerPass))
        self.list.append(getConfigListEntry(_(" "), config.plugins.GOS.separator))
        self.list.append(getConfigListEntry(_("--- Satellite synchronization ---"), config.plugins.GOS.separator))
        self.list.append(getConfigListEntry(_("Update bouquet for:"), config.plugins.GOS.j00zekBouquetsID))
        self.list.append(getConfigListEntry(_("Update type:"), config.plugins.GOS.j00zekBouquetsAuto))
        self.list.append(getConfigListEntry(_("Clear lamedb:"), config.plugins.GOS.j00zekBouquetsClearLameDB))
        self.list.append(getConfigListEntry(_("Action:"), config.plugins.GOS.j00zekBouquetsAction))
        self["config"].list = self.list
        self["config"].setList(self.list)
    
    def changedEntry(self):
        for x in self.onChangedEntry:
            x()

    def keyYellow(self):
        if config.plugins.GOS.j00zekBouquetsID.value != 'NA':
            #collecting info about NIM
            currentlyPlayingNIM = 0
            currentService = self.session and self.session.nav.getCurrentService()
            frontendInfo = currentService and currentService.frontendInfo()
            frontendData = frontendInfo and frontendInfo.getAll(True)
            if frontendData is not None:
                currentlyPlayingNIM = frontendData.get("tuner_number", None)
            del frontendInfo
            del currentService
            #stopping playing service
            self.session.nav.stopService()
            #tunning to transponder containing
            from Components.TuneTest import Tuner
            activeTuner = Tuner(currentlyPlayingNIM)
            
            #if config.plugins.GOS.j00zekBouquetsID.value.startswith('4918'):
            #    ZapTo=(10719, 27500, 1, 4, 2, 130, 0, 1, 0, 2)
            
            #activeTuner.tune(ZapTo)

            from GOSconsole import GOSconsole
            j00zekBouquets = "%s %s %s %s" % (resolveFilename(SCOPE_PLUGINS, 'Extensions/GOSmanager/components/j00zekBouquetsNC'), \
                config.plugins.GOS.j00zekBouquetsID.value, config.plugins.GOS.j00zekBouquetsClearLameDB.value, \
                config.plugins.GOS.j00zekBouquetsAction.value)
                
            self.session.openWithCallback(self.keyYellowEndRun ,GOSconsole, title = "j00zekBouquets...", cmdlist = [ ('%s' % j00zekBouquets ) ])

    def keyYellowEndRun(self, ret =0):
        from enigma import eDVBDB
        db = eDVBDB.getInstance()
        db.reloadServicelist()
        db.reloadBouquets()
        if self.prev_running_service:
            self.session.nav.playService(self.prev_running_service)

        
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
        if pathExists('/etc/cron/daily/j00zekBouquets') is True:
            os_remove('/etc/cron/daily/j00zekBouquets')
        elif pathExists('/etc/cron/weekly/j00zekBouquets') is True:
            os_remove('/etc/cron/weekly/j00zekBouquets')
        elif pathExists('/etc/cron/monthly/j00zekBouquets') is True:
            os_remove('/etc/cron/monthly/j00zekBouquets')
        if config.plugins.GOS.j00zekBouquetsAuto.value !='manual':
            if pathExists('/etc/cron/%s/j00zekBouquets' % config.plugins.GOS.j00zekBouquetsAuto.value ) is False:
                j00zekBouquets = "%s %s %s %s\n" % (resolveFilename(SCOPE_PLUGINS, 'Extensions/GOSmanager/components/j00zekBouquets'), \
                    config.plugins.GOS.j00zekBouquetsID.value, config.plugins.GOS.j00zekBouquetsClearLameDB.value, \
                    config.plugins.GOS.j00zekBouquetsAction.value)
                myfile = open('/etc/cron/%s/j00zekBouquets' % config.plugins.GOS.j00zekBouquetsAuto.value,'w')
                myfile.write(j00zekBouquets)
                myfile.close()

              
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
