# -*- coding: UTF-8 -*-

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox

from Plugins.Plugin import PluginDescriptor
from enigma import eTimer, evfd, eDVBVolumecontrol, iServiceInformation, eServiceCenter, eServiceReference
from time import *
from RecordTimer import *
import Screens.Standby
from ServiceReference import ServiceReference

from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigList
from Components.config import config, configfile, ConfigYesNo, ConfigSubsection, ConfigEnableDisable, getConfigListEntry, ConfigInteger, ConfigSelection, ConfigSelectionNumber, ConfigText
from Components.ConfigList import ConfigListScreen
from Components.LanguageGOS import gosgettext as _

from Screens.InfoBar import InfoBar

import os

myDEBUG = True #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def printDEBUG( callingFunction , myText ):
    if myDEBUG:
        print ("[CECv2] %s: %s" % (callingFunction , myText))

def _getCECModule():

    def _moduleCheck(module):
        test = int(os.popen('lsmod | grep ' + module + ' | wc -l').read().strip())
        if test == 0:
            return False
        else:
            return True

    if _moduleCheck('cec_ctrl'):
        return 'old_cec'
    else:
        return 'new_cec'

CEC_Module = _getCECModule()

config.plugins.CEC = ConfigSubsection()
config.plugins.CEC.Enable = ConfigYesNo(default = True) #globalnie jak False nic nie dziala
config.plugins.CEC.CheckInput = ConfigYesNo(default = False) #tylko dla nowego sterownika CEC

config.plugins.CEC.Delay = ConfigSelectionNumber(0, 5000, 100, default = 300)
config.plugins.CEC.Counter = ConfigSelectionNumber(0, 5, 1, default = 2)
config.plugins.CEC.DelayCounter = ConfigSelectionNumber(100, 1000, 100, default = 100)
config.plugins.CEC.StartDelay = ConfigSelectionNumber(5, 60, 5, default = 30)

config.plugins.CEC.ModerateStandby = ConfigYesNo(default = False)

if CEC_Module == 'old_cec':
    config.plugins.CEC.ActiveSource = ConfigSelection(default = "11", choices = [("11","HDMI1"),("21","HDMI2"),("31","HDMI3"),("41","HDMI4")])
elif CEC_Module == 'new_cec':
    config.plugins.CEC.ActiveSource = ConfigSelection(default = "Auto", choices = [("Auto","Auto"),("11","HDMI1"),("21","HDMI2"),("31","HDMI3"),("41","HDMI4")])
config.plugins.CEC.MiniEnable = ConfigYesNo(default = True)

class CECSetup(ConfigListScreen, Screen):
    skin = """
        <screen name="HDMI CEC Configuration" position="center,center" size="550,400">
            <widget name="config" position="20,10" size="520,330" scrollbarMode="showOnDemand" />
            <ePixmap position="0,350" zPosition="4" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
            <ePixmap position="140,350" zPosition="4" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
            <ePixmap position="280,350" zPosition="4" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
            <ePixmap position="420,350" zPosition="4" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />

            <widget source="key_red" render="Label" position="0,350" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget source="key_green" render="Label" position="140,350" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
        </screen>"""


    def __init__(self, session):
        Screen.__init__(self, session)
        self.title = _("HDMI CEC Configuration")
        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
        {
            "green": self.KeySave,
            "red": self.KeyCancel,
            "ok": self.KeySave,
            "cancel": self.KeyCancel,
        }, -2)
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("OK"))
        self.list = []
        self.list.append(getConfigListEntry(_("Activate CEC interface"), config.plugins.CEC.Enable))
        self.list.append(getConfigListEntry(_("Active TV input"), config.plugins.CEC.ActiveSource))
        if CEC_Module == 'new_cec':
            self.list.append(getConfigListEntry(_("Turn off TV only when on active input"), config.plugins.CEC.CheckInput))
            self.list.append(getConfigListEntry(_("Use alternative mode"), config.plugins.CEC.MiniEnable))
        self.list.append(getConfigListEntry(_("Data send delay [ms]"), config.plugins.CEC.Delay))
        self.list.append(getConfigListEntry(_("Repeat data sending"), config.plugins.CEC.Counter))
        self.list.append(getConfigListEntry(_("Interval between repetitions [ms]"), config.plugins.CEC.DelayCounter))
        self.list.append(getConfigListEntry(_("Status check after reboot [s]"), config.plugins.CEC.StartDelay))
        ConfigListScreen.__init__(self, self.list, session)
        self.setTitle(_("HDMI CEC Configuration"))

    def KeySave(self):
        printDEBUG( "KeySave" , "CEC Setup: save config and quit" )
        for x in self["config"].list:
            x[1].save()

        configfile.save()
        CECControl.ReadConfig(CECInstance)
        self.close()

    def KeyCancel(self):
        printDEBUG( "KeyCancel" , "CEC Setup: quit without saving" )
        print "CEC cancel"
        for x in self["config"].list:
            x[1].cancel()
        self.close()

