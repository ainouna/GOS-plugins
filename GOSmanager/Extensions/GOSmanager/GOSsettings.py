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
from enigma import eEnv, eTimer
from os import symlink as os_symlink, remove as os_remove, fsync as os_fsync, rename as os_rename, walk as os_walk, listdir, mkdir as os_mkdir, chmod as os_chmod
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.HardwareInfo import HardwareInfo
from Tools.GOSHardwareInfo import GOSHardwareInfo
from Tools.Directories import fileExists, resolveFilename, pathExists, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE
from Components.LanguageGOS import gosgettext as _

GOSsettings_list = [ ]
################## Zmienne GOS #########################################################
# config.GOSsettings.<NAZWA-ZMIENNEJ> = NoSave(ConfigSelection(default = "0", choices = [("0", _("on")), ("off", _("off"))]))
# GOSsettings_list.append((config.GOSsettings.<NAZWA-ZMIENNEJ>,"<NAZWA-ZMIENNEJ>","CONFIG"))
#
# Stała "CONFIG" definiuje parametr zapisywany w /etc/sysctl.gos
# default = "0" oznacza, że wartość domyślna nie będzie zapisywana,w przypadku innej wartości należy poprawić

config.GOSsettings = ConfigSubsection()
config.GOSsettings.separator = NoSave(ConfigNothing())

config.GOSsettings.fscheck = NoSave(ConfigSelection(default = "0", choices = [("0", _("on")), ("off", _("off"))]))
GOSsettings_list.append((config.GOSsettings.fscheck,"fscheck","CONFIG"))

config.GOSsettings.sshd = NoSave(ConfigSelection(default = "on", choices = [("on", "sshd"), ("off", "telnet")]))
GOSsettings_list.append((config.GOSsettings.sshd,"sshd","CONFIG"))

config.GOSsettings.sci = NoSave(ConfigSelection(default = "0", choices = [("tda8004", "tda8004"), ("0", "nbox")]))
GOSsettings_list.append((config.GOSsettings.sci,"sci","CONFIG"))

config.GOSsettings.led = NoSave(ConfigSelection(default = "0", choices = [("on", _("on")), ("0", _("off"))]))
GOSsettings_list.append((config.GOSsettings.led,"led","CONFIG"))

config.GOSsettings.vfd = NoSave(ConfigSelection(default = "0", choices = [("on", _("on")), ("0", _("off"))]))
GOSsettings_list.append((config.GOSsettings.vfd,"vfd","CONFIG"))

config.GOSsettings.SERWER = NoSave(ConfigText(default = "http://xunil.pl/openpli/plugins", fixed_size = False))
GOSsettings_list.append((config.GOSsettings.SERWER,"SERWER","CONFIG"))

config.GOSsettings.NAZWA_PLIKU = NoSave(ConfigText(default = "lista_tuxish.tar.gz", fixed_size = False))
GOSsettings_list.append((config.GOSsettings.NAZWA_PLIKU,"NAZWA_PLIKU","CONFIG"))

##### MODERATE SHUTDOWN #####
config.GOSsettings.ModerateShutDown = NoSave(ConfigSelection(default = "0", choices = [("on", _("moderate")), ("0", _("deep"))]))
GOSsettings_list.append((config.GOSsettings.ModerateShutDown,"ModerateShutDown","CONFIG"))

config.GOSsettings.clockINmoderate = NoSave(ConfigSelection(default = "0", choices = [("0", _("off")), ("on", _("on"))]))
GOSsettings_list.append((config.GOSsettings.clockINmoderate,"clockINmoderate","CONFIG"))

if GOSHardwareInfo().get_rcstype() == 'SPARK7162':
    iconID = "icon36"
elif GOSHardwareInfo().get_rcstype() == 'ADB2850':
    iconID = "icon2"
else:
    iconID = "icon1"

config.GOSsettings.iconINmoderate = NoSave(ConfigSelection(default = "0", choices = [("0", _("off")), ( iconID, _("on"))]))
GOSsettings_list.append((config.GOSsettings.iconINmoderate,"iconINmoderate","CONFIG"))
##### DEBUG #####
config.GOSsettings.oPLIdbg = NoSave(ConfigSelection(default = "0", choices = [("on", _("on")), ("0", _("off"))]))
GOSsettings_list.append((config.GOSsettings.oPLIdbg,"oPLIdbg","CONFIG"))

