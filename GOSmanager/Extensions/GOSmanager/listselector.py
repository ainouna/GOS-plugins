# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from enigma import ePoint
from Tools.LoadPixmap import LoadPixmap
from Components.Label import Label
from Components.LanguageGOS import gosgettext as _
from Components.Sources.List import List

class ListSelectorWidget(Screen):
    skin = """
    <screen name="ListSelectorWidgetScreen" position="center,center" size="480,555" title="ListSelectorWidget" >
        <widget source="list" render="Listbox" position="5,5" size="470,510" scrollbarMode="showOnDemand">
            <convert type="TemplatedMultiContent">
                {"template": [
                              #MultiContentEntryText(pos = (160, 2), size = (280, 36), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0), # name
                              MultiContentEntryText(pos = (160, 7), size = (280, 90), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER|RT_WRAP, text = 1), # index 0 is the name
                              MultiContentEntryPixmapAlphaTest(pos = (5, 2), size = (150, 100), png = 4), # index 4 is the status pixmap
                              ],
                "fonts": [gFont("Regular", 24),gFont("Regular", 14)],
                "itemHeight": 102
                }
            </convert>
        </widget>
        <widget name="key_red" position="300,530" zPosition="2" size="130,22" valign="center" halign="right" font="Regular;20" transparent="1" foregroundColor="red" />
    </screen>"""
   
    def __init__(self, session, list, Mytitle = 'ListSelectorWidget'): #lista zawiera <tytul opcji>, <oplink do pikony opcji>
        Screen.__init__(self, session)
        self.session = session
        
        if list == None or len(list) < 1:
            self.close(None)
            
        self.list = list
        self.title = Mytitle
        self["list"] = List(self.list)
        self["key_red"] = Label(_("Cancel"))

        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions"],
        {
            "ok": self.ok_pressed,
            "back": self.back_pressed,
            "red": self.back_pressed,
        }, -1)
        
        self.onLayoutFinish.append(self.onStart)
        return
        
    def onStart(self):
        self.setTitle(_(self.title))
	self.Menulist = []
        for item in self.list:
            try:
                self.Menulist.append((item[0], _(item[0], "plugin-GOSmanager") , '', '', LoadPixmap(cached=True, path=item[2]) ))
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
