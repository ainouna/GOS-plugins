##
## P(icture)i(n)g(raphics) renderer
##
from Renderer import Renderer
from enigma import eVideoWidget, eSize, eRect, ePoint, getDesktop
from Screens.PictureInPicture import PipPigMode
from Tools.GOSHardwareInfo import GOSHardwareInfo
if GOSHardwareInfo().get_rcstype() == 'ADB5800':
    print 'PIG disabled'
    PIGenabled=False
else:
    print 'PIG enabled'
    PIGenabled=True

class Pig(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.Position = self.Size = None
        self.hidePip = True

    GUI_WIDGET = eVideoWidget

    def postWidgetCreate(self, instance):
        desk = getDesktop(0)
        instance.setDecoder(0)
        instance.setFBSize(desk.size())

    def applySkin(self, desktop, parent):
        if PIGenabled:
            attribs = self.skinAttributes[:]
            for (attrib, value) in self.skinAttributes:
                if attrib == "hidePip":
                    self.hidePip = value == 1
                    attribs.remove((attrib,value))
                    break
            self.skinAttributes = attribs
            ret = Renderer.applySkin(self, desktop, parent)
            if ret:
                self.Position = self.instance.position()
                self.Size = self.instance.size()
            return ret
        else:
            return 0

    def onShow(self):
        if self.instance and PIGenabled:
            if self.Size:
                self.instance.resize(self.Size)
            if self.Position:
                self.instance.move(self.Position)
            self.hidePip and PipPigMode(True)

    def onHide(self):
        if self.instance and PIGenabled:
            self.preWidgetRemove(self.instance)
            self.hidePip and PipPigMode(False)