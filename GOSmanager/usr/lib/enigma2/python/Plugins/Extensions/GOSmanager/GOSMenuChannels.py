# -*- coding: utf-8 -*-
#######################################################################
#
#   Plugin for GOS
#   Coded by j00zek (c)2014/2015
#
#######################################################################

from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Console import Console
from Components.Label import Label
from enigma import eDVBDB, eServiceReference, eTimer
from GOSconsole import GOSconsole
from os import remove as os_remove, chmod as os_chmod, symlink as os_symlink #fsync as os_fsync, rename as os_rename, walk as os_walk, listdir, mkdir as os_mkdir
from Screens.InfoBar import InfoBar
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import fileExists, resolveFilename, pathExists, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE

try:
    from Components.LanguageGOS import gosgettext as _
    print('LanguageGOS detected')
except:
    print('LanguageGOS not detected, using local _')
    import gettext
    from translate import _ 
if pathExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/GOSmanager')) is True:
    PluginPath = resolveFilename(SCOPE_PLUGINS, 'Extensions/GOSmanager/')
    binType=''
else:
    PluginPath = resolveFilename(SCOPE_PLUGINS, 'Extensions/ChannelsManager/')
    binType='-mips'


config.plugins.GOS = ConfigSubsection()
config.plugins.GOS.separator = NoSave(ConfigNothing())

config.plugins.GOS.chlistServerIP = ConfigText(default = "192.168.1.5", fixed_size = False)
config.plugins.GOS.chlistServerLogin = ConfigText(default = "root", fixed_size = False)
config.plugins.GOS.chlistServerPass = ConfigText(default = "root", fixed_size = False)
config.plugins.GOS.chlistServerHidden = ConfigYesNo(default = False)
config.plugins.GOS.j00zekBouquetsNC = ConfigSelection(default = "NA", choices = [("NA", _("Don't update")),
                                                                                      ("49188PL", "HotBird-PL"),
                                                                                      ("49188", "HotBird"),
                                                                                      ("49186", "HotBird & Astra")
                                                                                      ])
config.plugins.GOS.j00zekBouquetsCP = ConfigSelection(default = "NA", choices = [("NA", _("Don't update")),
                                                                                      ("CP", "Hotbird"),
                                                                                      #("CPPL", "Cyfrowy Polsat-PL")
                                                                                      ])
