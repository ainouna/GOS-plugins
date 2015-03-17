from os import path, system
from subprocess import call as subprocess_call
from Plugins.Plugin import PluginDescriptor
from Components.PluginComponent import plugins
from Components.ServiceEventTracker import ServiceEventTracker
from enigma import iPlayableService
from Components.Label import Label
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from traceback import print_exc
from Tools.Import import my_import
from Screens.MessageBox import MessageBox
from threading import Thread
#from enigma import *
#from Components.Console import Console

doit = True
PlugLoadInstance = None
def woWebIf(session):
    try:
        modul = my_import('.'.join(['Plugins', 'Extensions', 'WebInterface', 'plugin']))
        myweb = getattr(modul, 'restartWebserver')
        myweb(session)
    except:
        print_exc()
class PlugLoadConfig(Screen):
    def __init__(self, session):
        try:
            Screen.__init__(self, session)
            self.session = session
            self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'ok':self.keyOK}, -1)
            self['text'] = Label(_('Press OK to reload the plugins manually!\nPress EXIT to cancel!'))
            skin = '<screen position="center,center" size="400,75" title="PlugLoad" >\n\t\t\t<widget name="text" position="0,0" zPosition="1" size="400,75" font="Regular;20" valign="center" halign="center" transparent="1" />\n\t\t\t</screen>'
            self.skin = skin
        except:
            print_exc()
            self.close()
    def cancel(self):
        self.close()
    def keyOK(self):
        try:
            print '[PlugLoad] is enabling Plugins'
            #system('/jzk/etc/PlugLoad.sh py')
            #Console().ePopen('/jzk/etc/PlugLoad.sh py')
            subprocess_call('/jzk/etc/PlugLoad.sh py', shell=True)
            print '[PlugLoad] is loading Plugins'
            plugins.readPluginList('/usr/lib/enigma2/python/Plugins/')
            if path.exists('/usr/lib/enigma2/python/Plugins/Extensions/WebInterface') is True:
                woWebIf(self.session)
            self.session.open(MessageBox, _('The plugins were reloaded successfully!'), MessageBox.TYPE_INFO, timeout=3)
            self.close()
        except:
            print_exc()
class PlugLoad1(Thread):
    def __init__(self, session):
        Thread.__init__(self)
        self.session = session
    def run(self):
        try:
            print '[PlugLoad] is enabling Plugins'
            #Console().ePopen('/jzk/etc/PlugLoad.sh py')
            #system('/jzk/etc/PlugLoad.sh py')
            subprocess_call('/usr/lib/enigma2/python/Plugins/Extensions/PlugLoad/PlugLoad.sh py', shell=True)
            print '[PlugLoad] is loading Plugins'
            plugins.readPluginList('/usr/lib/enigma2/python/Plugins/')
            if path.exists('/usr/lib/enigma2/python/Plugins/Extensions/WebInterface') is True:
                woWebIf(self.session)
            with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
            Console().ePopen('(/bin/run-parts /jzk/cron/post_E2) &')
            #system('(/bin/run-parts /jzk/cron/post_E2) &')
            #subprocess_call('(/bin/run-parts /jzk/cron/post_GUI) &', shell=True) odpalone przez vfd
        except:
            print '[PlugLoad] exception handled'
            print_exc()
class PlugLoad:
    def __init__(self, session):
        try:
            self.session = session
            self.service = None
            self.onClose = []


            self._PlugLoad__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evUpdatedInfo:self._PlugLoad__evUpdatedInfo})

        except:
            print_exc()
    def _PlugLoad__evUpdatedInfo(self):
        try:
            global doit
            if doit is True:
                doit = False
                service = self.session.nav.getCurrentService()
                if service is not None:
                    print '[PlugLoad] is initialising itself'
                    ret = PlugLoad1(self.session)
                    ret.start(); #continue
        except:
            print_exc()
def main(session, **kwargs):
    global PlugLoadInstance
    if PlugLoadInstance is None:
        PlugLoadInstance = PlugLoad(session)
def openconfig(session, **kwargs):
    session.open(PlugLoadConfig)
def Plugins(**kwargs):
    return [PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=main), PluginDescriptor(name=_('PlugLoad'), description=_('Load Plugins'), where=[PluginDescriptor.WHERE_PLUGINMENU], fnc=openconfig)]