config.GOSsettings.oPLIdbgFolder = NoSave(ConfigText(default = "/hdd", fixed_size = False))
GOSsettings_list.append((config.GOSsettings.oPLIdbgFolder,"oPLIdbgFolder","CONFIG"))

config.GOSsettings.oPLIdbgArchive = NoSave(ConfigSelection(default = "0", choices = [("0", _("last")), ("on", _("all"))]))
GOSsettings_list.append((config.GOSsettings.oPLIdbgArchive,"oPLIdbgArchive","CONFIG"))

config.GOSsettings.oPLIdbgtimestamp = NoSave(ConfigSelection(default = "0", choices = [("on", _("yes")), ("0", _("no"))]))
GOSsettings_list.append((config.GOSsettings.oPLIdbgtimestamp,"oPLIdbgtimestamp","CONFIG"))

if fileExists("/etc/rc.d/rc5.d/S90reportGS"):
    config.GOSsettings.ReportGS = NoSave(ConfigSelection(default = "on", choices = [("on", _("yes")), ("off", _("no"))]))
else:
    config.GOSsettings.ReportGS = NoSave(ConfigSelection(default = "off", choices = [("on", _("yes")), ("off", _("no"))]))
GOSsettings_list.append((config.GOSsettings.ReportGS,"ReportGS","DEF"))
##### TIME SYNCHRONIZATION #####
config.GOSsettings.useTransponderTime = NoSave(ConfigSelection(default = "0", choices = [("0", _("autoselection")), ("sat", _("from transponder")), ("ntp", _("from NTP server"))]))
GOSsettings_list.append((config.GOSsettings.useTransponderTime,"useTransponderTime","CONFIG"))

config.GOSsettings.activeOpenPLI = NoSave(ConfigSelection(default = "0", choices = [("0", _("autoselection")), ("enigma2", "gStreamer"), ("enigma2-multiframework", "GST&FFM")]))
GOSsettings_list.append((config.GOSsettings.activeOpenPLI,"activeOpenPLI","CONFIG"))

###################### universal evremote #####
config.GOSsettings.useLircdName = NoSave(ConfigSelection(default = "0", choices = [("off", _("Lircd codes")), ("0", _("Lircd names"))]))
GOSsettings_list.append((config.GOSsettings.useLircdName,"useLircdName","CONFIG"))

config.GOSsettings.usePeriod = NoSave(ConfigInteger(130, (90,250)))
GOSsettings_list.append((config.GOSsettings.usePeriod,"usePeriod","CONFIG"))

config.GOSsettings.useDelay = NoSave(ConfigInteger(20, (10,100)))
GOSsettings_list.append((config.GOSsettings.useDelay,"useDelay","CONFIG"))

if GOSHardwareInfo().get_rcstype() == 'SPARK7162':
    config.GOSsettings.blinkingIcon = NoSave(ConfigSelection(default = "35", choices = [("0", _("disabled")), ("35", _("Blue dot")), ("36", _("Standby sign"))]))
elif GOSHardwareInfo().get_rcstype() == 'UHD88':
    config.GOSsettings.blinkingIcon = NoSave(ConfigSelection(default = "0", choices = [("0", _("disabled")), ("2", _("green")), ("1", _("red"))]))
else:
    config.GOSsettings.blinkingIcon = NoSave(ConfigSelection(default = "0", choices = [("0", _("disabled")), ("1", "icon 1"), ("2", "icon 2"), ("3", "icon 3")]))
GOSsettings_list.append((config.GOSsettings.blinkingIcon,"blinkingIcon","CONFIG"))

###################### CPU_FREQ ###### echo $(($CLOCK/10 * 256 + 3)) > $PLL0
if GOSHardwareInfo().get_rcstype() == 'DSI87' or GOSHardwareInfo().get_rcstype() == 'ESI88' or GOSHardwareInfo().get_rcstype() == 'UHD88' or GOSHardwareInfo().get_rcstype() == 'ADB2850':
    config.GOSsettings.cpuFREQ = NoSave(ConfigSelection(default = "0", choices = [("14083", "550MHz"), ("15363", "600MHz"), ("16643", "650MHz"),
                                                                                    ("17923", "700MHz"), ("19203", "750MHz"), ("0", _("standard"))]))