class CECControl():

    CEC_send = ''
    CEC_Wakeup = ''
    CEC_goStandby = ''
    CEC_ActiveHDMI = ''
    CEC_Delay = 0
    CEC_Counter = 0
    CEC_DelayCounter = 0
    CEC_StartDelay = 0

    def __init__(self, session):

        self.ReadConfig()

        self.licz = 0
        self.standby = 1
        self.timelock=False

        self.timer2 = eTimer()
        self.timer2.stop()

        self.start_timer = eTimer()
        self.start_timer.callback.append(self.CEC_onStart)
        self.start_timer.start(self.CEC_StartDelay,1)

        config.misc.standbyCounter.addNotifier(self.standbyCounterChanged, initial_call = False)
        printDEBUG( "init " , "CEC_InitCompleted=True" )

        return

    def ReadConfig(self):
        #jakie jest nasze aktywne HDMI?
        self.CEC_ActiveHDMI = config.plugins.CEC.ActiveSource.getValue()
        if (self.CEC_ActiveHDMI == "Auto") and (CEC_Module == 'old_cec'):
            self.CEC_ActiveHDMI = "11"

        self.CEC_Delay = config.plugins.CEC.Delay.getValue()
        self.CEC_Counter = config.plugins.CEC.Counter.getValue()
        self.CEC_DelayCounter = config.plugins.CEC.DelayCounter.getValue()
        self.CEC_StartDelay = 1000*config.plugins.CEC.StartDelay.getValue()

        if CEC_Module == 'old_cec':
            self.CEC_send='/proc/stb/hdmi/cec'
            self.CEC_Wakeup='3004'
            self.CEC_goStandby='3036'
            self.CEC_ActiveHDMI = "3f82%s00" % self.CEC_ActiveHDMI
            #porzadki, jak ktos powachlowal sterownikami
            if config.plugins.CEC.CheckInput.value == True:
                config.plugins.CEC.CheckInput.value == False
                config.plugins.CEC.CheckInput.save()
        elif CEC_Module == 'new_cec':
            self.CEC_send="/proc/stb/cec/send"
            self.CEC_Wakeup='30 04 '
            self.CEC_goStandby='30 36 '
            if (self.CEC_ActiveHDMI != "Auto"):
                self.CEC_ActiveHDMI = "3f 82 %s 00 " % self.CEC_ActiveHDMI
        
        return

    def CEC_SendCommand(self, myPath, myCommand):
        ReturnCode=0
        try:
            open(myPath, "w").write(myCommand)
        except IOError:
            ReturnCode=1
            print "Error sending %s to %s :(" %(myCommand , myPath)
        return ReturnCode
    
    def CEC_Standby(self):
        #self.timer2.stop()
        self.timer2.callback.remove(self.CEC_Standby)

        if config.plugins.CEC.CheckInput.value == True: #dziala tylko dla nowego sterownika
            printDEBUG( "CEC_Standby" , "read /proc/stb/cec/state_activesource & /proc/stb/cec/state_cecaddress" )
            sameinput = False
            try:
                activesource = open("/proc/stb/cec/state_activesource").readline().strip()
                cecaddress = open("/proc/stb/cec/state_cecaddress").readline().strip()
                printDEBUG( "CEC_Standby" , "activesource=%s, cecaddress=%s" % (activesource, cecaddress) )
                if activesource == cecaddress:
                    sameinput = True
            except IOError:
                print "reading of /proc/stb/cec/state_activesource or /proc/stb/cec/state_cecaddress failed"
                sameinput = True # can't read ... suppose the same
                if sameinput:
                    printDEBUG( "CEC_Standby" , "%s -> %s" % (self.CEC_goStandby, self.CEC_send ) )
                try:
                    open(self.CEC_send, "w").write(self.CEC_goStandby)
                except IOError:
                    print "writing %s failed" % self.CEC_send
        else:
            printDEBUG( "CEC_Standby" , "%s -> %s" % (self.CEC_goStandby, self.CEC_send ) )
            self.CEC_SendCommand(self.CEC_send, self.CEC_goStandby)

        if self.licz>0 and self.standby==0:
            printDEBUG( "CEC_Standby" , "CEC_DelayCounter: %i, licz: %i" % (self.CEC_DelayCounter, self.licz) )
            self.timer2.callback.append(self.CEC_Standby)
            self.timer2.start(self.CEC_DelayCounter,1)
            self.licz=self.licz-1
        else:
            self.timelock=False

        return

    def CEC_ImageViewOn(self):
        #self.timer2.stop()
        self.timer2.callback.remove(self.CEC_ImageViewOn)

        printDEBUG( "CEC_ImageViewOn" , "%s -> %s" % (self.CEC_Wakeup, self.CEC_send ) )
        self.CEC_SendCommand(self.CEC_send, self.CEC_Wakeup)

        if self.standby==1:
            printDEBUG( "CEC_ImageViewOn" , "CEC_DelayCounter: %i, licz: %i" % (self.CEC_DelayCounter, self.licz) )
            self.timer2.callback.append(self.CEC_ActiveSource)
            self.timer2.start(self.CEC_DelayCounter,1)

        return

    def CEC_ActiveSource(self):
        #self.timer2.stop()
        self.timer2.callback.remove(self.CEC_ActiveSource)

        printDEBUG( "CEC_ActiveSource" , "%s -> %s" % (self.CEC_ActiveHDMI, self.CEC_send) )
        self.CEC_SendCommand(self.CEC_send, self.CEC_ActiveHDMI)

        if self.licz>0 and self.standby==1:
            printDEBUG( "CEC_ActiveSource" , "CEC_DelayCounter: %i, licz: %i" % (self.CEC_DelayCounter, self.licz) )
            self.timer2.callback.append(self.CEC_ImageViewOn)
            self.timer2.start(self.CEC_DelayCounter,1)
            self.licz=self.licz-1
        else:
            self.timelock=False

        return

    def CEC_SystemStandby(self):
        #self.timer2.stop()
        self.timer2.callback.remove(self.CEC_SystemStandby)

        if config.plugins.CEC.CheckInput.value == True:
            sameinput = False
            printDEBUG( "CEC_SystemStandby" , "read /proc/stb/cec/state_activesource & /proc/stb/cec/state_cecaddress" )
            try:
                activesource = open("/proc/stb/cec/state_activesource").readline().strip()
                cecaddress = open("/proc/stb/cec/state_cecaddress").readline().strip()
                printDEBUG( "CEC_SystemStandby" , "activesource=%s, cecaddress=%s" % (activesource, cecaddress) )
                if activesource == cecaddress:
                    sameinput = True
            except IOError:
                print "reading of /proc/stb/cec/state_activesource or /proc/stb/cec/state_cecaddress failed"
                sameinput = True # can't read ... suppose the same
            if sameinput:

                printDEBUG( "CEC_SystemStandby" , "0 -> /proc/stb/cec/systemstandby" )
                self.CEC_SendCommand("/proc/stb/cec/systemstandby", "0")

        else:

            printDEBUG( "CEC_SystemStandby" , "0 -> /proc/stb/cec/systemstandby" )
            self.CEC_SendCommand("/proc/stb/cec/systemstandby", "0")

        if self.licz>0 and self.standby==0:
            printDEBUG( "CEC_SystemStandby" , "CEC_DelayCounter: %i, licz: %i" % (self.CEC_DelayCounter, self.licz) )
            self.timer2.callback.append(self.CEC_SystemStandby)
            self.timer2.start(self.CEC_DelayCounter,1)
            self.licz=self.licz-1
        else:
            self.timelock=False

        return

    def CEC_OneTouchPlay(self):
        #self.timer2.stop()
        self.timer2.callback.remove(self.CEC_OneTouchPlay)

        printDEBUG( "CEC_OneTouchPlay" , "0 -> /proc/stb/cec/onetouchplay" )
        self.CEC_SendCommand("/proc/stb/cec/onetouchplay", "0")

        if self.licz>0 and self.standby==1:
            printDEBUG( "CEC_OneTouchPlay" , "CEC_DelayCounter: %i, licz: %i" % (self.CEC_DelayCounter, self.licz) )
            self.timer2.callback.append(self.CEC_OneTouchPlay)
            self.timer2.start(self.CEC_DelayCounter,1)
            self.licz=self.licz-1
        else:
            self.timelock=False

        return

    def leaveStandby(self):
        printDEBUG( "leaveStandby" , "CEC Box status: Left Standby, CEC_ActiveHDMI: %s" % (self.CEC_ActiveHDMI) )
        
        if config.plugins.CEC.MiniEnable.value == True:
            printDEBUG( "standbyCounterChanged" , "MiniMode enabled" )
            from Components.Console import Console
            myConsole = Console()
            with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
            myConsole.ePopen("/etc/cron/moderatestandby_off/40cec")
            return

        if config.plugins.CEC.Enable.value == True:
            if self.standby==0:
                self.standby = 1
                printDEBUG( "leaveStandby" , "CEC Box status: Not Standby!, CEC_Delay: %i, CEC_Counter: %i" % (self.CEC_Delay, self.CEC_Counter) )
                if not self.timelock:
                    self.licz = self.CEC_Counter
                    self.timelock=True
                    if self.CEC_ActiveHDMI == "Auto":
                        self.timer2.callback.append(self.CEC_OneTouchPlay)
                    else:
                        self.timer2.callback.append(self.CEC_ImageViewOn)
                    self.timer2.start(self.CEC_Delay,1)

        return

    def standbyCounterChanged(self, configElement):
        printDEBUG( "standbyCounterChanged" , "CEC Box status: Go to Standby" )

        from Screens.Standby import inStandby
        inStandby.onClose.append(self.leaveStandby)

        if config.plugins.CEC.MiniEnable.value == True:
            printDEBUG( "standbyCounterChanged" , "MiniMode enabled" )
            from Components.Console import Console
            myConsole = Console()
            with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
            myConsole.ePopen("/etc/cron/moderatestandby_on/20cec")
            return
            
        if config.plugins.CEC.Enable.value == True:
            if self.standby==1:
                self.standby = 0
                printDEBUG( "standbyCounterChanged" , "CEC Box status: Standby!, CEC_Delay: %i, CEC_Counter: %i" % (self.CEC_Delay, self.CEC_Counter) )
                if not self.timelock:
                    self.licz = self.CEC_Counter
                    self.timelock=True
                    if self.CEC_ActiveHDMI == "Auto":
                        self.timer2.callback.append(self.CEC_SystemStandby)
                    else:
                        self.timer2.callback.append(self.CEC_Standby)
                    self.timer2.start(self.CEC_Delay,1)

        return

    def CEC_onStart(self):

        printDEBUG( "CEC_onStart" , "CEC Box status: Check on Start, CEC_StartDelay: %i" % self.CEC_StartDelay)

        if config.plugins.CEC.ModerateStandby.value == True: #jak moderate standby to nie ma co uruchamiac
            config.plugins.CEC.ModerateStandby.value = False #wylaczamy na przyszlosc, musi byc ustawiane kazdorazowo
            config.plugins.CEC.ModerateStandby.save()
            return

        #no need to stop we asked it to iterate one time
        #self.start_timer.stop()
        self.start_timer.callback.remove(self.CEC_onStart)

        if config.plugins.CEC.Enable.value == True:
            if Screens.Standby.inStandby:
                self.standby = 0
                printDEBUG( "CEC_onStart" , "CEC Box status: Standby on Start!" )
                if not self.timelock:
                    self.licz = self.CEC_Counter
                    self.timelock=True
                    if self.CEC_ActiveHDMI == "Auto":
                        self.timer2.callback.append(self.CEC_SystemStandby)
                    else:
                        self.timer2.callback.append(self.CEC_Standby)
                    self.timer2.start(self.CEC_Delay,1)
            else:
                self.standby = 1
                printDEBUG( "CEC_onStart" , "CEC Box status: Not Standby on Start!" )
                if not self.timelock:
                    self.licz = self.CEC_Counter
                    self.timelock=True
                    if self.CEC_ActiveHDMI == "Auto":
                        self.timer2.callback.append(self.CEC_OneTouchPlay)
                    else:
                        self.timer2.callback.append(self.CEC_ImageViewOn)
                    self.timer2.start(self.CEC_Delay,1)

        return

    def standbyOnClose(self):
        printDEBUG( "standbyOnClose" , "To musimy uruchamiac z startopenpli, bo inaczej nie zapanujemy nad trybami")
        return

CECInstance = None

def autostart(session, reason, **kwargs):

    # for name, value in kwargs.items():
    #     print '{0} = {1}'.format(name, value)

    global CECInstance

    if reason == 0: # OpenPLi start
        printDEBUG( "autostart" , "CEC status -> OpenPLi start")
        if CECInstance is None:
            CECInstance = CECControl(session)

    elif reason == 1: # OpenPLi stop

        printDEBUG( "autostart" , "CEC status -> OpenPLi stop")
        CECControl.standbyOnClose(CECInstance)


def main(session, **kwargs):
    session.open(CECSetup)

def startSetup(menuid):
    if menuid != "system":
        return []
    return [(_("HDMI CEC"), main, "HDMI_CEC", None)]

def Plugins(**kwargs):
    return [PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART], needsRestart = True, fnc = autostart), 
        PluginDescriptor(name="HDMI CEC settings", description=_("HDMI CEC settings"), where = PluginDescriptor.WHERE_MENU, fnc=startSetup) ]
