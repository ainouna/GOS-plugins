# -*- coding: utf-8 -*-
#
#  BoardsReader 2015 by j00zek 2015
#
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigNothing, NoSave, ConfigYesNo, Config, ConfigInteger, ConfigSubList, ConfigText, getConfigListEntry, configfile
from Components.ConfigList import ConfigListScreen
from libs.tools import removeAllIconsFromPath, GetHostsList, IsHostEnabled, TranslateTXT as _
from confighost import ConfigHostMenu
try:
    from Components.LanguageGOS import gosgettext as _ 
except:
    from libs.tools import TranslateTXT as _

config.plugins.BoardReader = ConfigSubsection()
config.plugins.BoardReader.separator = NoSave(ConfigNothing())
config.plugins.BoardReader.showinextensions = ConfigYesNo(default = True)
config.plugins.BoardReader.showinMainMenu = ConfigYesNo(default = False)
config.plugins.BoardReader.PostsInReverseOrder = ConfigYesNo(default = True)
config.plugins.BoardReader.SelectFromList = ConfigSelection(default = "list", choices = [("list", _("List")),("picons", _("Picons"))]) 

########################################################
# Generate list of hosts options for Enabling/Disabling
########################################################
gListOfHostsNames = [] 
gListOfHostsNames = GetHostsList()
for hostName in gListOfHostsNames:
    try:
        print("Set default options for host '%s'" % hostName)
        # as default all hosts are enabled
        exec('config.plugins.BoardReader.host' + hostName + ' = ConfigYesNo(default = True)')
    except:
        print("Options import for host '%s' EXEPTION" % hostName)

class ConfigMenu(Screen, ConfigListScreen):

    skin = """
    <screen name="ConfigMenu" position="center,center" size="420,240" title="BoardsReaderConfigMenu" >

            <widget name="config" position="10,10" size="400,200" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />
            <widget name="key_red" position="0,210" zPosition="2" size="210,30" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="red" />
            <widget name="key_green" position="210,210" zPosition="2" size="210,30" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="green" />
    </screen>"""
    
    def __init__(self, session):
        Screen.__init__(self, session)
        
        self.onChangedEntry = [ ]
        self.list = [ ]
        ConfigListScreen.__init__(self, self.list, session = session, on_change = self.changedEntry)
        self.setup_title = _("Boards Reader settings")

        self["key_green"] = Label(_("Save"))
        self["key_red"] = Label(_("Cancel"))
        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "cancel": self.keyCancel,
                "green": self.keySave,
                "ok": self.keyOK,
                "red": self.keyCancel,
            }, -2)

        global gListOfHostsNames
        # prepar config entries for hosts Enabling/Disabling
        self.listConfigHostsEntries = []
        for hostName in gListOfHostsNames:
            exec( 'self.listConfigHostsEntries.append(getConfigListEntry( "%s" , config.plugins.BoardReader.host' % _("Press OK to set %s options") % hostName + hostName + '))' )
        
        self.firstHostIdx = -1
        self.runSetup()
        self.onLayoutFinish.append(self.layoutFinished)
        
    def layoutFinished(self):
        self.setTitle(_("Boards Reader settings"))

    def runSetup(self):

        self.list = []
        self.list.append(getConfigListEntry(_("Forum selection style:"), config.plugins.BoardReader.SelectFromList))
        self.list.append(getConfigListEntry(_("Display last posts on top:"), config.plugins.BoardReader.PostsInReverseOrder))
        self.list.append(getConfigListEntry(_("Show plugin on the Extensions menu?"), config.plugins.BoardReader.showinextensions))
        self.list.append(getConfigListEntry(_("Show plugin in main menu?"), config.plugins.BoardReader.showinMainMenu))
        self.list.append(getConfigListEntry("   ", config.plugins.BoardReader.separator))
        self.firstHostIdx = len(self.list)
        
        for hostConfItem in  self.listConfigHostsEntries:
            self.list.append( hostConfItem )
        
        self["config"].list = self.list
        self["config"].setList(self.list)

    def keySave(self):
        self.save()
        self.close()
    
    def save(self):
        for x in self["config"].list:
            x[1].save()
        configfile.save()
      
    def keyOK(self):
        self.save()
        
        if self.firstHostIdx > -1:
            curIndex = self["config"].getCurrentIndex()
            if curIndex >= self.firstHostIdx:
                # calculate index in hosts list
                idx = curIndex - self.firstHostIdx
                global gListOfHostsNames
                if idx < len(gListOfHostsNames):
                    hostName = gListOfHostsNames[idx]
                    if IsHostEnabled(hostName):
                        try:
                            self.host = __import__('forums.forum' + hostName, globals(), locals(), ['GetConfigList'], -1)
                            if( len(self.host.GetConfigList()) < 1 ):
                                print('ConfigMenu host "%s" does not have additiona configs' % hostName)
                            self.session.open(ConfigHostMenu, hostName = hostName)
                        except:
                            print('ConfigMenu host "%s" does not have method GetConfigList' % hostName)
        return

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
            