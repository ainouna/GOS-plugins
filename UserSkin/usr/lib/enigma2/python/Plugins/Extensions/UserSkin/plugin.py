# -*- coding: utf-8 -*-

# UserSkin, formerly AtileHD
#
# maintainer: <schomi@vuplus-support.org> / <plnick@vuplus-support.org>
#
# extension for all skins and openpli @j00zek 2014/2015

#This plugin is free software, you are allowed to
#modify it (if you keep the license),
#but you are not allowed to distribute/publish
#it without source code (this version and your modifications).
#This means you also have to distribute
#source code of your modifications.

from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.LanguageGOS import gosgettext as _
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Tools.Directories import *
from Tools.HardwareInfo import HardwareInfo 
from Tools.LoadPixmap import LoadPixmap
from Tools import Notifications
#system imports
from os import listdir, remove, rename, system, path, symlink, chdir
import shutil
import re

# Atile/UserSkin
config.plugins.UserSkin = ConfigSubsection()
config.plugins.UserSkin.refreshInterval = ConfigNumber(default=30) #in minutes
config.plugins.UserSkin.woeid = ConfigNumber(default=523920) #Location Warsaw (visit weather.yahoo.com)
config.plugins.UserSkin.tempUnit = ConfigSelection(default="Celsius", choices = [
                ("Celsius", _("Celsius")),
                ("Fahrenheit", _("Fahrenheit"))
                ])
config.plugins.UserSkin.PIG_active = ConfigYesNo(default=True)
        
def Plugins(**kwargs):
    return [PluginDescriptor(name=_("UserSkin Setup"), description=_("Personalize your Skin"), where = PluginDescriptor.WHERE_MENU, icon="plugin.png", fnc=menu)]

def menu(menuid, **kwargs):
    if menuid == "vtimain" or menuid == "system":
        return [(_("Setup - UserSkin"), main, "UserSkin_setup", 40)]
    return []

def main(session, **kwargs):
    print "[UserSkin]: Config ..."
    session.open(UserSkin_Config)

