# -*- coding: utf-8 -*-

# InetSpeedTest
#
# maintainer: j00zek
#
# extension for openpli, all skins, descriptions, bar selections and other @j00zek 2014/2015
# Uszanuj czyj¹œ pracê i NIE przyw³aszczaj sobie autorstwa!

#This plugin is free software, you are allowed to
#modify it (if you keep the license),
#but you are not allowed to distribute/publish
#it without source code (this version and your modifications).
#This means you also have to distribute
#source code of your modifications.

from Plugins.Plugin import PluginDescriptor
from os.path import exists
        
def Plugins(**kwargs):
    return [PluginDescriptor(name=_("InetSpeedTest"), description=_("Check health of your inet connection"), where = PluginDescriptor.WHERE_PLUGINMENU, fnc=main)]

def main(session, **kwargs):
    from Screens.Console import Console
    from Tools.Directories import resolveFilename, SCOPE_PLUGINS
    runlist = []
    ScriptPath = resolveFilename(SCOPE_PLUGINS, 'Extensions/InetSpeedTest/')
    runlist.append( ('chmod 755 %s/speedtest_cli.py*' % ScriptPath) )
    if exists('%s/speedtest_cli.py' % ScriptPath):
        runlist.append( ('%s/speedtest_cli.py' % ScriptPath) )
    elif exists('%s/speedtest_cli.pyo' % ScriptPath):
        runlist.append( ('%s/speedtest_cli.pyo' % ScriptPath) )
    elif exists('%s/speedtest_cli.pyc' % ScriptPath):
        runlist.append( ('%s/speedtest_cli.pyc' % ScriptPath) )
    else:
        runlist.append( ('echo "missing %s/speedtest_cli.py!!!' % ScriptPath) )

    session.open(Console, title = "InetSpeedTest...", cmdlist = runlist)
