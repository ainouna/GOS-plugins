# -*- coding: utf-8 -*-
from Plugins.Plugin import PluginDescriptor
from enigma import iPlayableService, eDVBVolumecontrol, eVideoWidget, getDesktop
import time
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Label import Label
from Components.LanguageGOS import gosgettext as _
from Tools.GOSHardwareInfo import GOSHardwareInfo
#from Screens.InfoBarGeneric import InfoBarChannelSelection

FirstTimeRun = True


class SVArun:
    def __init__(self, session):
        
        self.session = session
        self.onClose = [ ]
        
        self.__event_tracker = ServiceEventTracker(screen=self,eventmap=
            {
                iPlayableService.evUpdatedInfo: self.__evUpdatedInfo,
                iPlayableService.evGstreamerPlayStarted: self.__evUpdatedInfo,
                iPlayableService.evStart: self.__evStart,
                iPlayableService.evStopped: self.__evStopped,
            })
        
        self.currentVolume = 0
        self.LastVolume = 0
        self.MuteVolume = 0
        self.Muted = False
        self.dst_left = open("/proc/stb/vmpeg/0/dst_left").readline().strip()
        self.dst_top = open("/proc/stb/vmpeg/0/dst_top").readline().strip()
        self.dst_width = open("/proc/stb/vmpeg/0/dst_width").readline().strip()
        self.dst_height = open("/proc/stb/vmpeg/0/dst_height").readline().strip()
        self.NewService = False
        #InfoBarChannelSelection.onShown.append(self.chList_onShown)

    def chList_onShown(self):
        print "[SVA] chList_onShown"
    
    def __evStart(self):
        if config.plugins.SVA.PreviewHelper.value == True:
            self.NewService = True
            #print('[SVA] __evStart: echo "%s,%s,%s,%s">/proc/stb/vmpeg/0/dst_all' % (self.dst_left,self.dst_top,self.dst_width,self.dst_height) )
    
    def __evStopped(self):
        print "[SVA] __evStopped"
        if config.plugins.SVA.PreviewHelper.value == True:
            self.dst_left = open("/proc/stb/vmpeg/0/dst_left").readline().strip()
            self.dst_top = open("/proc/stb/vmpeg/0/dst_top").readline().strip()
            self.dst_width = open("/proc/stb/vmpeg/0/dst_width").readline().strip()
            self.dst_height = open("/proc/stb/vmpeg/0/dst_height").readline().strip()
            print ("[SVA]__evStopped: %s, %s, %s, %s\n" % (self.dst_left,self.dst_top,self.dst_width,self.dst_height))
        if config.plugins.SVA.muteONzap.value == True:
            self.Muted = True
            self.MuteVolume = eDVBVolumecontrol.getInstance().getVolume()
            eDVBVolumecontrol.getInstance().setVolume(0,0)
            print('[SVArun:__evStopped] %i>0' % self.MuteVolume)
        else:
            print('[SVArun:__evStopped] muteONzap disabled')
        
    def __evUpdatedInfo(self):
        print "[SVArun:__evUpdatedInfo] >>>"
        global FirstTimeRun
        if FirstTimeRun is True:
            FirstTimeRun = False
        
        if config.plugins.SVA.enabled.value == True:
            service=self.session.nav.getCurrentService()
            if service is not None:
                audio = service.audioTracks()
                if audio:
                    n = audio.getNumberOfTracks()
                    selectedAudio = audio.getCurrentTrack()
                    for x in range(n):
                        if x == selectedAudio:
                            i = audio.getTrackInfo(x)
                            description = i.getDescription();
                            if description.find("MP3") != -1:
                                self.currentVolume = int(config.plugins.SVA.mp2.value) + int(config.plugins.SVA.mp3adjust.value)
                                print "[SVArun:__evUpdatedInfo]MP3 Volume: %i" % self.currentVolume
                            elif description.find("AC3") != -1 or description.find("DTS") != -1:
                                self.currentVolume = int(config.plugins.SVA.mp2.value) + int(config.plugins.SVA.ac3adjust.value)
                                print "[SVArun:__evUpdatedInfo]AC3/DTS Volume: %i" % self.currentVolume
                            else:
                                self.currentVolume = int(config.plugins.SVA.mp2.value)
                                print "[SVArun:__evUpdatedInfo]MP2 Volume: %i" % self.currentVolume
                            eDVBVolumecontrol.getInstance().setVolume(self.currentVolume, self.currentVolume )
        
        if config.plugins.SVA.muteONzap.value == True and self.MuteVolume != 0 and self.Muted == True:
            print "[SVArun:__evUpdatedInfo] unmute to %i" % self.MuteVolume
            eDVBVolumecontrol.getInstance().setVolume(self.MuteVolume, self.MuteVolume )
            self.MuteVolume = 0
            self.Muted == False
            
        if self.NewService == True:
            self.NewService = False
            if self.dst_top == "0" or self.dst_left == "0" or self.dst_width == "0" or self.dst_height == "0":
                print('[SVA] no need to resize')
            else:
                print('[SVA] __evStart: echo "%s, %s, %s ,%s">/proc/stb/vmpeg/0/dst_all' % (self.dst_left,self.dst_top,self.dst_width,self.dst_height) )
                #with open('/proc/stb/vmpeg/0/dst_all', "w") as f: f.write("%s %s %s %s\n" % (self.dst_left,self.dst_top,self.dst_width,self.dst_height))
                with open('/proc/stb/vmpeg/0/dst_left', "w") as f: f.write("%s\n" % self.dst_left)
                with open('/proc/stb/vmpeg/0/dst_top', "w") as f: f.write("%s\n" % self.dst_top)
                with open('/proc/stb/vmpeg/0/dst_width', "w") as f: f.write("%s\n" % self.dst_width)
                with open('/proc/stb/vmpeg/0/dst_height', "w") as f: f.write("%s\n" % self.dst_height)
                self.dst_left = 0

