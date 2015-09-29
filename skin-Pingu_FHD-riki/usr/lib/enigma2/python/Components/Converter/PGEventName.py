from Components.Converter.Converter import Converter
from Components.Element import cached
from Tools.ISO639 import LanguageCodes
from Tools.BoundFunction import boundFunction

class PGEventName(Converter, object):
    NAME = 0
    SHORT_DESCRIPTION = 1
    EXTENDED_DESCRIPTION = 2
    Extra = 4
    WideInfo = 5
    DolbyInfo = 6
    EngInfo = 7
    HDInfo = 8
    FraInfo = 9
    DolbyA = 10
    DolbyB = 11
    NormInfo = 12

    def __init__(self, type):
        Converter.__init__(self, type)
        if type == 'Description':
            self.type = self.SHORT_DESCRIPTION
        elif type == 'ExtendedDescription':
            self.type = self.EXTENDED_DESCRIPTION
        elif type == 'Extra':
            self.type = self.Extra
        elif type == 'WideInfo':
            self.type = self.WideInfo
        elif type == 'DolbyInfo':
            self.type = self.DolbyInfo
        elif type == 'EngInfo':
            self.type = self.EngInfo
        elif type == 'HDInfo':
            self.type = self.HDInfo
        elif type == 'FraInfo':
            self.type = self.FraInfo
        elif type == 'DolbyA':
            self.type = self.DolbyA
        elif type == 'DolbyB':
            self.type = self.DolbyB
        elif type == 'NormInfo':
            self.type = self.NormInfo
        else:
            self.type = self.NAME

    @cached
    def getBoolean(self):
        event = self.source.event
        if not event:
            return False
        if self.type == self.WideInfo:
            data = str(event.getComponentData())
            if '16:9' in data or '11' in data or 'Breitwand' in data:
                return True
            return False
        if self.type == self.DolbyInfo:
            data = str(event.getComponentData())
            if 'Dolby' in data:
                return True
            return False
        if self.type == self.EngInfo:
            data = str(event.getComponentData())
            if 'English' in data or 'ENG' in data:
                return True
            return False
        if self.type == self.HDInfo:
            data = str(event.getComponentData())
            if '11' in data or 'HDTV' in data:
                return True
            return False
        if self.type == self.FraInfo:
            data = str(event.getComponentData())
            if 'fra' in data or 'fre' in data:
                return True
            return False
        if self.type == self.DolbyA:
            data = str(event.getComponentData())
            if 'Dolby Digital 2.0' in data:
                return False
            if 'Dolby Digital 5.1' in data or '11' in data:
                return True
            return False
        if self.type == self.DolbyB:
            data = str(event.getComponentData())
            if 'Dolby Digital 2.0' in data:
                return True
            return False
        if self.type == self.NormInfo:
            data = str(event.getComponentData())
            if '4:3' in data:
                return True
            return False

    boolean = property(getBoolean)

    @cached
    def getText(self):
        event = self.source.event
        if event is None:
            return ''
        elif self.type == self.NAME:
            return event.getEventName()
        elif self.type == self.SHORT_DESCRIPTION:
            return event.getShortDescription()
        elif self.type == self.EXTENDED_DESCRIPTION:
            return event.getExtendedDescription()
        elif self.type == self.Extra:
            return str(event.getComponentData())
        else:
            return

    text = property(getText)