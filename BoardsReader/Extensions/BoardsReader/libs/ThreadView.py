from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.config import config
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
#from Components.Sources.StaticText import StaticText
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
try:
    from Components.LanguageGOS import gosgettext as _ 
except:
    from libs.tools import TranslateTXT as _

class ThreadView(Screen):
    xunil = 0
    dvhk = 1
    
    def __init__(self, session,  WebPage , MainURL, ThreadURL):
        self.session = session
        Screen.__init__(self, session)

        self["text"] = ScrollLabel("")
        #nasze ustawienia
        self.mainurl = MainURL
        self.ThreadURL = ThreadURL 
        self.Plugin_PATH = resolveFilename(SCOPE_PLUGINS, 'Extensions/BoardsReader/')
        self.WebPage = WebPage[WebPage.find('\n')+1:]
        self.newtitle = WebPage[:WebPage.find('\n')]
        #print self.ThreadURL
        self.CurrentThreadPage = 1
        self.MaxThreadPage = 1
        self.MultiThreadPages = False
        if self.mainurl.find('xunil') > 0 :
            self.Board = self.xunil
        else:
            self.Board = self.dvhk
        
        if self.newtitle.find('Strona ') > 0 : # Zwracana strona musi zawierac w pierwszej linijce tytul i liczbe stron
            tmpPage = self.newtitle[self.newtitle.find('Strona ') + len('Strona '):]
            tmpPage = tmpPage[:tmpPage.find(' ')].strip()
            if tmpPage.isdigit(): 
                self.MultiThreadPages = True
                self.CurrentThreadPage = int(tmpPage)
                self.MaxThreadPage = self.CurrentThreadPage
                #print "Aktualna strona: " + tmpPage
        
        if self.MultiThreadPages == False:
            skin = """
                <screen name="ThreadView" position="50,70" size="1180,600" title="ThreadView..." >
                    <ePixmap position="5,5" zPosition="4" size="30,30" pixmap="%s/icons/red.png" transparent="1" alphatest="on" />
                    <widget name="key_red" position="40,5" size="300,27" valign="center" halign="left" font="Regular;21" transparent="1" foregroundColor="white"/>
                    <widget name="text" position="0,40" size="1180,560" font="Regular;24" />
                </screen>"""% (self.Plugin_PATH)
            self.skin = skin
            self["key_red"] = Label(_("Single page thread"))
        
            self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions"], 
            {
                "ok": self.cancel,
                "back": self.cancel,
                "left": self["text"].pageUp,
                "right": self["text"].pageDown,
                "up": self["text"].pageUp,
                "down": self["text"].pageDown
            }, -1)
        else:
            skin = """
                <screen name="ThreadView" position="50,70" size="1180,600" title="ThreadView..." >
                <ePixmap position="5,5" zPosition="4" size="30,30" pixmap="%s/icons/red.png" transparent="1" alphatest="on" />
                <ePixmap position="300,5" zPosition="4" size="30,30" pixmap="%s/icons/green.png" transparent="1" alphatest="on" />
                <ePixmap position="605,5" zPosition="4" size="30,30" pixmap="%s/icons/yellow.png" transparent="1" alphatest="on" />
                <ePixmap position="905,5" zPosition="4" size="30,30" pixmap="%s/icons/blue.png" transparent="1" alphatest="on" />
                <widget name="key_red" position="40,5" size="140,27" zPosition="5" valign="center" halign="left" backgroundColor="black" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_green" position="340,5" size="180,27" zPosition="5" valign="center" halign="left" backgroundColor="black" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_yellow" position="640,5" size="300,27" zPosition="5" valign="center" halign="left" backgroundColor="black" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="key_blue" position="940,5" size="140,27" zPosition="5" valign="center" halign="left" backgroundColor="black" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
                <widget name="text" position="0,40" size="1180,560" font="Regular;24" />
                </screen>""" % (self.Plugin_PATH,self.Plugin_PATH,self.Plugin_PATH,self.Plugin_PATH)
            self.skin = skin
            self["key_red"] = Label(_("First page"))
            self["key_green"] = Label(_("Previous page"))
            self["key_yellow"] = Label(_("Current page"))
            self["key_blue"] = Label(_("Current page"))

            self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions"], 
            {
                "ok": self.cancel,
                "back": self.cancel,
                "left": self["text"].pageUp,
                "right": self["text"].pageDown,
                "up": self["text"].pageUp,
                "down": self["text"].pageDown,
                "red": self.red_pressed,
                "green": self.green_pressed,
                "yellow": self.yellow_pressed,
                "blue": self.blue_pressed,
            }, -1)
          
        self.onShown.append(self.updateTitle)
        
        self.onLayoutFinish.append(self.processWebPage) # dont start before gui is finished

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def processWebPage(self):
        with open('/tmp/Thread.txt', 'w') as myfile:
            myfile.write(self.WebPage)
        self.removeHTMLtags()
        self.reversePosts()
        self["text"].setText(self.WebPage)

    def removeHTMLtags(self):
        print"removeHTMLtags"
        self.WebPage = self.WebPage.replace("</tr>","").replace("</td>","").replace("</a>","")
        while self.WebPage.find('  ') > 0:
          print"removeHTMLtags spaces"
          self.WebPage = self.WebPage.replace("  "," ")
        while self.WebPage.find('\t\t') > 0:
          print"removeHTMLtags tabs"
          self.WebPage = self.WebPage.replace("\t\t","\t")
        while self.WebPage.find('\n\n') > 0:
          print"removeHTMLtags newline"
          self.WebPage = self.WebPage.replace("\n\n","\n")
          
        return self.WebPage

    def reversePosts(self):
        if config.plugins.BoardReader.PostsInReverseOrder.value == True:
            Posts = self.WebPage.split("##########")
            if len(Posts) > 2:
                self.WebPage = ''
                for post in reversed(Posts):
                    self.WebPage += "##########" + post + "\n"
    
    def cancel(self):
        self.close()

    def SetLabels(self):
        if self.CurrentThreadPage == 1 :
            self["key_red"].setText(_("Current page"))
            self["key_green"].setText(_("Current page"))
            self["key_yellow"].setText(_("Next page"))
            self["key_blue"].setText(_("Last page"))
        elif self.CurrentThreadPage > 1 and self.CurrentThreadPage < self.MaxThreadPage :
            self["key_red"].setText(_("First page"))
            self["key_green"].setText(_("Previous page"))
            self["key_yellow"].setText(_("Next page"))
            self["key_blue"].setText(_("Last page"))
        elif self.CurrentThreadPage == self.MaxThreadPage :
            self["key_red"].setText(_("First page"))
            self["key_green"].setText(_("Previous page"))
            self["key_yellow"].setText(_("Current page"))
            self["key_blue"].setText(_("Current page"))
        return  

    def red_pressed(self):
        if self.CurrentThreadPage != 1:
            self.CurrentThreadPage = 1
            self.GetOtherThreadPage()
            self.SetLabels()
        return

    def green_pressed(self):
        if self.CurrentThreadPage > 1:
            self.CurrentThreadPage = self.CurrentThreadPage - 1
            self.GetOtherThreadPage()
            self.SetLabels()
        return

    def yellow_pressed(self):
        if self.CurrentThreadPage < self.MaxThreadPage:
            self.CurrentThreadPage = self.CurrentThreadPage + 1
            self.GetOtherThreadPage()
            self.SetLabels()
        return
 
    def blue_pressed(self):
        if self.CurrentThreadPage != self.MaxThreadPage:
            self.CurrentThreadPage = self.MaxThreadPage
            self.GetOtherThreadPage()
            self.SetLabels()
        return

    def GetOtherThreadPage(self):
        if self.Board == self.xunil:
            from Plugins.Extensions.BoardsReader.libs.smf import GetWebPage, GetFullThread
            username = config.plugins.BoardReader.xunil_login.value
            password = config.plugins.BoardReader.xunil_password.value
            myThreadURL = '.%i.html' % ((self.CurrentThreadPage - 1) * 15)
        elif self.Board == self.dvhk:
            from Plugins.Extensions.BoardsReader.libs.vbulletin import GetWebPage, GetFullThread
            username = config.plugins.BoardReader.dvhk_login.value
            password = config.plugins.BoardReader.dvhk_password.value
            myThreadURL = '&page=%i' % self.CurrentThreadPage
        else:
            return
        myThreadURL = self.ThreadURL + myThreadURL
        print "GetOtherThreadPage>>>" + self.mainurl + myThreadURL
        try:
            self.WebPage = GetFullThread(GetWebPage(self.mainurl,myThreadURL,username,password))
        except:
            pass
        self.newtitle = self.WebPage[:self.WebPage.find('\n')]
        self.setTitle(self.newtitle)
        self.WebPage = self.WebPage[self.WebPage.find('\n')+1:]
        self.processWebPage()
        return