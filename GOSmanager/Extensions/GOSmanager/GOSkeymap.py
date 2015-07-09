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
from os import symlink as os_symlink, remove as os_remove, fsync as os_fsync, rename as os_rename, walk as os_walk, listdir
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.HardwareInfo import HardwareInfo
from Tools.Directories import fileExists, resolveFilename, pathExists, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE
import xml.etree.cElementTree as ET
from Components.LanguageGOS import gosgettext as _

KEYMAPsettings_list = [ ]
################## Zmienne GOS #########################################################
# config.KEYMAPsettings.<NAZWA-ZMIENNEJ> = NoSave(ConfigSelection(default = "0", choices = [("0", "wł"), ("off", "wył")]))
# KEYMAPsettings_list.append((config.KEYMAPsettings.<NAZWA-ZMIENNEJ>,"<NAZWA-ZMIENNEJ>","CONFIG"))
#
# Stała "CONFIG" definiuje parametr zapisywany w /etc/sysctl.gos
# default = "0" oznacza, że wartość domyślna nie będzie zapisywana,w przypadku innej wartości należy poprawić

config.KEYMAPsettings = ConfigSubsection()
config.KEYMAPsettings.separator = NoSave(ConfigNothing())

########## chwilowe dane do wyboru keymap-y
MyKeymap = []
myDir=eEnv.resolve("${datadir}/enigma2/")
for file in listdir(myDir):
    if file.startswith("keymap") and file.endswith(".xml"):
        #print os_path.join(myDir, file)
        MyKeymap.append( ( os_path.join(myDir, file), file ) )
config.KEYMAPsettings.keymap = NoSave(ConfigSelection(default = config.usage.keymap.value, choices = MyKeymap))
KEYMAPsettings_list.append((config.KEYMAPsettings.keymap,"oPLIkeymap","DEF"))
##############################################################
config.KEYMAPsettings.keymap_KEY_PAGEUP = NoSave(ConfigSelection(default = "keyChannelUp", choices = [("keyChannelUp", _("previous marker")), ("keyLeft", _("key left action"))]))
config.KEYMAPsettings.keymap_KEY_PAGEDOWN = NoSave(ConfigSelection(default = "keyChannelDown", choices = [("keyChannelDown", _("next marker")), ("keyRight", _("key right action"))]))
from keys import standbyKeys
standbyKeys.sort()
config.KEYMAPsettings.keymap_TO_standby_KEY = NoSave(ConfigSelection(default = "KEY_POWER", choices = standbyKeys ))
config.KEYMAPsettings.keymap_FROM_standby_KEY = NoSave(ConfigSelection(default = "KEY_POWER", choices = standbyKeys ))

##############################################################