class UserSkin_Config(Screen, ConfigListScreen):
    skin = """
  <screen name="UserSkin_Config" position="82,124" size="1101,376" title="UserSkin Setup" backgroundColor="transparent" flags="wfNoBorder">
    <eLabel position="7,2" size="1091,372" zPosition="-15" backgroundColor="#20000000" />
    <eLabel position="4,51" size="664,238" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="672,51" size="410,237" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="6,301" size="240,55" zPosition="-10" backgroundColor="#20b81c46" />
    <eLabel position="284,302" size="240,55" zPosition="-10" backgroundColor="#20009f3c" />
    <eLabel position="564,302" size="240,56" zPosition="-10" backgroundColor="#209ca81b" />
    <eLabel position="843,301" size="240,55" zPosition="-10" backgroundColor="#202673ec" />
    <widget source="Title" render="Label" position="2,4" size="889,43" font="Regular;35" foregroundColor="#00ffffff" backgroundColor="#004e4e4e" transparent="1" />
    <widget name="config" position="6,55" size="657,226" scrollbarMode="showOnDemand" transparent="1" />
    <widget name="Picture" position="676,56" size="400,225" alphatest="on" />
    <widget name="key_red" position="18,316" size="210,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20b81c46" transparent="1" />
    <widget name="key_green" position="299,317" size="210,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20009f3c" transparent="1" />
    <widget name="key_yellow" position="578,317" size="210,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#209ca81b" transparent="1" />
    <widget name="key_blue" position="854,318" size="210,25" zPosition="0" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#202673ec" transparent="1" />
  </screen>
"""

    def __init__(self, session, args = 0):
        self.session = session
        self.skin_lines = []
        self.changed_screens = False
        Screen.__init__(self, session)
        
        self.skin_base_dir = resolveFilename(SCOPE_SKIN, config.skin.primary_skin.value.replace('skin.xml', ''))
        if not self.skin_base_dir.endswith('/'):
            self.skin_base_dir = self.skin_base_dir + '/'
        print "[UserSkin] self.skin_base_dir=%s, skin=%s" % (self.skin_base_dir, config.skin.primary_skin.value)
        self.currentSkin = config.skin.primary_skin.value.replace('skin.xml', '').replace('/', '')
        if self.currentSkin != '':
                self.currentSkin = '_' + self.currentSkin # default_skin = '', others '_skinname', used later

        self.default_font_file = _("using standard fonts")
        self.default_color_file = _("using standard colors")
        
        if path.exists(self.skin_base_dir):
            if path.exists(self.skin_base_dir + "allFonts/font_atile_Roboto.xml"):
                self.default_font_file = "font_atile_Roboto.xml"
            if not path.exists(self.skin_base_dir + "allFonts/"):
                mkdir(self.skin_base_dir + "allFonts/")

            if path.exists(self.skin_base_dir + "allColors/colors_atile_Grey_transparent.xml"):
                self.default_color_file = "colors_atile_Grey_transparent.xml"
            if not path.exists(self.skin_base_dir + "allColors/"):
                mkdir(self.skin_base_dir + "allColors/")
          
        self.color_file = "skin_user_colors.xml"
        self.font_file = "skin_user_header.xml"
        current_color = self.getCurrentColor()[0]
        current_font = self.getCurrentFont()[0]
        myUserSkin_active = self.getmyAtileState()
        self.myUserSkin_active = NoSave(ConfigYesNo(default=myUserSkin_active))
        self.myTuner = HardwareInfo().get_device_name()
        self.myUserSkin_font = NoSave(ConfigSelection(default=current_font, choices = self.getPossibleFont()))
        self.myUserSkin_style = NoSave(ConfigSelection(default=current_color, choices = self.getPossibleColor()))
        self.myUserSkin_fake_entry = NoSave(ConfigNothing())
        self.BrakPlikuInfo = ''
        
        self.list = []
        ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)

        self["key_red"] = Label(_("Cancel"))
        self["key_green"] = Label(_("OK"))
        self["key_yellow"] = Label()
        self["key_blue"] = Label(_("About"))
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "green": self.keyOk,
                "red": self.cancel,
                "yellow": self.keyYellow,
                "blue": self.about,
                "cancel": self.cancel,
                "ok": self.keyOk,
            }, -2)
            
        self["Picture"] = Pixmap()
        
        if not self.selectionChanged in self["config"].onSelectionChanged:
            self["config"].onSelectionChanged.append(self.selectionChanged)
        
        self.createConfigList()

    def createConfigList(self):
        self.set_color = getConfigListEntry(_("Style:"), self.myUserSkin_style)
        self.set_font = getConfigListEntry(_("Font:"), self.myUserSkin_font)
        self.set_myatile = getConfigListEntry(_("Enable skin personalization:"), self.myUserSkin_active)
        self.list = []
        self.list.append(self.set_myatile)
        self.list.append(self.set_color)
        self.list.append(self.set_font)
        #if HardwareInfo().get_device_name().lower().find("adb") < 0: # PIG is dangerous in adb boxes
        #    self.list.append(getConfigListEntry(_("Enable PIG (not recommended for 1080p):"), config.plugins.UserSkin.PIG_active))
        self.list.append(getConfigListEntry(_("---Weather---"), self.myUserSkin_fake_entry))
        self.list.append(getConfigListEntry(_("Refresh interval in minutes:"), config.plugins.UserSkin.refreshInterval))
        self.list.append(getConfigListEntry(_("Location # (http://weather.yahoo.com/):"), config.plugins.UserSkin.woeid))
        self.list.append(getConfigListEntry(_("Temperature unit:"), config.plugins.UserSkin.tempUnit))
        self["config"].list = self.list
        self["config"].l.setList(self.list)
        if self.myUserSkin_active.value:
            self["key_yellow"].setText(_("User skins"))
        else:
            self["key_yellow"].setText("")

    def changedEntry(self):
        if self["config"].getCurrent() == self.set_color:
            self.setPicture(self.myUserSkin_style.value)
        elif self["config"].getCurrent() == self.set_font:
            self.setPicture(self.myUserSkin_font.value)
        elif self["config"].getCurrent() == self.set_myatile:
            if self.myUserSkin_active.value:
                self["key_yellow"].setText(_("User skins"))
            else:
                self["key_yellow"].setText("")

    def selectionChanged(self):
        if self["config"].getCurrent() == self.set_color:
            self.setPicture(self.myUserSkin_style.value)
        elif self["config"].getCurrent() == self.set_font:
            self.setPicture(self.myUserSkin_font.value)
        else:
            self["Picture"].hide()

    def cancel(self):
        if self["config"].isChanged():
            self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Don't save settings?"), MessageBox.TYPE_YESNO, default = False)
        else:
            for x in self["config"].list:
                x[1].cancel()
            if self.changed_screens:
                self.restartGUI()
            else:
                self.close()

    def cancelConfirm(self, result):
        if result is None or result is False:
            print "[UserSkin]: Cancel confirmed."
        else:
            print "[UserSkin]: Cancel confirmed. Config changes will be lost."
            for x in self["config"].list:
                x[1].cancel()
            self.close()

    def getPossibleColor(self):
        color_list = []
        if not path.exists(self.skin_base_dir + "allColors/"):
            return color_list
        for f in sorted(listdir(self.skin_base_dir + "allColors/"), key=str.lower):
            if f.endswith('.xml') and f.startswith('colors_'):
                friendly_name = f.replace("colors_atile_", "").replace("colors_", "")
                friendly_name = friendly_name.replace(".xml", "")
                friendly_name = friendly_name.replace("_", " ")
                color_list.append((f, friendly_name))
        return color_list

    def getPossibleFont(self):
        font_list = []
        if not path.exists(self.skin_base_dir + "allFonts/"):
            return font_list
        for f in sorted(listdir(self.skin_base_dir + "allFonts/"), key=str.lower):
            if f.endswith('.xml') and f.startswith('font_'):
                friendly_name = f.replace("font_atile_", "").replace("font_", "")
                friendly_name = friendly_name.replace(".xml", "")
                friendly_name = friendly_name.replace("_", " ")
                font_list.append((f, friendly_name))
        return font_list

    def getmyAtileState(self):
        chdir(self.skin_base_dir)
        if path.exists("mySkin"):
            return True
        else:
            return False

    def getCurrentColor(self):
        myfile = self.skin_base_dir + self.color_file
        if not path.exists(myfile):
            if path.exists(self.skin_base_dir + "allColors/" + self.default_color_file):
                if path.islink(myfile):
                    remove(myfile)
                chdir(self.skin_base_dir)
                symlink("allColors/" + self.default_color_file, self.color_file)
            else:
                return (self.default_color_file, self.default_color_file)
        filename = path.realpath(myfile)
        filename = path.basename(filename)
        friendly_name = filename.replace("colors_atile_", "").replace("colors_", "")
        friendly_name = friendly_name.replace(".xml", "")
        friendly_name = friendly_name.replace("_", " ")
        return (filename, friendly_name)

    def getCurrentFont(self):
        myfile = self.skin_base_dir + self.font_file
        if not path.exists(myfile):
            if path.exists(self.skin_base_dir + "allFonts/" + self.default_font_file):
                if path.islink(myfile):
                    remove(myfile)
                chdir(self.skin_base_dir)
                symlink("allFonts/" + self.default_font_file, self.font_file)
            else:
                return (self.default_font_file, self.default_font_file)
        filename = path.realpath(myfile)
        filename = path.basename(filename)
        friendly_name = filename.replace("font_atile_", "").replace("font_", "")
        friendly_name = friendly_name.replace(".xml", "")
        friendly_name = friendly_name.replace("_", " ")
        return (filename, friendly_name)

    def setPicture(self, f):
        pic = f.replace(".xml", ".png")
        preview = self.skin_base_dir + "preview/"
        if not path.exists(preview):
            mkdir(preview)
        preview = preview + "preview_" + pic
        if path.exists(preview):
            self["Picture"].instance.setPixmapFromFile(preview)
            self["Picture"].show()
        else:
            self["Picture"].hide()

    def keyYellow(self):
        if self.myUserSkin_active.value:
            self.copyTemplates()
            if not path.exists(self.skin_base_dir + "mySkin_off"):
                mkdir(self.skin_base_dir + "mySkin_off")
            if not path.exists(self.skin_base_dir + "preview"):
                mkdir(self.skin_base_dir + "preview")
            self.session.openWithCallback(self.UserSkinScreesnCB, UserSkinScreens)
        else:
            self["config"].setCurrentIndex(0)

    def keyOk(self):
        if self["config"].isChanged():
            for x in self["config"].list:
                x[1].save()
            configfile.save()
            chdir(self.skin_base_dir)
            if path.exists(self.font_file):
                remove(self.font_file)
            elif path.islink(self.font_file):
                remove(self.font_file)
            if path.exists('allFonts/' + self.myUserSkin_font.value):
                symlink('allFonts/' + self.myUserSkin_font.value, self.font_file)
            if path.exists(self.color_file):
                remove(self.color_file)
            elif path.islink(self.color_file):
                remove(self.color_file)
            if path.exists("allColors/" + self.myUserSkin_style.value):
                symlink("allColors/" + self.myUserSkin_style.value, self.color_file)
            if self.myUserSkin_active.value:
                if not path.exists("mySkin") and path.exists("mySkin_off"):
                        symlink("mySkin_off","mySkin")
            else:
                if path.exists("mySkin"):
                    if path.exists("mySkin_off"):
                        if path.islink("mySkin"):
                            remove("mySkin")
                        else:
                            shutil.rmtree("mySkin")
                    else:
                        rename("mySkin", "mySkin_off")
            self.update_user_skin()
            self.restartGUI()
        else:
            if self.changed_screens:
                self.update_user_skin()
                self.restartGUI()
            else:
                self.close()

    def UserSkinScreesnCB(self):
        self.changed_screens = True
        self["config"].setCurrentIndex(0)

    def restartGUI(self):
        myMessage = ''
        if self.BrakPlikuInfo != '':
            print"[UserSkin] missing components: %s" % self.BrakPlikuInfo
            myMessage += _("Missing components found: %s\n\n") % self.BrakPlikuInfo
        myMessage += _("Restart necessary, restart GUI now?")
        restartbox = self.session.openWithCallback(self.restartGUIcb,MessageBox, myMessage, MessageBox.TYPE_YESNO)
        restartbox.setTitle(_("Message"))

    def about(self):
        self.session.open(UserSkin_About)

    def restartGUIcb(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

    def update_user_skin(self):
        #print "[UserSkin} update_user_skin"
        #TBC - for VTI we don't need to make it, auto discovery would be nice
        user_skin_file=resolveFilename(SCOPE_CONFIG, 'skin_user' + self.currentSkin + '.xml')
        if path.exists(user_skin_file):
            remove(user_skin_file)
        if self.myUserSkin_active.value:
            print "[UserSkin} update_user_skin.self.myUserSkin_active.value"
            user_skin = ""
            if path.exists(self.skin_base_dir + 'skin_user_header.xml'):
                user_skin = user_skin + self.readXMLfile(self.skin_base_dir + 'skin_user_header.xml' , 'fonts')
            if path.exists(self.skin_base_dir + 'skin_user_colors.xml'):
                user_skin = user_skin + self.readXMLfile(self.skin_base_dir + 'skin_user_colors.xml' , 'ALLSECTIONS')
            if path.exists(self.skin_base_dir + 'mySkin'):
                for f in listdir(self.skin_base_dir + "mySkin/"):
                    user_skin = user_skin + self.readXMLfile(self.skin_base_dir + "mySkin/" + f, 'screen')
            if user_skin != '':
                user_skin = "<skin>\n" + user_skin
                user_skin = user_skin + "</skin>\n"
                with open (user_skin_file, "w") as myFile:
                    print "[UserSkin} update_user_skin.self.myUserSkin_active.value write myFile"
                    myFile.write(user_skin)
                    myFile.flush()
                    myFile.close()
            #checking if all renderers are in system
            self.checkComponent(user_skin, 'render' , '/usr/lib/enigma2/python/Components/Renderer/')
               
    def checkComponent(self, myContent, look4Component , myPath): #look4Component=render|
        r=re.findall( r' %s="([a-zA-Z0-9]+)" ' % look4Component , myContent )
        if r:
            for myComponent in set(r):
                #print" [UserSkin] checks if %s exists" % myComponent
                if not path.exists(myPath + myComponent + ".pyo") and not path.exists(myPath + myComponent + ".py"):
                    if self.BrakPlikuInfo == '':
                        self.BrakPlikuInfo = myComponent
                    else:
                        self.BrakPlikuInfo += "," + myComponent
        return
    
    def readXMLfile(self, XMLfilename, XMLsection): #sections:ALLSECTIONS|fonts|
        myPath=path.realpath(XMLfilename)
        if not path.exists(myPath):
            remove(XMLfilename)
            return ''
        filecontent = ''
        if XMLsection == 'ALLSECTIONS':
            sectionmarker = True
        else:
            sectionmarker = False
        with open (XMLfilename, "r") as myFile:
            for line in myFile:
                if line.find('<skin>') >= 0 or line.find('</skin>') >= 0:
                    continue
                if line.find('<%s' %XMLsection) >= 0 and sectionmarker == False:
                    sectionmarker = True
                elif line.find('</%s>' %XMLsection) >= 0 and sectionmarker == True:
                    sectionmarker = False
                    filecontent = filecontent + line
                if sectionmarker == True:
                    filecontent = filecontent + line
            myFile.close()
        if config.plugins.UserSkin.PIG_active.value == False:
            if filecontent.find('render="Pig"') > 0 or filecontent.find("render='Pig'") > 0:
                filecontent = ''
        return filecontent

    def copyTemplates(self):
        if path.exists(self.skin_base_dir):
            if not path.exists(self.skin_base_dir + "allScreens/"):
                mkdir(self.skin_base_dir + "allScreens/")
            TempDir = resolveFilename(SCOPE_PLUGINS, 'Extensions/UserSkin/templates/')
            if not path.exists(TempDir):
                return
            for f in listdir(TempDir):
                print f
                if f.endswith('.xml'):
                    if f.startswith('colors_' + self.currentSkin):
                        shutil.copy(TempDir + f, self.skin_base_dir + "allColors/") 
                    elif f.startswith('font_' + self.currentSkin):
                        shutil.copy(TempDir + f, self.skin_base_dir + "allFonts/") 
                    elif f.startswith('skin_' + self.currentSkin):
                        shutil.copy(TempDir + f, self.skin_base_dir + "allScreens/") 
                elif f.endswith('.png'):
                    if f.startswith('preview_' + self.currentSkin):
                        shutil.copy(TempDir + f, self.skin_base_dir + "preview/") 
                elif f.endswith('.py') or f.endswith('.pyo'):
                    if f.startswith('Converter_' + self.currentSkin):
                        shutil.copy(TempDir + f, self.skin_base_dir + "Converter/") 
                    elif f.startswith('Renderer_' + self.currentSkin):
                        shutil.copy(TempDir + f, self.skin_base_dir + "Renderer/") 
                    elif f.startswith('Source_' + self.currentSkin):
                        shutil.copy(TempDir + f, self.skin_base_dir + "Sources/") 
                    elif f.startswith('Component_' + self.currentSkin):
                        shutil.copy(TempDir + f, self.skin_base_dir + "Components/") 
        return

class UserSkin_About(Screen):
    skin = """
  <screen name="UserSkin_About" position="center,center" size="370,120" title="UserSkin v0.1">
    <eLabel text="(c)2014 by j00zek" position="0,15" size="370,50" font="Regular;28" halign="center" />
    <eLabel text="Based on AtileHD skin by schomi / plugin by VTi" position="0,55" size="370,30" font="Regular;18" halign="center" />
    <eLabel text="http://forum.xunil.pl" position="0,90" size="370,30" font="Regular;24" halign="center" />
  </screen>
"""

    def __init__(self, session, args = 0):
        self.session = session
        Screen.__init__(self, session)
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "cancel": self.cancel,
                "ok": self.keyOk,
            }, -2)

    def keyOk(self):
        self.close()

    def cancel(self):
        self.close()

