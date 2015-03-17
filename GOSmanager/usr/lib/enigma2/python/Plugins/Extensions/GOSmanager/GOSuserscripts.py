# -*- coding: utf-8 -*-
# @j00zek 2104 dla Graterlia
#
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from os import listdir
from Plugins.Plugin import PluginDescriptor
from GOSconsole import GOSconsole
from Screens.Screen import Screen

############################################
from Components.LanguageGOS import gosgettext as _

class UserScripts(Screen):
    skin = """
    <screen position="center,center" size="420,400" title="%s" >
        <widget name="list" position="0,0" size="420,400" scrollbarMode="showOnDemand" />
    </screen>""" % _("User scripts")

    def __init__(self, session, args=None):
        Screen.__init__(self, session)
        self.session = session
        
        try:
            list = listdir("/etc/sysconfig/user_scripts")
            list = [x for x in list]
        except:
            list = []
        
        self["list"] = MenuList(list)
        
        self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.run, "cancel": self.close}, -1)

    def run(self):
        script = self["list"].getCurrent()
        if script is not None:
            #self.session.open(GOSconsole, script.replace("_", " "), cmdlist=[("/etc/sysconfig/user_scripts/%s" % script)])
            self.session.openWithCallback(self.endrun ,GOSconsole, title = "%s" % script, cmdlist = [ ('"/etc/sysconfig/user_scripts/%s"' % script) ])

    def endrun(self):
        return
    
