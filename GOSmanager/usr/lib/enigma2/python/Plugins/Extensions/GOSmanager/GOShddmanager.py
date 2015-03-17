# -*- coding: utf-8 -*-
# @j00zek 2104 dla Graterlia
#
from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Label import Label
from Components.MenuList import MenuList
from os import popen, system as os_system
from Plugins.Plugin import PluginDescriptor
from GOSconsole import GOSconsole
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.LanguageGOS import gosgettext as _

###########################################################
def ReadMounts():
    try:
        with open("/proc/mounts", "r") as f:
            result = [line.strip().split(' ') for line in f]
            for item in result:
                item[1] = item[1].replace('\\040', ' ')
            f.close()
    except IOError, ex:
        print "Failed to open /proc/mounts", ex
        result = ""
    return result

def isPARTITIONmounted(partition = ""):
    #print partition
    if partition != "":
        for line in ReadMounts():
            print line[0]
            if line[0].find(partition) > 0:
                return True
    return False

def isFOLDERmounted(folder = ""):
    if folder != "":
        for line in ReadMounts():
            if line[1] == folder:
                return line[0]
    return ""

def GetPartitions( UnmountedOnly = False ):
    devices = []
    try:
        with open("/proc/partitions", "r") as f:
            for line in f.readlines():
                parts = line.strip().split()
                if parts and parts[3][-4:-2] == "sd":
                    if UnmountedOnly == True and isPARTITIONmounted(parts[3]) == True:
                        continue
                    size = int(parts[2])
                    if (size / 1024 / 1024) > 1:
                        des = str(size / 1024 / 1024) + "GB)"
                    else:
                        des = str(size / 1024) + "MB)"
                    devices.append(parts[3] + " (" + des)
            f.close()
    except IOError, ex:
        print "Failed to open /proc/partitions", ex
    return devices 

def GetDevices():
    devices = []
    try:
        with open("/proc/partitions", "r") as f:
            for line in f.readlines():
                parts = line.strip().split()
                if parts and parts[3][-3:-1] == "sd":
                    size = int(parts[2])
                    if (size / 1024 / 1024) > 1:
                        des = str(size / 1024 / 1024) + "GB"
                    else:
                        des = str(size / 1024) + "MB"
                    devices.append( (parts[3] + " " + des , parts[3] , size) )
            f.close()
    except IOError, ex:
        print "Failed to open /proc/partitions", ex
    return devices 

def isEXT(partition = ""):    
    if partition != "":
        try:
            blkids=popen("blkid -c /dev/null -w /dev/null | grep '/dev/%s' | grep 'TYPE=.ext'" % partition)
            for blkid in blkids.readlines():
                if blkid.find(partition) >0:
                    return True
        except:
            pass
    return False
    
def isRECORDS():    
    try:
        blkids=popen(" blkid -c /dev/null -w /dev/null | grep 'LABEL=.records' | cut -d ' ' -f1-2")
        for blkid in blkids.readlines():
            if blkid.find('LABEL="records"') > 0:
                dev=blkid.split(":")
                if len(dev) == 2:
                    return dev[0].replace("/dev/","")
    except:
        pass
    return ""
    
###########################################################
class GOShddmanager(Screen):
    skin = """
    <screen position="center,center" size="420,180" title="GOShddmanager" >
        <widget name="list" position="0,0" size="420,180" scrollbarMode="showOnDemand" />
    </screen>"""

    def __init__(self, session, args=None):
        Screen.__init__(self, session)
        self.session = session
        
        self.list = []
        if isFOLDERmounted("/hdd") == "":
            self.list.append( (_("Set mounting of /hdd directory") , "mountONhdd") )
        else:
            self.list.append( (_("Change mounting of /hdd from %s") % isFOLDERmounted("/hdd") , "mountONhdd") )
        self.list.append( (_("Mount/umount partition temporarly"), "ADHOCmount") )
        self.list.append( (_("Filesystem checking"), "doFSCheck") )
        self.list.append( (_("Format partition"), "doFormat") )
        self.list.append( (_("Make partitions"), "makePartitions") )
        
        self["list"] = MenuList(self.list)
        
        self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.run, "cancel": self.close}, -1)
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(_("HDD/PEN manager"))

    def run(self):
        myIDX = self["list"].getSelectedIndex()
        if myIDX is not None:
            opcja = self.list[myIDX][1]
            if opcja == "mountONhdd":
                self.session.openWithCallback(self.endrun,mountONhdd)
            elif opcja == "ADHOCmount":
                self.session.openWithCallback(self.endrun,ADHOCmount)
            elif opcja == "doFSCheck":
                self.session.openWithCallback(self.endrun,doFSCheck)
            elif opcja == "doFormat":
                self.session.openWithCallback(self.endrun,doFormat)
            elif opcja == "makePartitions":
                self.session.openWithCallback(self.endrun,makePartitions)
            else:
                print "Nieznana opcja: %s" % opcja

    def endrun(self):
        return
    
