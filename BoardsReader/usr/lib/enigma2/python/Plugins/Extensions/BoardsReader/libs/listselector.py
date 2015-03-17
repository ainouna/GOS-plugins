# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Components.ActionMap import ActionMap, HelpableActionMap
from enigma import ePoint
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE
from Tools.LoadPixmap import LoadPixmap
from Components.Label import Label
from Components.config import config
from Components.Sources.List import List

class ListSelectorWidget(Screen):
    skin = """
    <screen name="ListSelectorWidgetScreen" position="center,center" size="450,340" title="ListSelectorWidget" >
        <widget source="list" render="Listbox" position="5,5" size="440,315" scrollbarMode="showOnDemand">
            <convert type="TemplatedMultiContent">
                {"template": [
                              MultiContentEntryText(pos = (110, 2), size = (440, 100), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0), 
                              MultiContentEntryText(pos = (110, 26), size = (440, 16), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1),
                              MultiContentEntryPixmapAlphaTest(pos = (5, 2), size = (100, 100), png = 4), # index 4 is the status pixmap
                              ],
                "fonts": [gFont("Regular", 24),gFont("Regular", 14)],
                "itemHeight": 105
                }
            </convert>
        </widget>
        <widget name="key_red" position="300,320" zPosition="2" size="130,22" valign="center" halign="right" font="Regular;20" transparent="1" foregroundColor="red" />
    </screen>"""
   
    def __init__(self, session, list, mytitle = 'ListSelectorWidget'): #lista zawiera <tytul opcji>, <nazwa opcji do zwrocenia>, <oplink do pikony opcji>
        Screen.__init__(self, session)
        self.session = session
        
        if list == None or len(list) < 1:
            self.close(None)
            
        self.list = list
        self.title = mytitle
        self["list"] = List(self.list)
        self["key_red"] = Label(_("Cancel"))

        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions"],
        {
            "ok": self.ok_pressed,
            "red": self.back_pressed,
            "back": self.back_pressed,
        }, -1)
        
        self.onLayoutFinish.append(self.onStart)
        return
        
    def onStart(self):
        self.setTitle(_(self.title))
	self.Menulist = []
        for item in self.list:
            try:
                self.Menulist.append((item[0] , item[0] , '', '', LoadPixmap(cached=True, path=item[2])))
            except:
                pass
        self['list'].setList(self.Menulist)
        return
                    
    def __onClose(self):
        return
        
    def back_pressed(self):
        self.close(None)
        return

    def ok_pressed(self):
        current = self['list'].getIndex()
        print "[BoardsReader] selected %s" % self.list[current][1]
        self.close(self.list[current])