config.plugins.GOS.j00zekBouquetsClearLameDB = ConfigYesNo(default = False)
config.plugins.GOS.j00zekBouquetsExcludeBouquet = ConfigYesNo(default = False)
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

    onChangedEntry = [ ]
    LastIndex=0
    CurrIndex=0
    j00zekBouquetsBin=''
        
    def __init__(self, session):
        Screen.__init__(self, session)

        
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

        self["key_green"] = Label()
        self["key_green"].setText(_("Save"))
        self["key_red"] = Label(_("Exit"))
        self["key_blue"] = Label(_("Update from tuner"))
        self["key_yellow"] = Label(_("Update from sat"))
        
        self.timer = eTimer()
        
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(_("Graterlia channels list synchronization"))
        self.runSetup()

    def runSetup(self):
        self.list = [ ]
        self.list.append(getConfigListEntry(_("--- Local synchronization ---"), config.plugins.GOS.separator))
        self.list.append(getConfigListEntry(_("Get channels list from tuner:"), config.plugins.GOS.chlistServerIP))
        self.list.append(getConfigListEntry(_("Login as:"), config.plugins.GOS.chlistServerLogin))
        self.list.append(getConfigListEntry(_("Password:"), config.plugins.GOS.chlistServerPass))
        self.list.append(getConfigListEntry(_(" "), config.plugins.GOS.separator))
        self.list.append(getConfigListEntry(_("--- Satellite synchronization ---"), config.plugins.GOS.separator))
        self.list.append(getConfigListEntry(_("nc+:"), config.plugins.GOS.j00zekBouquetsNC))
        self.list.append(getConfigListEntry(_("Cyfrowy Polsat:"), config.plugins.GOS.j00zekBouquetsCP))
        self.list.append(getConfigListEntry(_("Clear lamedb:"), config.plugins.GOS.j00zekBouquetsClearLameDB))
        self.list.append(getConfigListEntry(_("Action:"), config.plugins.GOS.j00zekBouquetsAction))
        self.list.append(getConfigListEntry(_("Exclude predefined channels:"), config.plugins.GOS.j00zekBouquetsExcludeBouquet))
        self["config"].list = self.list
        self["config"].setList(self.list)
    
    def changedEntry(self):
        print "Index: %d" % self["config"].getCurrentIndex()
        for x in self.onChangedEntry:
            x()

    def ConfigureJB(self):
        self.ZapNC=("1:0:1:1163:2AF8:13E:820000:0:0:0:")
        self.ZapCP=("1:0:1:332d:3390:71:820000:0:0:0:")
        self.j00zekBouquetsNCBin='%scomponents/j00zekBouquetsNC%s' % (PluginPath,binType)
        self.j00zekBouquetsCPBin='%scomponents/j00zekBouquetsCP%s' % (PluginPath,binType)
        self.ExcludedSIDsTemplate='%scomponents/excludedSIDs.template' % PluginPath
        self.ExcludedSIDsFileName='userbouquet.excludedSIDs.j00zekAutobouquet.tv'
        self.ExcludedSIDsFile='/etc/enigma2/%s' % self.ExcludedSIDsFileName
        self.IncludedTranspondersTemplate='%scomponents/transponders.PL' % PluginPath
        self.IncludedTranspondersFile='/tmp/transponders.PL'
        self.runlist = []
        self.ZapTo=""
        self.ExcludeSIDS=""
        
        #tylko polskie transpondery
        if config.plugins.GOS.j00zekBouquetsNC.value.endswith('PL'):
            if pathExists(self.IncludedTranspondersFile) is False:
                os_symlink(self.IncludedTranspondersTemplate,self.IncludedTranspondersFile)
        else:
            if pathExists(self.IncludedTranspondersFile) is True:
                os_remove(self.IncludedTranspondersFile)
        #kanaly do pominiecia
        if config.plugins.GOS.j00zekBouquetsExcludeBouquet.value == True:
            self.ExcludeSIDS="ExcludeSIDS"
            if pathExists(self.ExcludedSIDsFile) is False:
                from shutil import copy as shutil_copy
                shutil_copy(self.ExcludedSIDsTemplate,self.ExcludedSIDsFile)
            with open("/etc/enigma2/bouquets.tv", "r") as bouquetsTV:
                needUpdate=1
                for line in bouquetsTV:
                    if line.find(self.ExcludedSIDsFileName) > 0:
                        needUpdate=1
                        break
                bouquetsTV.close()
            with open("/etc/enigma2/bouquets.tv", "a") as bouquetsTV:
                bouquetsTV.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\n' % self.ExcludedSIDsFileName)
                bouquetsTV.close()

        if config.plugins.GOS.j00zekBouquetsNC.value != 'NA':
            self.runlist.append("%s %s %s %s %s" % ( self.j00zekBouquetsNCBin, config.plugins.GOS.j00zekBouquetsNC.value, \
                                config.plugins.GOS.j00zekBouquetsAction.value, self.ZapNC, self.ExcludeSIDS))
            self.ZapTo=self.ZapNC
        if config.plugins.GOS.j00zekBouquetsCP.value != 'NA':
            self.runlist.append("%s %s %s %s %s" % ( self.j00zekBouquetsCPBin, config.plugins.GOS.j00zekBouquetsCP.value, \
                                config.plugins.GOS.j00zekBouquetsAction.value, self.ZapCP, self.ExcludeSIDS))
            if self.ZapTo == "":
                self.ZapTo = self.ZapCP

    def keyYellow(self):
        if config.plugins.GOS.j00zekBouquetsNC.value != 'NA' or config.plugins.GOS.j00zekBouquetsCP.value != 'NA':
            #stopping playing service
            self.prev_root = InfoBar.instance.servicelist.getRoot()
            self.prev_running_service = self.session.nav.getCurrentlyPlayingServiceReference()
            self.session.nav.stopService()
            #cleaningLAMEDB
            if config.plugins.GOS.j00zekBouquetsClearLameDB.value == True:
                self.BuildLameDB()
            #configuring excluded SIDs
            #zap to channel on transponder, we use it as hack to simplify selection of the NIM
            self.ConfigureJB()

            service = eServiceReference(self.ZapTo)
            InfoBar.instance.servicelist.clearPath()
            InfoBar.instance.servicelist.enterPath(service)
            InfoBar.instance.servicelist.setCurrentSelection(service)
            InfoBar.instance.servicelist.zap()
            self.timer.callback.append(self.keyYellowStep2)
            self.timer.start(500,1) # j00zekBouquets waits for e2 to tune.

    def keyYellowStep2(self):
        self.timer.callback.remove(self.keyYellowStep2)
        self.session.openWithCallback(self.keyYellowEndRun ,GOSconsole, title = "j00zekBouquets...", cmdlist = self.runlist)
        
    def keyYellowEndRun(self, ret =0):
        self.reloadLAMEDB()
        self.ZapToPrevChannel()

    def BuildLameDB(self):
        #e2 de facto dodaje nowe serwisy a nie przeladowuje lamedb, wiec musimy najperw wszystkie wykasowac...#
        db = eDVBDB.getInstance()
        SatPositions=[50,70,90,100,130,160,192,215,235,255,260,284,305,313,330,360,390,400,420,450,490,530,550,570,600,620,642,685,705,720,750,800,852]
        for sat in SatPositions:
            db.removeServices(-1, -1, -1, sat)
        # ... teraz dodac to co potrzebujemy :)            
        db.loadServicelist(resolveFilename(SCOPE_PLUGINS, 'Extensions/GOSmanager/components/j00zekBouquets.lamedb'))
        db.saveServicelist()

    def reloadLAMEDB(self):
        eDVBDB.getInstance().reloadServicelist()
        eDVBDB.getInstance().reloadBouquets()

    def ZapToPrevChannel(self):
        InfoBar.instance.servicelist.clearPath()
        InfoBar.instance.servicelist.enterPath(self.prev_root)
        if self.prev_running_service:
            self.session.nav.playService(self.prev_running_service)
    
    def keyBlue(self):
        self.session.openWithCallback(self.keyBlueYESNO ,MessageBox,_("Synchronize with %s now?") % config.plugins.GOS.chlistServerIP.value,\
                                    MessageBox.TYPE_YESNO)
        
    def keyBlueYESNO(self, ret):
        if ret is True:
            runlist=[("%s %s %s %s" % (resolveFilename(SCOPE_PLUGINS, 'Extensions/GOSmanager/components/CHlistSynchro.sh'),\
                    config.plugins.GOS.chlistServerIP.value,config.plugins.GOS.chlistServerLogin.value,config.plugins.GOS.chlistServerPass.value))]
            self.session.openWithCallback(self.GOSconsoleEndRun ,GOSconsole, title = _("Graterlia channels list synchronization"), cmdlist = runlist)
            self.reloadLAMEDB()
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

    def GOSconsoleEndRun(self, ret =0):
        return
