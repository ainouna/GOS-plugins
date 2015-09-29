from enigma import iServiceInformation
from Components.Converter.Converter import Converter
from Components.Element import cached
from Tools.Directories import fileExists
import os

class CamdInfo3(Converter, object):

    def __init__(self, type):
        Converter.__init__(self, type)

    @cached
    def getText(self):
        service = self.source.service
        info = service and service.info()
        camd = ''
        camdlist = None
        serlist = None
        if not info:
            return ''
        else:
            if fileExists('/tmp/.emu.info'):
                try:
                    camdlist = open('/tmp/.emu.info', 'r')
                except:
                    return

            elif fileExists('/etc/CurrentBhCamName'):
                try:
                    camdlist = open('/etc/CurrentBhCamName', 'r')
                except:
                    return

            elif fileExists('/etc/active_emu.list'):
                try:
                    camdlist = open('/etc/.active_emu.list', 'r')
                except:
                    return

            elif fileExists('/tmp/egami.inf', 'r'):
                lines = open('/tmp/egami.inf', 'r').readlines()
                for line in lines:
                    item = line.split(':', 1)
                    if item[0] == 'Current emulator':
                        return item[1].strip()

            elif fileExists('/etc/init.d/softcam') or fileExists('/etc/init.d/cardserver') or fileExists('/etc/.ActiveCamd'):
                try:
                    camdlist = os.popen('/etc/init.d/softcam info')
                except:
                    pass

                try:
                    serlist = os.popen('/etc/init.d/cardserver info')
                except:
                    pass

                try:
                    camdlist = open('/etc/.ActiveCamd', 'r')
                except:
                    pass

            elif fileExists('/tmp/cam.info'):
                try:
                    camdlist = open('/tmp/cam.info', 'r')
                except:
                    return

            elif fileExists('/etc/clist.list'):
                try:
                    camdlist = open('/etc/clist.list', 'r')
                except:
                    return

            elif fileExists('/usr/lib/enigma2/python/Plugins/Bp/geminimain/lib/libgeminimain.so'):
                try:
                    from Plugins.Bp.geminimain.plugin import GETCAMDLIST
                    from Plugins.Bp.geminimain.lib import libgeminimain
                    camdl = libgeminimain.getPyList(GETCAMDLIST)
                    cam = None
                    for x in camdl:
                        if x[1] == 1:
                            cam = x[2]

                    return cam
                except:
                    return

            else:
                return
            if serlist is not None:
                try:
                    cardserver = ''
                    for current in serlist.readlines():
                        cardserver = current

                    serlist.close()
                except:
                    pass

            else:
                cardserver = 'NA'
            if camdlist is not None:
                try:
                    emu = ''
                    for current in camdlist.readlines():
                        emu = current

                    camdlist.close()
                except:
                    pass

            else:
                emu = 'NA'
            return '%s %s' % (cardserver.split('\n')[0], emu.split('\n')[0])

    text = property(getText)

    def changed(self, what):
        Converter.changed(self, what)