elif GOSHardwareInfo().get_rcstype() == 'SPARK7162':
    config.GOSsettings.cpuFREQ = NoSave(ConfigSelection(default = "0", choices = [("14083", "550MHz"), ("15363", "600MHz"), ("16643", "650MHz"), ("17923", "700MHz"),
                                                                                    ("19203", "750MHz"), ("20483", "800MHz"), ("0", _("standard"))]))
else:
    config.GOSsettings.cpuFREQ = NoSave(ConfigSelection(default = "0", choices = [("7683", "270MHz"), ("8963", "315MHz"), ("9475", "333MHz"),
                                                                                    ("10243", "360MHz"), ("11267", "400MHz"), ("0", "standard")]))
GOSsettings_list.append((config.GOSsettings.cpuFREQ,"cpuFREQ","CONFIG"))

###################### ustawienia dla SPARK7162 #############################
if GOSHardwareInfo().get_rcstype() == 'SPARK7162':
    config.GOSsettings.SPARK7162tunerType = NoSave(ConfigSelection(default = "0", choices = [("0", "DVB-T"), ("DVB-C", "DVB-C")]))
    GOSsettings_list.append((config.GOSsettings.SPARK7162tunerType,"tunerType","CONFIG"))
    
    if fileExists("/etc/cron/minutely/spark7162VFD-BIGclock"): 
        config.GOSsettings.SPARK7162vfdtime = NoSave(ConfigSelection(default = "showclock", choices = [("0", _("no")), ("showclock", _("yes"))]))
    else:
        config.GOSsettings.SPARK7162vfdtime = NoSave(ConfigSelection(default = "0", choices = [("0", _("no")), ("showclock", _("yes"))]))
    GOSsettings_list.append((config.GOSsettings.SPARK7162vfdtime,"spark7162vfd","DEF"))

############## DEBUG ################################################
##############################################################

if not fileExists("/etc/opkg/opkg-ready.conf") and not fileExists("/etc/opkg/opkg-testing.conf"): 
    config.GOSsettings.opkg = NoSave(ConfigSelection(default = "NA", choices = [("NA", "release"), ("ready", "ready"), ("testing", "test")]))
elif not fileExists("/etc/opkg/opkg-testing.conf"): 
    config.GOSsettings.opkg = NoSave(ConfigSelection(default = "NA", choices = [("NA", "ready"), ("testing", "test")]))
else:
    config.GOSsettings.opkg = NoSave(ConfigSelection(default = "NA", choices = [("NA", "test")]))
GOSsettings_list.append((config.GOSsettings.opkg,"opkg","DEF"))

config.GOSsettings.POWERx5 = NoSave(ConfigSelection(default = "NA", choices = [("NA", _("after pressing 5xPOWER quickly")), ("POWERx5", _("after pressing key POWER 5 times"))]))
GOSsettings_list.append((config.GOSsettings.POWERx5,"POWERx5","DEF"))
######################## Obsluga skorek HD ######################################
config.GOSsettings.EnableSkinHD = NoSave(ConfigSelection(default = "0", choices = [("0", _("no")), ("on", _("yes"))]))
GOSsettings_list.append((config.GOSsettings.EnableSkinHD,"EnableSkinHD","CONFIG"))