class GOSkeymapMenu(Screen, ConfigListScreen):

    skin = """
    <screen name="GOSkeymapMenu" position="center,center" size="640,440" title="GOSkeymapMenu" >

            <widget name="config" position="10,10" size="620,390" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />
            <widget name="key_red"    position="0,405" zPosition="2" size="160,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="red" />
            <widget name="key_green"  position="160,405" zPosition="2" size="160,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="green" />
            <widget name="key_yellow" position="320,405" zPosition="2" size="160,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="yellow" />
            <widget name="key_blue"   position="480,405" zPosition="2" size="160,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="blue" />

    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)

        self.list = [ ]
        self.XMLKeymaps = []

        self.onChangedEntry = [ ]
        ConfigListScreen.__init__(self, self.list, session = session, on_change = self.changedEntry)
        self.setup_title = _("Keymap configurator")
        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "cancel": self.keyCancel,
                "green": self.keySave,
                "ok": self.keySave,
                "red": self.keyCancel,
                "blue": self.keyBlue,
                "yellow": self.LoadXML,
            }, -2)

        self["key_green"] = Label(_("Save"))
        self["key_red"] = Label(_("Cancel"))
        self["key_yellow"] = Label(_("Read"))
        self["key_blue"] = Label(_("Make backup"))

        self.myDir=eEnv.resolve("${datadir}/enigma2/")

        self.myConsole = Console()

        self.onLayoutFinish.append(self.layoutFinished)

    def runSetup(self):
        self.list = [ getConfigListEntry(_("Active keymap:"), config.KEYMAPsettings.keymap) ]# zapisywane w settings
        self.list.append(getConfigListEntry(" ", config.KEYMAPsettings.separator))

        self.list.append(getConfigListEntry(_("--- Channels List ---"), config.KEYMAPsettings.separator))
        
        #self.XMLKeymaps.append(
        config.KEYMAPsettings.keymap_KEY_PAGEUP.value = self.getElement( "ChannelSelectBaseActions" , 'id','KEY_PAGEUP', 'flags','m', 'mapto')
        self.list.append(getConfigListEntry(_("Key P+:"), config.KEYMAPsettings.keymap_KEY_PAGEUP))
        
        config.KEYMAPsettings.keymap_KEY_PAGEDOWN.value = self.getElement( "ChannelSelectBaseActions" , 'id','KEY_PAGEDOWN', 'flags','m', 'mapto')
        self.list.append(getConfigListEntry(_("Key P-:"), config.KEYMAPsettings.keymap_KEY_PAGEDOWN))
        
        self.list.append(getConfigListEntry(" ", config.KEYMAPsettings.separator))
        self.list.append(getConfigListEntry(_("--- Standby/Wake up ---"), config.KEYMAPsettings.separator))
        
        # isElement( context        , ParamNname1, paramValue1 , paramName2 , paramValue2 ):
	    # getElement(context , ParamNname1, paramValue1 , paramName2 , paramValue2 , returnParam )
        
        ##### przejscie w standby - to działa jakoś dziwnie
        #if self.isElement("GlobalActions" , 'mapto' , 'power_down', 'flags' , 'm'):
        #    config.KEYMAPsettings.keymap_TO_standby_KEY.value = self.getElement("GlobalActions",'mapto','power_down', 'flags' , 'm', 'id')
        #elif self.isElement("GlobalActions" , 'mapto' , 'power_long', 'flags' , 'l'):
        #    config.KEYMAPsettings.keymap_TO_standby_KEY.value = self.getElement( "GlobalActions",'mapto','power_long','flags' , 'l', 'id')
        #elif self.isElement("GlobalActions" , 'mapto' , 'power_long', 'flags' , 'm'):
        #    config.KEYMAPsettings.keymap_TO_standby_KEY.value = self.getElement( "GlobalActions",'mapto','power_long','flags' , 'm', 'id')
        #self.list.append(getConfigListEntry("Uśpienie klawiszem:", config.KEYMAPsettings.keymap_TO_standby_KEY))
        
        ##### budzenie ze standby
        if self.isElement( "StandbyActions",'mapto','power','flags' , 'm'):
            config.KEYMAPsettings.keymap_FROM_standby_KEY.value = self.getElement( "StandbyActions",'mapto','power','flags' , 'm', 'id')
            self.list.append(getConfigListEntry(_("Wake up with key:"), config.KEYMAPsettings.keymap_FROM_standby_KEY))
        
        self["config"].list = self.list
        self["config"].setList(self.list)
    
    def isElement(self, context , ParamName1, paramValue1 , paramName2 , paramValue2 ):
        #pobieramy elementy struktury dokumentu XML
        if paramName2 == '' and paramValue2 == '':
            znaleziono = len(self.root.findall('./map[@context="%s"]/key[@%s="%s"]' % (context,ParamName1,paramValue1)))
        else:
            znaleziono = len(self.root.findall('./map[@context="%s"]/key[@%s="%s"][@%s="%s"]' % (context,ParamName1,paramValue1,paramName2,paramValue2)))
        print "[GOSkeymap] isElement= %s" % znaleziono
        return znaleziono

    def getElement(self, context , ParamName1, paramValue1 , paramName2 , paramValue2 , returnParam ):
        #pobieramy elementy struktury dokumentu XML
        myElement = self.root.findall('./map[@context="%s"]/key[@%s="%s"][@%s="%s"]' % (context,ParamName1,paramValue1,paramName2,paramValue2))
        if myElement:
            print myElement[0].attrib[returnParam]
            return myElement[0].attrib[returnParam]
        else:
            print "Nie znaleziono"
            return ''

    def setElement(self, context , ParamName1, paramValue1 , paramName2 , paramValue2 , setParam , setValue ):
        #pobieramy elementy struktury dokumentu XML
        myElement = self.root.findall('./map[@context="%s"]/key[@%s="%s"][@%s="%s"]' % (context,ParamName1,paramValue1,paramName2,paramValue2))
        if myElement:
            myElement[0].attrib[setParam] = setValue
        else:
            print "ERROR setting parameter!!!"

    def removeElement(self, context , ParamName1, paramValue1 , paramName2 , paramValue2):
        #pobieramy elementy struktury dokumentu XML
        for keymap in self.root:
            if keymap.attrib['context'] == context:
                for key in keymap:
                    print key.attrib
                    if ParamName1 in key.attrib and paramName2 == '' and paramValue2 == '':
                        if key.attrib[ParamName1] == paramValue1:
                            keymap.remove(key)
                    elif ParamName1 in key.attrib and paramName2 in key.attrib:
                        if key.attrib[ParamName1] == paramValue1 and key.attrib[paramName2] == paramValue2:
                            keymap.remove(key)
                break
                  
    def keySave(self):
        for x in self["config"].list:
            for GOSsetting in KEYMAPsettings_list:
                if GOSsetting[0] == x[1]:
                    opcja = GOSsetting[1]
                    wartosc = x[1].getValue()
                    if GOSsetting[2] == "CONFIG": # do konfiguracji, tylko konfiguracje
                        if str(wartosc) not in ["0" , "lircd.conf"]: # tu ewentualnie dopisac, jakie zmienne są defaultowe
                            myContent += str(opcja) + '=' + str(wartosc) + '\n'
                    elif GOSsetting[2] == "DEF": # musimy zalatwic procedurą
                        print str(opcja)
                        #ustawienie keymapy
                        if str(opcja) == "oPLIkeymap":
                            if fileExists(config.KEYMAPsettings.keymap.value):
                                config.usage.keymap.value = config.KEYMAPsettings.keymap.value
                                config.usage.keymap.save()
                                
            x[1].save()
        configfile.save()
        #zapis xml
        if len(self.onChangedEntry) > 0:
            self.modifyXML()
            with open(config.usage.keymap.value, 'wb') as myFile:
                myFile.write(ET.tostring(self.root))
                self.session.openWithCallback(self.keySaveEnd, MessageBox,_("OpenPLI has to be restarted after changes in keymap.\nRestart now?"),  type = MessageBox.TYPE_YESNO)
        else:
            self.close()
        
    def keySaveEnd(self, ret):
        if ret == True:
            from enigma import quitMainloop
            quitMainloop(3)
        else:
            self.close()
    
    def modifyXML(self):
        for currentSetting in self.onChangedEntry:
            if currentSetting == config.KEYMAPsettings.keymap_KEY_PAGEUP:
                #setElement    ( context ,       ParamNname1, paramValue1, paramName2 , paramValue2 , setParam , setValue )
                self.setElement("ChannelSelectBaseActions",'id','KEY_PAGEUP', 'flags','m', 'mapto' ,config.KEYMAPsettings.keymap_KEY_PAGEUP.value)
            elif currentSetting == config.KEYMAPsettings.keymap_KEY_PAGEDOWN:
                self.setElement( "ChannelSelectBaseActions" , 'id','KEY_PAGEDOWN', 'flags','m', 'mapto' , config.KEYMAPsettings.keymap_KEY_PAGEDOWN.value)
            
            ##### przejscie w standby
            elif currentSetting == config.KEYMAPsettings.keymap_TO_standby_KEY:
                #removeElement(self, context , ParamName1, paramValue1 , paramName2 , paramValue2)
                if config.KEYMAPsettings.keymap_TO_standby_KEY.value == 'KEY_MUTE':
                    if self.isElement("GlobalActions" , 'id' , 'KEY_MUTE', 'mapto' , 'volumeMute'):
                        self.removeElement("GlobalActions" , 'id' , 'KEY_MUTE', 'mapto' , 'volumeMute')
                if self.isElement("GlobalActions" , 'mapto' , 'power_down', 'flags' , 'm'):
                    self.setElement( "GlobalActions" , 'mapto' , 'power_down', 'flags','m', 'id' , config.KEYMAPsettings.keymap_TO_standby_KEY.value)
            
                if config.KEYMAPsettings.keymap_TO_standby_KEY.value != 'KEY_POWER':
                    if self.isElement("GlobalActions" , 'mapto' , 'power_long', 'flags' , 'l'):
                        self.removeElement( "GlobalActions" , 'mapto','power_long', 'flags','l')
                else:
                    if self.isElement("GlobalActions" , 'mapto' , 'power_long', 'flags' , 'l'):
                        self.setElement( "GlobalActions" , 'mapto','power_long', 'flags','l', 'id' , config.KEYMAPsettings.keymap_TO_standby_KEY.value)
                    if self.isElement("GlobalActions" , 'mapto' , 'power_long', 'flags' , 'm'):
                        self.setElement( "GlobalActions" , 'mapto','power_long', 'flags','m', 'id' , config.KEYMAPsettings.keymap_TO_standby_KEY.value)
            
            ##### budzenie ze standby
            elif currentSetting == config.KEYMAPsettings.keymap_FROM_standby_KEY:
                self.setElement( "StandbyActions",'mapto','power','flags' , 'm', 'id', config.KEYMAPsettings.keymap_FROM_standby_KEY.value)

    def LoadXML(self):
        if pathExists(config.usage.keymap.value) is True:
            self.root = ET.parse(config.usage.keymap.value).getroot()

    def reloadKeymap(self):
        if self["config"].getCurrent()[1] == config.KEYMAPsettings.keymap:  
                config.usage.keymap.value = config.KEYMAPsettings.keymap.value
                config.usage.keymap.save()
                self.LoadXML()
                self.runSetup()
      
    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.reloadKeymap()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.reloadKeymap()

    def keyBlue(self):
        self.myConsole.ePopen('cp -rf %s %s.bkp' % (config.KEYMAPsettings.keymap.value , config.KEYMAPsettings.keymap.value ) )
        
    def changedEntry(self):
        if self["config"].getCurrent()[1] not in self.onChangedEntry:
            self.onChangedEntry.append(self["config"].getCurrent()[1])
        
    def layoutFinished(self):
        self.LoadXML()
        self.runSetup()

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()