##############################################################

class mountONhdd(Screen, ConfigListScreen):

    skin = """
    <screen name="mountONhdd" position="center,center" size="260,90" title="mountONhdd" >

            <widget name="config" position="10,10" size="240,30" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />
            <widget name="key_green" position="0,40" zPosition="2" size="100,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="green" />
            <widget name="key_red" position="160,40" zPosition="2" size="100,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="red" />

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
            }, -2)

        self["key_green"] = Label("Ustaw")
        self["key_red"] = Label(_("Cancel"))

        self.runSetup()
        self.onLayoutFinish.append(self.layoutFinished)

    def runSetup(self):

        config.GOShddmanager = ConfigSubsection()
        config.GOShddmanager.partitions = NoSave(ConfigSelection( choices = GetPartitions() ))

        self.list.append(getConfigListEntry(_("on partition:"), config.GOShddmanager.partitions))

        self["config"].list = self.list
        self["config"].setList(self.list)

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
        
    def keyLeft(self):
        ConfigListScreen.keyLeft(self)

    def keyRight(self):
        ConfigListScreen.keyRight(self)

    def layoutFinished(self):
        self.setTitle(_("Permanent /hdd mount ..."))

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()
    
    def keySave(self): #openpliPC - F2 emuluje green
        tytul = config.GOShddmanager.partitions.value
        partycja = tytul.split(' ')[0]
        self.session.openWithCallback(self.dorun, MessageBox,_("Do you confirm %s should be mounted on /hdd?") % partycja ,  type = MessageBox.TYPE_YESNO)
            
    def dorun(self, ret):
        if ret == True:
            tytul = config.GOShddmanager.partitions.value
            partycja = tytul.split(' ')[0]
            cmds = []
            maxWhile = 5
            while isFOLDERmounted("/hdd") != "" or maxWhile == 0 :
                print "GOSmanager>isFOLDERmounted(/hdd)='%s'" % isFOLDERmounted("/hdd")
                os_system('umount /hdd')
                maxWhile -= 1
            print "GOSmanager>isFOLDERmounted(/media/hdd)='%s'" % isFOLDERmounted("/media/hdd")
            if isFOLDERmounted("/media/hdd") != "":
                os_system('umount /media/hdd')
            print "GOSmanager>isRECORDS='%s'" % isRECORDS()
            if isRECORDS() != "" and isRECORDS() != partycja:
                os_system('tune2fs -L %s /dev/%s' % (isRECORDS() ,isRECORDS()) )
            os_system('mount /dev/%s /hdd' % (partycja))
            from Components.Console import Console
            myConsole = Console()
            myConsole.ePopen('tune2fs -L records /dev/%s' % partycja, self.middlerun() )
            #self.session.openWithCallback(self.endrun ,GOSconsole, title = "Montuję /dev/%s na %s" % (partycja, folder), cmdlist = [ ('mount /dev/%s %s' % (partycja,folder)) ])

    def middlerun(self, ret = 0):
        tytul = config.GOShddmanager.partitions.value
        partycja = tytul.split(' ')[0]
        if isPARTITIONmounted(partycja) == True:
            self.session.openWithCallback(self.endrun, MessageBox,_("%s mounted properly") % partycja,  type = MessageBox.TYPE_INFO)
        else:
            self.session.openWithCallback(self.endrun, MessageBox,_("Error mounting partition, restart tuner to apply changes."),  type = MessageBox.TYPE_INFO)
    
    def endrun(self, ret =0):
        return

##############################################################

class ADHOCmount(Screen, ConfigListScreen):

    skin = """
    <screen name="ADHOCmount" position="center,center" size="260,110" title="ADHOCmount" >

            <widget name="config" position="10,10" size="240,60" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />
            <widget name="key_green" position="0,70" zPosition="2" size="100,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="green" />
            <widget name="key_red" position="160,70" zPosition="2" size="100,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="red" />

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
                "ok": self.keyOK,
                "red": self.keyCancel,
            }, -2)

        self["key_green"] = Label("Zamontuj")
        self["key_red"] = Label(_("Cancel"))

        self.runSetup()
        self.onLayoutFinish.append(self.layoutFinished)

    def runSetup(self):

        config.GOShddmanager = ConfigSubsection()
        config.GOShddmanager.folders = NoSave(ConfigDirectory(default = "/mnt/usb/"))
        config.GOShddmanager.partitions = NoSave(ConfigSelection( choices = GetPartitions() ))

        self.list.append(getConfigListEntry(_("directory:"), config.GOShddmanager.folders))
        self.list.append(getConfigListEntry(_("on partition:"), config.GOShddmanager.partitions))

        self["config"].list = self.list
        self["config"].setList(self.list)

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
        
    def keyLeft(self):
        ConfigListScreen.keyLeft(self)

    def keyRight(self):
        ConfigListScreen.keyRight(self)

    def layoutFinished(self):
        self.setTitle(_("Mount ..."))

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()
    
    def keySave(self): #openpliPC - F2 emuluje green
        tytul = config.GOShddmanager.partitions.value
        folder = config.GOShddmanager.folders.value
        partycja = tytul.split(' ')[0]
        self.session.openWithCallback(self.dorun, MessageBox,_("Mount %s on %s?") % (partycja, folder) ,  type = MessageBox.TYPE_YESNO)
            
    def dorun(self, ret):
        if ret == True:
            tytul = config.GOShddmanager.partitions.value
            partycja = tytul.split(' ')[0]
            folder = config.GOShddmanager.folders.value
            from Components.Console import Console
            myConsole = Console()
            myConsole.ePopen('mount /dev/%s %s' % (partycja,folder), self.middlerun() )
            #self.session.openWithCallback(self.endrun ,GOSconsole, title = "Montuję /dev/%s na %s" % (partycja, folder), cmdlist = [ ('mount /dev/%s %s' % (partycja,folder)) ])

    def middlerun(self, ret = 0):
        tytul = config.GOShddmanager.partitions.value
        partycja = tytul.split(' ')[0]
        folder = config.GOShddmanager.folders.value
        if isPARTITIONmounted(partycja):
            self.session.openWithCallback(self.endrun, MessageBox,_("Mounted successfully"),  type = MessageBox.TYPE_INFO)
        else:
            self.session.openWithCallback(self.endrun, MessageBox,_("Error mounting partition"),  type = MessageBox.TYPE_INFO)
    
    def endrun(self, ret =0):
        return

    def keyOK(self):
        curIndex = self["config"].getCurrentIndex()
        currItem = self["config"].list[curIndex][1]
        if isinstance(currItem, ConfigDirectory):
            def SetDirPathCallBack(curIndex, newPath):
                if None != newPath: self["config"].list[curIndex][1].value = newPath
            from filebrowserwidget import DirectorySelectorWidget
            from Tools.BoundFunction import boundFunction
            self.session.openWithCallback(boundFunction(SetDirPathCallBack, curIndex), DirectorySelectorWidget, currDir=currItem.value, title=_("Select directory"))