##############################################################
class GOSsetupMenu(Screen, ConfigListScreen):

    skin = """
    <screen name="GOSsetupMenu" position="center,center" size="640,500" title="GOSsetupMenu" >

            <widget name="config" position="10,10" size="620,450" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />
            <widget name="key_green" position="0,465" zPosition="2" size="200,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="green" />
            <widget name="key_red" position="220,465" zPosition="2" size="200,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="red" />
            <widget name="key_blue" position="440,465" zPosition="2" size="200,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="blue" />

    </screen>"""

    def runSetup(self):
        ###### chwilowe dane do wyboru mapy lircd
        MyKeymap = []
        self.list = [ ]
        for file in listdir("/etc/"):
            #print os_path.join("/etc/", file)
            if file.startswith("lircd") and file.endswith(".conf"):
                #print os_path.join("/etc/", file)
                MyKeymap.append( ( os_path.join("/etc/", file), file ) )
        config.GOSsettings.lircdCONF = NoSave(ConfigSelection(default = "lircd.conf", choices = MyKeymap))
        GOSsettings_list.append((config.GOSsettings.lircdCONF,"lircdCONF","CONFIG"))
        ##### KONIEC DEFINICJI #####
        self.list.append(getConfigListEntry(_("--- Standard settings ---"), config.GOSsettings.separator))

        try: self.list.append(getConfigListEntry(_("Selected terminal:"), config.GOSsettings.sshd))
        except: pass
        if HardwareInfo().get_device_name() == 'nbox':
            self.list.append(getConfigListEntry("Czytnik kart:", config.GOSsettings.sci))
            self.list.append(getConfigListEntry("Wyświetlacz LED:", config.GOSsettings.led))
            self.list.append(getConfigListEntry("Wyświetlacz VFD:", config.GOSsettings.vfd))
        self.list.append(getConfigListEntry(_("Checking file system during boot?"), config.GOSsettings.fscheck))
        #wybor e2
        if fileExists("/usr/bin/enigma2-multiframework"):
            self.list.append(getConfigListEntry(_("openPLI uses:"), config.GOSsettings.activeOpenPLI))
        #drzewo okpg
        if fileExists("/etc/opkg/opkg.conf"):
            self.list.append(getConfigListEntry(_("OPKG branch:"), config.GOSsettings.opkg))
        ###################### ustawienia TYLKO dla SPARK7162 #############################
        if GOSHardwareInfo().get_rcstype() == 'SPARK7162':
            self.list.append(getConfigListEntry(" ", config.GOSsettings.separator))
            self.list.append(getConfigListEntry("--- Spark7162/Triplex/AA2 settings ---", config.GOSsettings.separator))
            self.list.append(getConfigListEntry(_("Air head mode:"), config.GOSsettings.SPARK7162tunerType)) # zapisywane w /etc/sysctl.gos
            self.list.append(getConfigListEntry(_("Time also on main VFD:"), config.GOSsettings.SPARK7162vfdtime)) # zapisywane w /etc/sysctl.gos

        ###### ADDITIONAL SETTINGS #####
        self.list.append(getConfigListEntry(" ", config.GOSsettings.separator))
        self.list.append(getConfigListEntry(_("--- Additional settings ---"), config.GOSsettings.separator))
        self.list.append(getConfigListEntry(_("Enable skins-HD support"), config.GOSsettings.EnableSkinHD)) 
        self.list.append(getConfigListEntry(_("Emergency tuner restart"), config.GOSsettings.POWERx5)) # własna procedura nie wykonywana, bo to tak tylko informacyjnie
        self.list.append(getConfigListEntry(_("Time synchronization:"), config.GOSsettings.useTransponderTime)) # zapisywane w /etc/sysctl.gos
        self.list.append(getConfigListEntry(_("Shutdown type:"), config.GOSsettings.ModerateShutDown)) # moderate gdzie nie ma deep
        if config.GOSsettings.ModerateShutDown.value == "on":
            self.list.append(getConfigListEntry(_("Show clock:"), config.GOSsettings.clockINmoderate))
            self.list.append(getConfigListEntry(_("Set icon:"), config.GOSsettings.iconINmoderate))
        #zmienne globalne z openPLI, generalnie powinny byc zdefiniowane w UsageConfig.py
        try: self.list.append(getConfigListEntry(_("Volume controlled in TV:"), config.hdmicec.volume_forwarding))
        except: pass

        ###### KONIFGURACJA PILOTA #####
        self.list.append(getConfigListEntry(" ", config.GOSsettings.separator))
        self.list.append(getConfigListEntry(_("--- Remote control settings ---"), config.GOSsettings.separator))
        self.list.append(getConfigListEntry(_("Lircd settings:"), config.GOSsettings.lircdCONF)) # zapisywane w /etc/sysctl.gos
        #self.list.append(getConfigListEntry(_("evremote2 mode:"), config.GOSsettings.useLircdName)) # zapisywane w /etc/sysctl.gos
        #if config.GOSsettings.useLircdName.value == "on":
        self.list.append(getConfigListEntry(_("Blinking icon:"), config.GOSsettings.blinkingIcon))
        self.list.append(getConfigListEntry(_("Max. key press time (90-250, standard 130ms):"), config.GOSsettings.usePeriod)) # zapisywane w /etc/sysctl.gos
        self.list.append(getConfigListEntry(_("Delay (10-100, standard 20ms):"), config.GOSsettings.useDelay)) # zapisywane w /etc/sysctl.gos
        #Advanced settings
        self.list.append(getConfigListEntry(" ", config.GOSsettings.separator))
        self.list.append(getConfigListEntry(_("--- Advanced settings ---"), config.GOSsettings.separator))
        if fileExists("/lib/modules/cpu_frequ.ko") or fileExists("/lib/modules/cpu_freq.ko"):
            mySPEED = "(---)"
            if fileExists("/proc/cpu_frequ/pll0_ndiv_mdiv"):
                with open ("/proc/cpu_frequ/pll0_ndiv_mdiv", "r") as mySPEEDfile:
                    for line in mySPEEDfile:
                        if line.startswith('SH4') and not line.startswith('SH4_'): 
                            mySPEED = _("(now %sMHz)") % line.split()[2]
                            break
                    mySPEEDfile.close()
                
            self.list.append(getConfigListEntry(_("CPU speed %s:") % mySPEED, config.GOSsettings.cpuFREQ))
        self.list.append(getConfigListEntry(_("Write debug logs?"), config.GOSsettings.oPLIdbg))
        self.list.append(getConfigListEntry(_("timestamp each item?"), config.GOSsettings.oPLIdbgtimestamp))
        self.list.append(getConfigListEntry(_("Debug logs in:"), config.GOSsettings.oPLIdbgFolder))
        self.list.append(getConfigListEntry(_("Keep old logs?"), config.GOSsettings.oPLIdbgArchive))
        
        self.list.append(getConfigListEntry(_("Automatically share GS during boot?"), config.GOSsettings.ReportGS))

        #outdated?
        #self.list.append(getConfigListEntry("Serwer z listą kanałów:", config.GOSsettings.SERWER))
        #self.list.append(getConfigListEntry("Archiwum listy kanałów:", config.GOSsettings.NAZWA_PLIKU))

        self["config"].list = self.list
        self["config"].setList(self.list)

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()
        
    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        if self["config"].getCurrent()[1] == config.GOSsettings.opkg:
            if config.GOSsettings.opkg.value == "testing":
                self.session.open(MessageBox,_("WARNING: The probability of issues in 'testing' branch is high. It's NOT recommended for unexperienced users!\n\nReturning to release branch only through reinstallation!!!"),  MessageBox.TYPE_INFO)
            elif config.GOSsettings.opkg.value == "ready":
                self.session.open(MessageBox,_("WARNING: The probability of issues in 'ready' branch is small, but exists."),  MessageBox.TYPE_INFO)
        elif self["config"].getCurrent()[1] == config.GOSsettings.ModerateShutDown:
            self.runSetup()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        if self["config"].getCurrent()[1] == config.GOSsettings.opkg:
            if config.GOSsettings.opkg.value == "testing":
                self.session.open(MessageBox,_("WARNING: The probability of issues in 'testing' branch is high. It's NOT recommended for unexperienced users!\n\nReturning to release branch only through reinstallation!!!"),  MessageBox.TYPE_INFO)
            elif config.GOSsettings.opkg.value == "ready":
                self.session.open(MessageBox,_("WARNING: The probability of issues in 'ready' branch is small, but exists."),  MessageBox.TYPE_INFO)
        elif self["config"].getCurrent()[1] == config.GOSsettings.ModerateShutDown:
            self.runSetup()

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
        
    def layoutFinished(self):
        self.setTitle(_("Graterlia system settings configurator"))
        self.getValues()
        self.runSetup()
    
    def __init__(self, session):
        Screen.__init__(self, session)

        self.onChangedEntry = [ ]
        self.list = [ ]
        ConfigListScreen.__init__(self, self.list, session = session, on_change = self.changedEntry)
        self.setup_title = _("Graterlia system settings configurator")
        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "cancel": self.keyCancel,
                "green": self.keySave,
                "ok": self.keySave,
                "red": self.keyCancel,
                "blue": self.keyBlue,
            }, -2)

        self["key_green"] = Label(_("Save"))
        self["key_red"] = Label(_("Cancel"))
        self["key_blue"] = Label(_("Restart RC"))

        self.MySetupFile = ""
        if fileExists("/etc/init.d/graterlia_init"):
            self.MySetupFile="/etc/sysctl.gos"
        else:
            self.MySetupFile= resolveFilename(SCOPE_PLUGINS, 'Extensions/GOSmanager/sysctl.gos') #to do developowania na openpliPC
        
        self.myConsole = Console()
        #self.runSetup()
        self.onLayoutFinish.append(self.layoutFinished)

    def keyBlue(self):
        self.keySave
        self.myConsole.ePopen('/etc/init.d/gremotecontrol restart')
        
    def opkg2test(self, decyzja): #tutaj wpadniemy jedynie po zmianie repo, czyli raz
        if decyzja is False:
            return
        #czyli zmieniamy
        if config.GOSsettings.opkg.value == "ready" or config.GOSsettings.opkg.value == "testing":
            if not fileExists("/etc/opkg/opkg-ready.conf"):
                os_symlink("/etc/opkg/ready.gos","/etc/opkg/opkg-ready.conf")
        if config.GOSsettings.opkg.value == "testing":
            if not fileExists("/etc/opkg/opkg-testing.conf"):
                os_symlink("/etc/opkg/testing.gos","/etc/opkg/opkg-testing.conf")
      
    def keySave(self): #openpliPC - F2 emuluje green
        myContent = "### Utworzono za pomocą konfiguratora ustawień GOS @j00zek ###\n"
        for x in self["config"].list:
            for GOSsetting in GOSsettings_list:
                if GOSsetting[0] == x[1]:
                    opcja = GOSsetting[1]
                    wartosc = x[1].getValue()
                    if GOSsetting[2] == "CONFIG": # do konfiguracji, tylko konfiguracje
                        # wymuszenie wartosci standardowych
                        if str(opcja) == "usePeriod" and str(wartosc) == 130: wartosc=0
                        elif str(opcja) == "useDelay" and str(wartosc) == 20: wartosc=0
                        
                        if str(wartosc) not in ["0" , "lircd.conf"]: # tu ewentualnie dopisac, jakie zmienne są defaultowe
                            myContent += str(opcja) + '=' + str(wartosc) + '\n'
                    elif GOSsetting[2] == "DEF": # musimy zalatwic procedurą
                        print str(opcja)
                        #opkg
                        if str(opcja) == "opkg":
                            if wartosc != "NA": #NA to nasz defaultowy release, po prostu not available ;)
                                self.session.openWithCallback(self.opkg2test,MessageBox,_("Are you sure, you want to switch opkg branch to UNSTABLE %s?") % wartosc, MessageBox.TYPE_YESNO)
                        #reportGS
                        elif str(opcja) == "ReportGS":
                            if config.GOSsettings.ReportGS.value == "off" and fileExists("/etc/rc.d/rc5.d/S90reportGS"):
                                os_remove("/etc/rc.d/rc5.d/S90reportGS")
                            elif config.GOSsettings.ReportGS.value == "on" and not fileExists("/etc/rc.d/rc5.d/S90reportGS"):
                                os_chmod(resolveFilename(SCOPE_PLUGINS, 'Extensions/GOSmanager/components/reportGS'), 0775)
                                os_symlink(resolveFilename(SCOPE_PLUGINS, 'Extensions/GOSmanager/components/reportGS'),"/etc/rc.d/rc5.d/S90reportGS")
                                
            x[1].save()
        #zapis konfiguracji gos
        with open (self.MySetupFile, "w") as myconfigfile:
            myconfigfile.write(myContent)
            myconfigfile.flush()
            os_fsync(myconfigfile.fileno())
            myconfigfile.close()
        configfile.save()
        self.close()

    def getValues(self):
       if not fileExists(self.MySetupFile):
          return
       with open (self.MySetupFile, "r") as myconfigfile:
            for line in myconfigfile:
                if not line or line[0] == '#':
                    continue
                line = line.split("\n")[0]
                skladniki = line.split('=', 1)
                if len(skladniki) != 2:
                    continue
                (opcja, wartosc) = skladniki
                wartosc = wartosc.strip()
                print "[GOSsettings] '%s'='%s'" % (opcja, wartosc)
                for GOSsetting in GOSsettings_list:
                    if GOSsetting[1] == opcja:
                        if opcja in ['usePeriod' , 'useDelay' ]:
                            GOSsetting[0].value = int(wartosc)
                        else:
                            GOSsetting[0].value = wartosc