class UserSkinScreens(Screen):
    skin = """
  <screen name="UserSkinScreens" position="0,0" size="1280,720" title="UserSkin Setup" backgroundColor="transparent" flags="wfNoBorder">
    <eLabel position="0,0" size="1280,720" zPosition="-15" backgroundColor="#20000000" />
    <eLabel position=" 55,100" size="725,515" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="785,295" size="445,320" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="785,100" size="135,190" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="925,100" size="305,190" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position=" 55,620" size="290,55" zPosition="-10" backgroundColor="#20b81c46" />
    <eLabel position="350,620" size="290,55" zPosition="-10" backgroundColor="#20009f3c" />
    <eLabel position="645,620" size="290,55" zPosition="-10" backgroundColor="#209ca81b" />
    <eLabel position="940,620" size="290,55" zPosition="-10" backgroundColor="#202673ec" />
    <eLabel position=" 55,675" size="290, 5" zPosition="-10" backgroundColor="#20b81c46" />
    <eLabel position="350,675" size="290, 5" zPosition="-10" backgroundColor="#20009f3c" />
    <eLabel position="645,675" size="290, 5" zPosition="-10" backgroundColor="#209ca81b" />
    <eLabel position="940,675" size="290, 5" zPosition="-10" backgroundColor="#202673ec" />
    <!--widget source="session.VideoPicture" render="Pig" position="935,115" zPosition="3" size="284,160" backgroundColor="#ff000000">
    </widget-->
    <widget source="Title" render="Label" position="70,47" size="950,43" font="Regular;35" foregroundColor="#00ffffff" backgroundColor="#004e4e4e" transparent="1" />
    <widget source="menu" render="Listbox" position="70,115" size="700,480" scrollbarMode="showOnDemand" transparent="1">
      <convert type="TemplatedMultiContent">
                                {"template":
                                        [
                                                MultiContentEntryPixmapAlphaTest(pos = (2, 2), size = (54, 54), png = 2),
                                                MultiContentEntryText(pos = (60, 2), size = (500, 54), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1),
                                        ],
                                        "fonts": [gFont("Regular", 22),gFont("Regular", 16)],
                                        "itemHeight": 60
                                }
                        </convert>
    </widget>
    <widget name="Picture" position="808,342" size="400,225" alphatest="on" />
    <widget source="key_red" render="Label" position="70,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20b81c46" transparent="1" />
    <widget source="key_green" render="Label" position="365,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20009f3c" transparent="1" />
    <widget name="key_blue" position="950,635" zPosition="1" size="260,25" valign="center" halign="left" font="Regular;20" transparent="1" foregroundColor="#00ffffff" />
  </screen>
"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        
        self.title=_("UserSkin additional screens")
        try:
            self["title"]=StaticText(self.title)
        except:
            print 'self["title"] was not found in skin'
        
        self["key_red"] = StaticText(_("Exit"))
        self["key_green"] = StaticText(_("on"))
        self["key_blue"] = Label()
        self['key_blue'].setText('')
        
        self["Picture"] = Pixmap()
        
        menu_list = []
        self["menu"] = List(menu_list)
        
        self["shortcuts"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"],
        {
            "ok": self.runMenuEntry,
            "cancel": self.keyCancel,
            "red": self.keyCancel,
            "green": self.runMenuEntry,
            "blue": self.keyBlue,
        }, -2)
        
        self.currentSkin = config.skin.primary_skin.value.replace('skin.xml', '').replace('/', '')
        self.skin_base_dir = resolveFilename(SCOPE_SKIN, config.skin.primary_skin.value.replace('skin.xml', ''))
        if not self.skin_base_dir.endswith('/'):
            self.skin_base_dir = self.skin_base_dir + '/'
        self.screen_dir = "allScreens"
        self.file_dir = "mySkin_off"
        self.enabled_pic = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/UserSkin/pic/install.png"))
        #check if we have preview files
        isPreview=0
        for xpreview in os.listdir(self.skin_base_dir + "preview/"):
            if len(xpreview) > 4 and  xpreview[-4:] == ".png":
                isPreview += 1
            if isPreview >= 2:
                break
        if self.currentSkin == "infinityHD-nbox-tux-full" and isPreview < 2:
            print "[UserSkin] no preview files :("
            self.disabled_pic = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/UserSkin/pic/opkg.png"))
            self['key_blue'].setText(_('Install from OPKG'))
        else:
            self.disabled_pic = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/UserSkin/pic/remove.png"))
        
        if not self.selectionChanged in self["menu"].onSelectionChanged:
            self["menu"].onSelectionChanged.append(self.selectionChanged)
        
        self.onLayoutFinish.append(self.createMenuList)

    def keyBlue(self):
            #self.session.openWithCallback(self.endrun , MessageBox,_("To see previews install enigma2-skin-infinityhd-nbox-tux-full-preview package"), type = MessageBox.TYPE_INFO)
            self.session.open(MessageBox,_("To see previews install package:\nenigma2-skin-infinityhd-nbox-tux-full-preview"), type = MessageBox.TYPE_INFO)
            return

    def endrun(self):
        return
     
    def selectionChanged(self):
        sel = self["menu"].getCurrent()
        self.setPicture(sel[0])
        if sel[2] == self.enabled_pic:
            self["key_green"].setText(_("off"))
        elif sel[2] == self.disabled_pic:
            self["key_green"].setText(_("on"))

    def createMenuList(self):
        chdir(self.skin_base_dir)
        f_list = []
        list_dir = sorted(listdir(self.skin_base_dir + self.screen_dir), key=str.lower)
        for f in list_dir:
            if config.plugins.UserSkin.PIG_active.value == False:
                if f.find('PIG') > 0 or f.find('PiG') > 0  or f.find('Pig') > 0 or f.lower().find('_pig') > 0:
                    continue
            if f.endswith('.xml') and f.startswith('skin_'):
                friendly_name = f.replace("skin_", "")
                friendly_name = friendly_name.replace(".xml", "")
                friendly_name = friendly_name.replace("_", " ")
                linked_file = self.skin_base_dir + self.file_dir + "/" + f
                if path.exists(linked_file):
                    if path.islink(linked_file):
                        pic = self.enabled_pic
                    else:
                        remove(linked_file)
                        symlink(self.skin_base_dir + self.screen_dir + "/" + f, self.skin_base_dir + self.file_dir + "/" + f)
                        pic = self.enabled_pic
                else:
                    pic = self.disabled_pic
                f_list.append((f, friendly_name, pic))
        menu_list = [ ]
        if len(f_list) == 0:
            f_list.append(("dummy", _("No User skins found"), self.disabled_pic))
        for entry in f_list:
            menu_list.append((entry[0], entry[1], entry[2]))
        self["menu"].updateList(menu_list)
        self.selectionChanged()

    def setPicture(self, f):
        pic = f.replace(".xml", ".png")
        #preview = self.skin_base_dir + "preview/preview_" + pic
        if path.exists(self.skin_base_dir + "preview/preview_" + pic):
            self["Picture"].instance.setPixmapFromFile(self.skin_base_dir + "preview/preview_" + pic)
            self["Picture"].show()
        elif path.exists(self.skin_base_dir + "preview/" + pic):
            self["Picture"].instance.setPixmapFromFile(self.skin_base_dir + "preview/" + pic)
            self["Picture"].show()
        else:
            self["Picture"].hide()
    
    def keyCancel(self):
        self.close()

    def runMenuEntry(self):
        sel = self["menu"].getCurrent()
        if sel[2] == self.enabled_pic:
            remove(self.skin_base_dir + self.file_dir + "/" + sel[0])
        elif sel[2] == self.disabled_pic:
            symlink(self.skin_base_dir + self.screen_dir + "/" + sel[0], self.skin_base_dir + self.file_dir + "/" + sel[0])
        self.createMenuList()