SVArunInstance = None

########################### DEFINICJA WTYCZKI ################################################

def main(session, **kwargs):
    # Create Instance if none present, show Dialog afterwards
    global SVArunInstance
    if SVArunInstance is None:
        SVArunInstance = SVArun(session)

def startSetup(menuid, **kwargs):
    if menuid != "system":
        return [ ]
    return [(_("Volume Control","plugin-SimpleVolumeAdjustment"), mainsetup, "SVAconfig", None)]

def mainsetup(session,**kwargs):
    session.open(SVASetupMenu)

def Plugins(**kwargs):
    if GOSHardwareInfo().get_rcstype() == 'ADB5800':
        return [ PluginDescriptor(name="SVAsetup", where = PluginDescriptor.WHERE_SESSIONSTART, fnc=main ),
                PluginDescriptor(name=_("Volume Control","plugin-SimpleVolumeAdjustment"), where = PluginDescriptor.WHERE_MENU, fnc=startSetup)
                ]
    else:
        return [ PluginDescriptor(name="SVAsetup", where = PluginDescriptor.WHERE_SESSIONSTART, fnc=main ),
                PluginDescriptor(name=_("Volume and PIG Control","plugin-SimpleVolumeAdjustment"), where = PluginDescriptor.WHERE_MENU, fnc=startSetup)
                ]

########################### KONFIGURATOR ################################################
config.plugins.SVA = ConfigSubsection()
config.plugins.SVA.enabled = ConfigYesNo(default = False)
config.plugins.SVA.muteONzap = ConfigYesNo(default = False)
config.plugins.SVA.ac3adjust = ConfigSelectionNumber(0, 80, 5, default = 40)
config.plugins.SVA.mp3adjust = ConfigSelectionNumber(0, 80, 5, default = 0)
config.plugins.SVA.mp2 = ConfigSelectionNumber(20, 65, 5, default = 60)
config.plugins.SVA.PreviewHelper = ConfigYesNo(default = False)

class SVASetupMenu(Screen, ConfigListScreen):

    skin = """
    <screen name="SVASetupMenu" position="center,center" size="540,200" title="j00zek">

            <widget name="config" position="10,10" size="520,150" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />
            <widget name="key_green" position="0,160" zPosition="2" size="250,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="green" />
            <widget name="key_red" position="250,160" zPosition="2" size="250,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="red" />

    </screen>"""
    
    def __init__(self, session):
        Screen.__init__(self, session)

        self.onChangedEntry = [ ]
        self.list = [ ]
        ConfigListScreen.__init__(self, self.list, session = session, on_change = self.changedEntry)
        self.setup_title = _("Simple Volume Control","plugin-SimpleVolumeAdjustment")
        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "cancel": self.keyCancel,
                "green": self.keySave,
                "ok": self.keySave,
                "red": self.keyCancel,
            }, -2)

        self["key_green"] = Label(_("Save","enigma2"))
        self["key_red"] = Label(_("Cancel","enigma2"))

        #self.runSetup()
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(_("Simple Volume Control","plugin-SimpleVolumeAdjustment"))
        self.runSetup()
        
    def runSetup(self):

        self.list.append(getConfigListEntry(_("Volume Controlled in TV?","plugin-SimpleVolumeAdjustment"), config.plugins.SVA.enabled))
        self.list.append(getConfigListEntry(_("Mute on zap?","plugin-SimpleVolumeAdjustment"), config.plugins.SVA.muteONzap))
        self.list.append(getConfigListEntry(_("Volume for MP2:","plugin-SimpleVolumeAdjustment"), config.plugins.SVA.mp2))
        self.list.append(getConfigListEntry(_("Adjust AC3/DTS by:","plugin-SimpleVolumeAdjustment"), config.plugins.SVA.ac3adjust))
        self.list.append(getConfigListEntry(_("Adjust MP3 by:","plugin-SimpleVolumeAdjustment"), config.plugins.SVA.mp3adjust))
        if GOSHardwareInfo().get_rcstype() != 'ADB5800':
            self.list.append(getConfigListEntry(_("Activate PIG preview on Channel list helper:","plugin-SimpleVolumeAdjustment"), config.plugins.SVA.PreviewHelper))
        
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
        
    def keyLeft(self):
        ConfigListScreen.keyLeft(self)

    def keyRight(self):
        ConfigListScreen.keyRight(self)

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