##############################################################

class doFSCheck(Screen, ConfigListScreen):

    skin = """
    <screen name="doFSCheck" position="center,center" size="260,90" title="doFSCheck" >

            <widget name="config" position="10,10" size="240,30" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />
            <widget name="key_green" position="0,40" zPosition="2" size="100,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="green" />
            <widget name="key_red" position="160,40" zPosition="2" size="100,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="red" />

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
            }, -2)

        self["key_green"] = Label("Wykonaj")
        self["key_red"] = Label(_("Cancel"))

        self.runSetup()
        self.onLayoutFinish.append(self.layoutFinished)

    def runSetup(self):

        config.GOShddmanager = ConfigSubsection()
        config.GOShddmanager.partitions = NoSave(ConfigSelection( choices = GetPartitions( UnmountedOnly = True ) ))

        self.list.append(getConfigListEntry(_("partition:"), config.GOShddmanager.partitions))

        self["config"].list = self.list
        self["config"].setList(self.list)

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
        
    def keyLeft(self):
        ConfigListScreen.keyLeft(self)

    def keyRight(self):
        ConfigListScreen.keyRight(self)

    def layoutFinished(self):
        self.setTitle(_("Checking partition"))

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()
    
    def keySave(self): #openpliPC - F2 emuluje green
        tytul = config.GOShddmanager.partitions.value
        partycja = tytul.split(' ')[0]
        if isEXT(partycja) == True:
            self.session.openWithCallback(self.endrun ,GOSconsole, title = _("Checking /dev/%s") % tytul, cmdlist = [ ('e2fsck -pfv /dev/%s' % partycja) ])
        else:
            self.session.openWithCallback(self.endrun, MessageBox,_("Only ext[2|3|4] partitions can be checked."),  type = MessageBox.TYPE_INFO)
            
    def dorun(self):
        self.close()

    def endrun(self, ret =0):
        return
##############################################################

class doFormat(Screen, ConfigListScreen):

    skin = """
    <screen name="doFormat" position="center,center" size="260,110" title="doFormat" >

            <widget name="config" position="10,10" size="240,60" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />
            <widget name="key_green" position="0,70" zPosition="2" size="100,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="green" />
            <widget name="key_red" position="160,70" zPosition="2" size="100,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="red" />

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
            }, -2)

        self["key_green"] = Label(_("Run"))
        self["key_red"] = Label(_("Cancel"))

        self.runSetup()
        self.onLayoutFinish.append(self.layoutFinished)

    def runSetup(self):

        config.GOShddmanager = ConfigSubsection()
        config.GOShddmanager.partitions = NoSave(ConfigSelection( choices = GetPartitions( UnmountedOnly = True ) ))
        config.GOShddmanager.FormatTypes = NoSave(ConfigSelection(default = "ext3", choices = [("ext2", "ext2"), ("ext3", "ext3"), ("ext4", "ext4")]))

        self.list.append(getConfigListEntry(_("partition:"), config.GOShddmanager.partitions))
        self.list.append(getConfigListEntry(_("on system:"), config.GOShddmanager.FormatTypes))

        self["config"].list = self.list
        self["config"].setList(self.list)

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
        
    def keyLeft(self):
        ConfigListScreen.keyLeft(self)

    def keyRight(self):
        ConfigListScreen.keyRight(self)

    def layoutFinished(self):
        self.setTitle(_("Format ..."))

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()
    
    def keySave(self): #openpliPC - F2 emuluje green
        tytul = config.GOShddmanager.partitions.value
        self.session.openWithCallback(self.dorun, MessageBox,_("Do you want to format %s partition?") % tytul ,  type = MessageBox.TYPE_YESNO)
            
    def dorun(self, ret):
        if ret == True:
            tytul = config.GOShddmanager.partitions.value
            partycja = tytul.split(' ')[0]
            typ = config.GOShddmanager.FormatTypes.value
            self.session.openWithCallback(self.endrun ,GOSconsole, title = _("Formatting /dev/%s as %s") % (tytul, typ), cmdlist = [ ('mkfs.%s /dev/%s' % (typ,partycja)) ])

    def endrun(self, ret =0):
        return
##############################################################

class makePartitions(Screen, ConfigListScreen):

    skin = """
    <screen name="makePartitions" position="center,center" size="260,220" title="makePartitions" >

            <widget name="config" position="10,10" size="240,160" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />
            <widget name="key_green" position="0,170" zPosition="2" size="100,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="green" />
            <widget name="key_red" position="160,170" zPosition="2" size="100,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="red" />

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
            }, -2)

        self["key_green"] = Label(_("Run"))
        self["key_red"] = Label(_("Cancel"))

        config.GOShddmanager = ConfigSubsection()
        config.GOShddmanager.drives = NoSave(ConfigSelection( choices = GetDevices() ))
        config.GOShddmanager.numberPartitions = NoSave(ConfigSelection(default = 1, choices = [(1, "1"), (2, "2"), (3, "3"), (4, "4")]))
        config.GOShddmanager.Partycja1size = NoSave(ConfigSelection(default = "+512M", choices = [("+128M", "128MB"), ("+256M", "256MB"), ("+384M", "384MB"), ("+512M", "512MB"), ("+1G", "1GB"), ("+2G", "2GB"), (" ", _("all free"))]))
        config.GOShddmanager.Partycja2size = NoSave(ConfigSelection(default = "+512M", choices = [("+128M", "128MB"), ("+256M", "256MB"), ("+384M", "384MB"), ("+512M", "512MB"), ("+1G", "1GB"), ("+2G", "2GB"), (" ", _("all free"))]))
        config.GOShddmanager.Partycja3size = NoSave(ConfigSelection(default = "+512M", choices = [("+128M", "128MB"), ("+256M", "256MB"), ("+384M", "384MB"), ("+512M", "512MB"), ("+1G", "1GB"), ("+2G", "2GB"), (" ", _("all free"))]))
        config.GOShddmanager.Partycja4size = NoSave(ConfigSelection(default = " ", choices = [("+128M", "128MB"), ("+256M", "256MB"), ("+384M", "384MB"), ("+512M", "512MB"), ("+1G", "1GB"), ("+2G", "2GB"), (" ", _("all free"))]))

        self.runSetup()
        self.onLayoutFinish.append(self.layoutFinished)

    def runSetup(self):


        self.list = [ getConfigListEntry(_("Medium:"), config.GOShddmanager.drives) ]
        self.list.append(getConfigListEntry(_("Partitions number:"), config.GOShddmanager.numberPartitions))
        if config.GOShddmanager.numberPartitions.value == 1:
            config.GOShddmanager.Partycja1size.value = "0"
        self.list.append(getConfigListEntry(_("Partition 1 size:"), config.GOShddmanager.Partycja1size))
        if config.GOShddmanager.numberPartitions.value >=2:
            self.list.append(getConfigListEntry(_("Partition 2 size:"), config.GOShddmanager.Partycja2size))
        if config.GOShddmanager.numberPartitions.value >=3:
            self.list.append(getConfigListEntry(_("Partition 3 size:"), config.GOShddmanager.Partycja3size))
        if config.GOShddmanager.numberPartitions.value ==4:
            self.list.append(getConfigListEntry(_("Partition 4 size:"), config.GOShddmanager.Partycja4size))

        self["config"].list = self.list
        self["config"].setList(self.list)

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
        
    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        if self["config"].getCurrent()[1] == config.GOShddmanager.numberPartitions:
            self.runSetup()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        if self["config"].getCurrent()[1] == config.GOShddmanager.numberPartitions:
            self.runSetup()

    def layoutFinished(self):
        self.setTitle(_("Make partitions"))

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()
    
    def keySave(self): #openpliPC - F2 emuluje green
        dyski = config.GOShddmanager.drives.value
        self.session.openWithCallback(self.dorun, MessageBox,_("Are you sure to make partitions on %s?") % dyski ,  type = MessageBox.TYPE_YESNO)
            
    def dorun(self, ret):
        if ret == True:
            dyski = config.GOShddmanager.drives.value
            dysk = dyski.split(' ')[0]
            komenda = "(echo o"
            komenda += "; echo n; echo p; echo 1; echo; echo %s" % config.GOShddmanager.Partycja1size.value
            if config.GOShddmanager.numberPartitions.value >= 2:
                komenda += "; echo n; echo p; echo 2; echo; echo %s" % config.GOShddmanager.Partycja2size.value
            if config.GOShddmanager.numberPartitions.value >= 3:
                komenda += "; echo n; echo p; echo 3; echo; echo %s" % config.GOShddmanager.Partycja3size.value
            if config.GOShddmanager.numberPartitions.value == 4:
                komenda += "; echo n; echo p; echo 4; echo; echo %s" % config.GOShddmanager.Partycja4size.value
            komenda += ";echo w) | fdisk /dev/%s" %dysk
            #(echo o; echo n; echo p; echo 1; echo ; echo; echo w) | sudo fdisk
            #print komenda
            self.session.openWithCallback(self.endrun ,GOSconsole, title = _("Making partitions on /dev/%s") % dyski, cmdlist = [ komenda ])

    def endrun(self, ret =0):
        return
