#!/usr/bin/env python
# -*- coding: utf-8 -*-
#######################################################################
# maintainer: <schomi@vuplus-support.org> 
# THX @einfall and @markusw for parts of this code
# modified by j0zek:
# - selection of description language
# - downloading also from filmweb.pl to get covers for Polish moview
#This plugin is free software, you are allowed to
#modify it (if you keep the license),
#but you are not allowed to distribute/publish
#it without source code (this version and your modifications).
#This means you also have to distribute
#source code of your modifications.
#######################################################################

myDEBUG = True #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
append2file=False
def printDEBUG( myText , myFUNC = '???'):
    global append2file
    if myDEBUG:
        print ("[CoverFind] %s" % myText)
        try:
            if append2file == False:
                f = open('/tmp/CoverFind.log', 'w')
                append2file = True
            else:
                f = open('/tmp/CoverFind.log', 'a')
            f.write('[CoverFind:' + myFUNC + '] ' + myText + '\n')
            f.close
        except:
            pass

from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import *
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmap, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap
from Components.AVSwitch import AVSwitch
from Components.PluginComponent import plugins
from Components.config import *
from Components.ConfigList import ConfigList, ConfigListScreen
# from Components.FileList import FileList
from re import compile as re_compile
from os import path as os_path, listdir
from Components.MenuList import MenuList
from Components.Harddisk import harddiskmanager
from Tools.Directories import SCOPE_CURRENT_SKIN, resolveFilename, fileExists
from enigma import RT_HALIGN_LEFT, eListboxPythonMultiContent, eServiceReference, eServiceCenter, gFont
from Tools.LoadPixmap import LoadPixmap
#
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.GUIComponent import GUIComponent
from Components.Sources.List import List
from Tools.LoadPixmap import LoadPixmap
from Tools.BoundFunction import boundFunction
from Tools.Directories import pathExists, fileExists, SCOPE_SKIN_IMAGE, resolveFilename
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from enigma import eListboxPythonMultiContent, eListbox, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, loadPNG, RT_WRAP, eConsoleAppContainer, eServiceCenter, eServiceReference, getDesktop, loadPic, loadJPG, RT_VALIGN_CENTER, gPixmapPtr, ePicLoad, eTimer
import sys, os, re, shutil
from os import path, remove
from twisted.web.client import getPage
from twisted.web.client import downloadPage
from twisted.web import client, error as weberror
from twisted.internet import reactor
from twisted.internet import defer
from urllib import urlencode
from Tools.MovieInfoParser import getExtendedMovieDescription 

try:
    from Components.LanguageGOS import gosgettext as _
    printDEBUG('[CoverFind] LanguageGOS detected')
except:
    printDEBUG('LanguageGOS not detected, using local _')
    from Components.Language import language
    from Tools.Directories import SCOPE_PLUGINS
    import gettext
    PluginLanguageDomain = "CoverFind"
    PluginLanguagePath = "Extensions/CoverFind/locale"
    def localeInit():
        lang = language.getLanguage()[:2]
        os.environ["LANGUAGE"] = lang
        gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))
    def _(txt):
        t = gettext.dgettext(PluginLanguageDomain, txt)
        if t == txt:
            t = gettext.gettext(txt)
        return t
    localeInit()
    language.addCallback(localeInit)
    
pname = _("CoverFind")
pdesc = _("Find Cover ... function for Movielist")
pversion = "0.7-r3"
pdate = "20150124"

config.plugins.coverfind = ConfigSubsection()
config.plugins.coverfind.themoviedb_coversize = ConfigSelection(default="w185", choices = ["w92", "w185", "w500", "original"])
config.plugins.coverfind.followsymlink = ConfigYesNo(default = False)
#config.plugins.coverfind.thetvdb_coversize = ConfigSelection(default="w185", choices = ["w92", "w185", "w500", "original"])
config.plugins.coverfind.language = ConfigSelection(default="en", choices = ["de", "en", "it", "pl"])
config.plugins.coverfind.filmweb_pl = ConfigYesNo(default = True)

def main(session, service, **kwargs):
    session.open(CoverFindScreen, service, session.current_dialog, **kwargs)

def Plugins(**kwargs):
    return [
            PluginDescriptor(name=_("CoverFind"), description=_("Find Covers ..."), where = PluginDescriptor.WHERE_MOVIELIST, fnc=main),
            ]

def decodeHtml(text):
    text = text.replace('&auml;','ä')
    text = text.replace('\u00e4','ä')
    text = text.replace('&#228;','ä')

    text = text.replace('&Auml;','Ä')
    text = text.replace('\u00c4','Ä')
    text = text.replace('&#196;','Ä')

    text = text.replace('&ouml;','ö')
    text = text.replace('\u00f6','ö')
    text = text.replace('&#246;','ö')

    text = text.replace('\xc3\xb6','ö')
    text = text.replace('\xc3\x96','Ö')
    text = text.replace('\xc3\xbc','ü')
    text = text.replace('\xc3\x9c','Ü')
    text = text.replace('\xc3\xab','ä')
    text = text.replace('\xc3\x84','Ä')

    text = text.replace('&ouml;','Ö')
    text = text.replace('&Ouml;','Ö')
    text = text.replace('\u00d6','Ö')
    text = text.replace('&#214;','Ö')

    text = text.replace('&uuml;','ü')
    text = text.replace('\u00fc','ü')
    text = text.replace('&#252;','ü')

    text = text.replace('&Uuml;','Ü')
    text = text.replace('\u00dc','Ü')
    text = text.replace('&#220;','Ü')

    text = text.replace('&szlig;','ss')
    text = text.replace('\u00df','ss')
    text = text.replace('&#223;','ss')

    return text

def cleanFile(text):
    cutlist = ['x264','720p','1080p','1080i','PAL','GERMAN','ENGLiSH','WS','DVDRiP','UNRATED','RETAIL','Web-DL','DL','LD','MiC','MD','DVDR','BDRiP','BLURAY','DTS','UNCUT','ANiME',
                'AC3MD','AC3','AC3D','TS','DVDSCR','COMPLETE','INTERNAL','DTSD','XViD','DIVX','DUBBED','LINE.DUBBED','DD51','DVDR9','DVDR5','h264','AVC',
                'WEBHDTVRiP','WEBHDRiP','WEBRiP','WEBHDTV','WebHD','HDTVRiP','HDRiP','HDTV','ITUNESHD','REPACK','SYNC']
    text = text.replace('.wmv','').replace('.flv','').replace('.ts','').replace('.m2ts','').replace('.mkv','').replace('.avi','').replace('.mpeg','').replace('.mpg','').replace('.iso','').replace('.mp4','')
    
    for word in cutlist:
        text = re.sub('(\_|\-|\.|\+)'+word+'(\_|\-|\.|\+)','+', text, flags=re.I)
    text = text.replace('.',' ').replace('-',' ').replace('_',' ').replace('+','')

    return text
    
def cleanEnd(text):
    text = text.replace('.wmv','').replace('.flv','').replace('.ts','').replace('.m2ts','').replace('.mkv','').replace('.avi','').replace('.mpeg','').replace('.mpg','').replace('.iso','').replace('.mp4','')
    return text
    
def DecodePLletters(text):
    #durne wpisy od nagran
    text = re.sub('^.*[:-]','', text)
    #polskie litery
    text = text.replace('ą','a').replace('ę','e').replace('ś','s').replace('ć','c').replace('ż','z').replace('ź','z').replace('ł','l').replace('ń','n')
    text = text.replace('Ą','A').replace('Ę','E').replace('Ś','S').replace('Ć','C').replace('Ż','Z').replace('Ź','Z').replace('Ł','L').replace('Ń','N')
    return text.strip()

class PicLoader:
    def __init__(self, width, height, sc=None):
        self.picload = ePicLoad()
        if(not sc):
            sc = AVSwitch().getFramebufferScale()
        self.picload.setPara((width, height, sc[0], sc[1], False, 1, "#ff000000"))

    def load(self, filename):
        self.picload.startDecode(filename, 0, 0, False)
        data = self.picload.getData()
        return data
    
    def destroy(self):
        del self.picload
        
class CoverFindConfigScreen(Screen, ConfigListScreen):
    skin = """
        <screen position="40,80" size="1200,600" title=" " >
            <widget name="info" position="10,10" size="1180,30" font="Regular;24" foregroundColor="#00fff000"/>
            <widget name="config" position="10,60" size="1180,480" transparent="1" scrollbarMode="showOnDemand" />
            <widget name="key_red" position="100,570" size="260,25" transparent="1" font="Regular;20"/>
            <widget name="key_green" position="395,570" size="260,25"  transparent="1" font="Regular;20"/>
            <widget name="key_yellow" position="690,570" size="260,25" transparent="1" font="Regular;20"/>
            <widget name="key_blue" position="985,570" size="260,25" transparent="1" font="Regular;20"/>
            <ePixmap position="70,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CoverFind/pic/button_red.png" transparent="1" alphatest="on"/>
            <ePixmap position="365,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CoverFind/pic/button_green.png" transparent="1" alphatest="on"/>
            <ePixmap position="660,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CoverFind/pic/button_yellow.png" transparent="1" alphatest="on"/>
            <ePixmap position="955,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CoverFind/pic/button_blue.png" transparent="1" alphatest="on"/>
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session

        self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
            "cancel": self.cancel,
            "red": self.cancel,
            "green"    : self.save
        }, -1)

        self['info'] = Label(_("Settings:"))
        self['key_red'] = Label(_("Cancel"))
        self['key_green'] = Label("Ok")
        self['key_yellow'] = Label("")
        self['key_blue'] = Label("")

        self.list = []
        self.createConfigList()
        ConfigListScreen.__init__(self, self.list)

    def createConfigList(self):
        self.setTitle(pname + " (" + pversion + ")")
        self.list = []
        self.list.append(getConfigListEntry(_("Cover resolution TMDB:"), config.plugins.coverfind.themoviedb_coversize))
        self.list.append(getConfigListEntry(_("Search in symlinks:"), config.plugins.coverfind.followsymlink))
        #self.list.append(getConfigListEntry(_("Cover resolution TVDB:"), config.plugins.coverfind.thetvdb_coversize))
        self.list.append(getConfigListEntry(_("Language:"), config.plugins.coverfind.language))
        self.list.append(getConfigListEntry(_("Search in filmweb.pl:"), config.plugins.coverfind.filmweb_pl))

    def changedEntry(self):
        self.createConfigList()
        self["config"].setList(self.list)

    def save(self):
        for x in self["config"].list:
            x[1].save()
        configfile.save()
        self.close()

    def cancel(self):
        self.close()
        
class CoverFindScreen(Screen):
    skin = """
        <screen position="40,80" size="1200,600" title=" " >
            <widget name="searchinfo" position="10,10" size="1180,30" font="Regular;24" foregroundColor="#00fff000"/>
            <widget name="list" position="10,60" size="1180,500" scrollbarMode="showOnDemand"/>
            <widget name="key_red" position="100,570" size="260,25" transparent="1" font="Regular;20"/>
            <widget name="key_green" position="395,570" size="260,25"  transparent="1" font="Regular;20"/>
            <widget name="key_yellow" position="690,570" size="260,25" transparent="1" font="Regular;20"/>
            <widget name="key_blue" position="985,570" size="260,25" transparent="1" font="Regular;20"/>
            <ePixmap position="70,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CoverFind/pic/button_red.png" transparent="1" alphatest="on"/>
            <ePixmap position="365,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CoverFind/pic/button_green.png" transparent="1" alphatest="on"/>
            <ePixmap position="660,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CoverFind/pic/button_yellow.png" transparent="1" alphatest="on"/>
            <ePixmap position="955,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CoverFind/pic/button_blue.png" transparent="1" alphatest="on"/>
        </screen>"""    

    def __init__(self, session, service, parent, args = 0):
        Screen.__init__(self, session, parent = parent)
        self.session = session

        self.isDirectory = False
        serviceHandler = eServiceCenter.getInstance()
        info = serviceHandler.info(service)
        path = service.getPath()
#        if path.endswith(".ts") is True:
#            path = path[:-3]
        self.savePath = path
        self.dir = '/'.join(path.split('/')[:-1]) + '/'
        self.file = self.baseName(path)
        if path.endswith("/") is True:
            path = path[:-1]
            self.file = self.baseName(path)
            self.text = self.baseName(path)
            self.isDirectory = True
        else:
            try:
                self.text = cleanFile(info.getName(service))
            except:
                self.text = _('NOT VIDEO!!!')
            self.descr = ''
            self.orgTitle = ''
            self.UseOrgTitle = False
            if fileExists(self.dir + self.file.replace('.ts','.eit')): 
                self.descr = open(self.dir + self.file.replace('.ts','.eit'), 'r').read(2048)
                if self.descr.find(' oryginalny:') > 1:
                    try:
                        self.orgTitle = re.findall('Tytu. oryginalny:(.*);', self.descr, flags=re.I)[0].strip()
                        self.UseOrgTitle = True
                    except:
                        self.UseOrgTitle = False
                self.descr=''
            self.isDirectory = False

        with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
        printDEBUG('isDirectory=' + str(self.isDirectory), 'init') #DEBUG
        printDEBUG('path=' + path) #DEBUG
        printDEBUG('self.dir=' + str(self.dir), 'init') #DEBUG
        printDEBUG('self.file=' + str(self.file), 'init') #DEBUG   
        printDEBUG('self.text=' + str(self.text), 'init') #DEBUG
        #printDEBUG('self.descr=' + str(self.descr), 'init') #DEBUG
        printDEBUG('self.orgTitle=' + str(self.orgTitle), 'init') #DEBUG

        self.buttonChoice = 0
        
        self["actions"]  = ActionMap(["OkCancelActions", "ColorActions", "ChannelSelectBaseActions"], 
        {
            "red": self.goRed,
            "green": self.goGreen,
            "yellow": self.goYellow,
            "blue": self.setButtonTxt,
            "prevBouquet": self.setButtonTxt,
            "nextBouquet": self.setButtonTxt,            
            "cancel": self.cancel,
            "ok": self.ok,
        }, -1)

        self['searchinfo'] = Label(_("Search for Covers ..."))
        self['key_red'] = Label(_("Cancel"))
        self['key_green'] = Label(_("Search cover manual"))
        self['key_yellow'] = Label(_("Find more covers"))
        self['key_blue'] = Label(_("more"))
        self['list'] = createCoverList()        
        
        self.onLayoutFinish.append(self.onFinish)
        
    def onFinish(self):
        self.setTitle(pname)
        printDEBUG(self.text, "onFinish")
        if re.search('[Ss][0-9]+[Ee][0-9]+', self.text):
            print "[CoverFind] TV Search.."
            printDEBUG(self.text, "onFinish")
            self.text = re.sub('[Ss][0-9]+[Ee][0-9]+.*[a-zA-Z0-9_]+','', self.text, flags=re.S|re.I)
            printDEBUG(self.text, "onFinish")
            self.getCoverTV()
        else:
            print "[CoverFind] TV Movie.."
            self.getCoverMovie()
    
    def setButtonTxt(self):
        if self.buttonChoice == 1:
            self['key_red'].text = _("Cancel")
            self['key_green'].text = _("Search cover manual")
            self['key_yellow'].text = _("Find more covers")
            self['key_blue'].text = _("more")
            self.buttonChoice = 0
        elif self.buttonChoice == 0:
            self['key_red'].text = _("Settings")
            self['key_green'].text = _("Open cover file")
            self['key_yellow'].text = _("Autofind all covers")
            self['key_blue'].text = _("more")
            self.buttonChoice = 1
            
    def goRed(self):
        if self.buttonChoice == 0:
            self.cancel()
        if self.buttonChoice == 1:
            self.session.open(CoverFindConfigScreen)

    def goGreen(self):
        if self.buttonChoice == 0:
            self.manSearch()
        if self.buttonChoice == 1:
            self.fileSearch()
    
    def goYellow(self):
        if self.buttonChoice == 0:
            self.searchSeries()
        if self.buttonChoice == 1:
#            mydir = self.dir
            self.session.open(CoverFindAll, self.dir)            
            
    def manSearch(self):
        self.session.openWithCallback(self.manSearchCB, VirtualKeyBoard, title = (_("Search for Cover:")), text = self.text)    
    
    def manSearchCB(self, text):
        if text:
            print "[CoverFind:manSearchCB] " + text
            self.text = text
            self.getCoverMovie()
            
    def fileSearch(self):
        start_dir = "/tmp/"
        self.session.openWithCallback(self.fileSearchCB, CoverFindFile, start_dir)

    def fileSearchCB(self, res):
        if res:
            print "[CoverFind:fileSearchCB] " + res
            print "[CoverFind:fileSearchCB] " + self.savePath
            extension = res.split('.')
            extension = extension[-1].lower()
            self.savePath = cleanEnd(self.savePath)
            
            if self.isDirectory:
                print "[CoverFind] Folder"
                target = self.savePath + "folder." + extension
                print "[CoverFind] " + target
            else:
                print "[CoverFind] File"
                target = self.savePath + "." + extension
                print "[CoverFind] " + target
            try:        
                shutil.copy(res, target)
            except:
                print "[CoverFind] User rights are not sufficiently!"
            
            self.close(False)
        
    def searchSeries(self):
        #Proceed with search for series cover
        self.getCoverTV()

    def getCoverMovie(self, search4title =''):
        if search4title == '':
            search4title = self.text
        self['searchinfo'].setText(_("Try to find %s in tmdb ...")% search4title)
        url = "http://api.themoviedb.org/3/search/movie?api_key=8789cfd3fbab7dccf1269c3d7d867aff&query=%s&language=%s" % (search4title.replace(' ','%20'),config.plugins.coverfind.language.value)
        printDEBUG("[CoverFind:getCoverMovie] " + url) #DEBUG
        getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.readCoverMovie).addErrback(self.dataError)

    def getCoverTV(self):
        self['searchinfo'].setText(_("Try to find %s in tvdb ...")% self.text)
        url = "http://thetvdb.com/api/GetSeries.php?seriesname=%s&language=%s" % (self.text.replace(' ','%20'),config.plugins.coverfind.language.value)
        printDEBUG("[CoverFind:getCoverTV] " + url) #DEBUG
        getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.readCoverTV).addErrback(self.dataError)

    def getFromWebfilmPL(self):
        self['searchinfo'].setText(_("Try to find %s in webfilm.pl ...")% self.text)
        url = "http://www.filmweb.pl/search/film?q=%s" % (DecodePLletters(self.text).replace(' ','%20'))
        printDEBUG("[CoverFind:getFromWebfilmPL] " + url) #DEBUG
        getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.readFromWebfilmPL).addErrback(self.dataError)

    def readFromWebfilmPL(self, data):
        self.piclist = []
        urls = []
        #printDEBUG(data)
        list = re.findall('<li id="film_(.*?)">.*<img src="(.*.jpg)">', data, re.S)
        
        if list:
            for id,coverPath in list:
                urls.append((self.text, coverPath, id))

        printDEBUG("Number of covers: %d" % len(urls))
        if len(urls) != 0:
            ds = defer.DeferredSemaphore(tokens=2)
            downloads = [ds.run(self.download, url, title).addCallback(self.buildList,title,url,id,"movie").addErrback(self.dataError) for title,url,id in urls]
            finished = defer.DeferredList(downloads).addErrback(self.dataError)
            self['searchinfo'].setText(_("Found for: %s") % self.text)
        else:
            self['searchinfo'].setText(_("%s not found.") % self.text)

    def readCoverMovie(self, data):
        self.piclist = []
        urls = []
        list = re.findall('"id":(.*?),.*?original_title":"(.*?)".*?"poster_path":"(.*?)".*?title":"(.*?)"', data, re.S)
        if list:
            for id,otitle,coverPath,title in list:
                coverUrl = "http://image.tmdb.org/t/p/%s%s" % (config.plugins.coverfind.themoviedb_coversize.value, coverPath)
                print "[CoverFind] " + title, coverUrl
                urls.append((title, coverUrl, id))

        if len(urls) != 0:
            ds = defer.DeferredSemaphore(tokens=2)
            downloads = [ds.run(self.download, url, title).addCallback(self.buildList,title,url,id,"movie").addErrback(self.dataError) for title,url,id in urls]
            finished = defer.DeferredList(downloads).addErrback(self.dataError)
            if self.orgTitle == '':
                self['searchinfo'].setText(_("Found for: %s") % self.text)
            else:
                self['searchinfo'].setText(_("Found for: %s") % (self.text + '/' + self.orgTitle))
        else:
            if self.UseOrgTitle == True:
                self.UseOrgTitle = False
                #self.text = self.orgTitle
                printDEBUG("Searching for orgTitle=" + self.text)
                self.getCoverMovie(self.orgTitle)
                return
            elif config.plugins.coverfind.filmweb_pl.value == True:
                self.getFromWebfilmPL()
                return
            self['searchinfo'].setText(_("%s not found.") % self.text)

    def readCoverTV(self, data):
        self.piclist = []
        urls = []
        tv = re.findall('<seriesid>(.*?)</seriesid>.*?<SeriesName>(.*?)</SeriesName>', data, re.S)
        if tv:
            for id,title in tv:
                coverUrl1 = "http://www.thetvdb.com/banners/_cache/posters/%s-1.jpg" % str(id)
                coverUrl2 = "http://www.thetvdb.com/banners/_cache/posters/%s-2.jpg" % str(id)
                coverUrl3 = "http://www.thetvdb.com/banners/_cache/posters/%s-3.jpg" % str(id)
                print "[CoverFind] " + title, coverUrl1
                urls.append((title, coverUrl1, id, "1"))
                urls.append((title, coverUrl2, id, "2"))
                urls.append((title, coverUrl3, id, "3"))

        if len(urls):
            ds = defer.DeferredSemaphore(tokens=2)
            downloads = [ds.run(self.download2, url, title, count).addCallback(self.buildList2,title,url,id,"tv",count).addErrback(self.dataError) for title,url,id,count in urls]
            finished = defer.DeferredList(downloads).addErrback(self.dataError)
            self['searchinfo'].setText(_("Found for: %s") % self.text)
        else:
            self['searchinfo'].setText(_("%s not found.") % self.text)

    def dataError(self, error):
        print "[CoverFind] " + "ERROR:", error

    def download(self, url, title):
        return downloadPage(url, '/tmp/'+title+'.jpg')

    def download2(self, url, title, count):
        return downloadPage(url, '/tmp/'+title+count+'.jpg')
        
    def buildList(self, data, title, url, id, type):
        self.piclist.append(((title, '/tmp/'+title+'.jpg', id, type),))
        self['list'].setList(self.piclist, 'Test')

    def buildList2(self, data, title, url, id, type, count):
        self.piclist.append(((title, '/tmp/'+title+count+'.jpg', id, type),))
        self['list'].setList(self.piclist, 'Test')

    def ok(self):
        check = self['list'].getCurrent()
        if check == None:
            return

        bild = self['list'].getCurrent()[1]
        idx = self['list'].getCurrent()[2]
        type = self['list'].getCurrent()[3]
        self.savePath = cleanEnd(self.savePath)

        if fileExists(bild):
            if self.isDirectory == True:
                try:
                    shutil.move(bild, self.savePath + "folder.jpg")
                except:
                    print "[CoverFind] User rights are not sufficiently!"
            else:
                try:
                    shutil.move(bild, self.savePath + ".jpg")
                except:
                    print "[CoverFind] User rights are not sufficiently!"

        iurl = "http://api.themoviedb.org/3/movie/%s?api_key=8789cfd3fbab7dccf1269c3d7d867aff&language=%s" % (idx,config.plugins.coverfind.language.value)
        print "[CoverFind] " + iurl
        getPage(iurl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getInfos, type).addErrback(self.dataError2)

    def getInfos(self, data, type):
        if type == "movie":
            infos = re.findall('"genres":\[(.*?)\].*?"overview":"(.*?)",', data, re.S)
            if infos:
                (genres, desc) = infos[0]
                genre = re.findall('"name":"(.*?)"', genres, re.S)
                genre = str(genre).replace('\'','').replace('[','').replace(']','')
                #print "beschreibung:", desc
                self.writeTofile(desc)

        elif type == "tv":
            infos = re.findall('<Overview>(.*?)</Overview>', data, re.S)
            if infos:
                desc = infos[0]
                #print "beschreibung:", desc
                self.writeTofile(desc)

        self.close(False)

    def writeTofile(self, text):
        if not self.savePath.endswith("/"):
            if not fileExists(self.savePath+".txt"):
                wFile = open(self.savePath+".txt","w") 
                wFile.write(text) 
                wFile.close()
            else:
                print "[CoverFind] %s exist" % (self.savePath+".txt")
        else:
            print "[CoverFind] %s is a directory" % (self.savePath)

    def dataError(self, error):
        print error

    def dataError2(self, error):
        print error
        self.close(False)

    def cancel(self):
        self.close(False)
        
    def baseName(self, str):
        name = str.split('/')[-1]
        return name

class CoverFindAll(Screen):
    skin = """
        <screen position="40,80" size="1200,600" title=" " >
            <widget name="searchinfo" position="10,10" size="1180,30" font="Regular;24" foregroundColor="#00fff000"/>
            <widget name="list" position="10,60" size="800,480" scrollbarMode="showOnDemand"/>
            <widget name="cover" position="850,90" size="300,420" alphatest="blend"/>
            <widget name="key_red" position="100,570" size="260,25" transparent="1" font="Regular;20"/>
            <widget name="key_green" position="395,570" size="260,25"  transparent="1" font="Regular;20"/>
            <widget name="key_yellow" position="690,570" size="260,25" transparent="1" font="Regular;20"/>
            <widget name="key_blue" position="985,570" size="260,25" transparent="1" font="Regular;20"/>
            <ePixmap position="70,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CoverFind/pic/button_red.png" transparent="1" alphatest="on"/>
            <ePixmap position="365,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CoverFind/pic/button_green.png" transparent="1" alphatest="on"/>
            <ePixmap position="660,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CoverFind/pic/button_yellow.png" transparent="1" alphatest="on"/>
            <ePixmap position="955,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CoverFind/pic/button_blue.png" transparent="1" alphatest="on"/>
        </screen>"""

    def __init__(self, session, servicepath):
        Screen.__init__(self, session)
        self.session = session

        self["actions"]  = ActionMap(["OkCancelActions", "ShortcutActions", "WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions", "EPGSelectActions"], {
            "cancel": self.cancel,
            "green" : self.goGreen,
            "left"  : self.keyLeft,
            "right" : self.keyRight,
            "up"    : self.keyUp,
            "down"  : self.keyDown
        }, -1)

        self['searchinfo'] = Label("")
        self['cover'] = Pixmap()
        self['key_red'] = Label(_("Cancel"))
        self['key_green'] = Label(_("Find all Covers"))
        self['key_yellow'] = Label("")
        self['key_blue'] = Label("")
        self['list'] = createCoverFindList()

        #self.onFirstExecBegin.append(self.start)
        self.mypath = servicepath
        self.onLayoutFinish.append(self.onFinish)
        
    def onFinish(self):
        self.setTitle(pname)
        self.getFileList()

    def getFileList(self):
        self['searchinfo'].setText(_("Scanning folders: %s") % str(self.mypath))
#        os.system('echo %s %s > /tmp/test.log' % ("findcoverscreen dir : ", str(self.mypath)))
        data = []
        symlinks_dupe = []
#        for root, dirs, files in os.walk("/media/hdd/movie/", topdown=False, onerror=None, followlinks=True):
        for root, dirs, files in os.walk(self.mypath, topdown=False, onerror=None, followlinks=config.plugins.coverfind.followsymlink.value):
            if not root.endswith('/'):
                root += "/"
            slink = os.path.realpath(root)
            if not slink in symlinks_dupe:
                symlinks_dupe.append(slink)
            else:
                print "[CoverFind] Search looping.."
                break

            for file in files:
                filename = os.path.join(root, file)
                if os.path.isdir(filename):
                    data.append(('dir', 'movie', filename, file))
                else:    
                    if file.endswith('.wmv') or file.endswith('.avi') or file.endswith('.divx') or file.endswith('.flv') or file.endswith('.iso') or file.endswith('.ISO') or file.endswith('.m2ts') or file.endswith('.m4v') or file.endswith('.mov') or file.endswith('.mp4') or file.endswith('.mpg') or file.endswith('.mpeg') or file.endswith('.mkv') or file.endswith('.vob'):
                        cleanTitle = cleanFile(file)
                        if re.search('[Ss][0-9]+[Ee][0-9]+', file) is not None:
                            data.append(('file', 'serie', filename, cleanTitle))
                        else:
                            data.append(('file', 'movie', filename, cleanTitle))

                    elif file.endswith('.ts'):
                        #print '[CoverFind] .ts File '+ file
                        if re.search('^[0-9]{8} [0-9]{4}', file):
                            cleanTitle = re.sub('^.*? - .*? - ', '', file)
                        else:
                            cleanTitle = re.sub('^.*? - ', '', file)
                        cleanTitle = re.sub('[.]ts', '', cleanTitle)
                        #print '[CoverFind] .ts Cleaned '+ cleanTitle
                        if re.search('[Ss][0-9]+[Ee][0-9]+', file) is not None:
                            #print "ts "+cleanTitle
                            cleanTitle = re.sub('[Ss][0-9]+[Ee][0-9]+.*[a-zA-Z0-9_]+','', cleanTitle, flags=re.S|re.I)
                            data.append(('file', 'serie', filename, cleanTitle))
                        else:
                            #print "movie "+cleanTitle
                            data.append(('file', 'movie', filename, cleanTitle))

        self.count = len(data)
        self.data = data
        filenumber = str(self.count)
        print "[coverFind] found %s entries" % str(self.count)
        if self.count != 0:
            self['searchinfo'].setText(_("%s movie files without covers found!") % str(self.count))
                
    def goGreen(self):    
        if self.count != 0:
            data = self.data
            urls = []
            self.guilist = []
            self.counting = 0
            for which,type,filename,cleanTitle in data:
                if type == "movie":
                    url = 'http://api.themoviedb.org/3/search/movie?api_key=8789cfd3fbab7dccf1269c3d7d867aff&query=%s&language=%s' % (cleanTitle.replace(' ','%20'),config.plugins.coverfind.language.value)
                    urls.append((type, filename, url, cleanTitle, None, None))
                elif type == "serie":
                    season = None
                    episode = None
                    seasonEpisode = re.findall('.*?[Ss]([0-9]+)[Ee]([0-9]+)', cleanTitle, re.S|re.I)
                    if seasonEpisode:
                        (season, episode) = seasonEpisode[0]
                    name2 = re.sub('[Ss][0-9]+[Ee][0-9]+.*[a-zA-Z0-9_]+','', cleanTitle, flags=re.S|re.I)
                    url = 'http://thetvdb.com/api/GetSeries.php?seriesname=%s&language=%s' % (name2.replace(' ','%20'),config.plugins.coverfind.language.value)
                    urls.append((type, filename, url, cleanTitle, season, episode))
                else:
                    self.counting = int(self.counting) + 1

            if len(urls) != 0:
                ds = defer.DeferredSemaphore(tokens=2)
                downloads = [ds.run(self.download, url).addCallback(self.parseWebpage, type, filename, url, cleanTitle, season, episode).addErrback(self.dataError) for type, filename, url, cleanTitle, season, episode in urls]
                finished = defer.DeferredList(downloads).addErrback(self.dataError2)
            else:
                self['searchinfo'].setText(_("No Movies found!"))

    def parseWebpage(self, data, type, filename, url, cleanTitle, season, episode):
        self.counting = int(self.counting) + 1

        if type == "movie":
            list = []
            list = re.findall('original_title":"(.*?)".*?"poster_path":"(.*?)"', data, re.S)
            if list:
                #purl = "http://image.tmdb.org/t/p/w185"+list[0][1]
                purl = "http://image.tmdb.org/t/p/%s%s" % (config.plugins.coverfind.themoviedb_coversize.value, list[0][1])
                self.guilist.append(((cleanTitle, True, filename),))
                cfilename = cleanEnd(filename)
                if not fileExists(cfilename+".jpg"):
                    downloadPage(purl, cfilename+'.jpg').addErrback(self.dataError)
            else:
                self.guilist.append(((cleanTitle, False, filename),))

            # get description
            idx = []
            idx = re.findall('"id":(.*?),', data, re.S)
            if idx:
                iurl = "http://api.themoviedb.org/3/movie/%s?api_key=8789cfd3fbab7dccf1269c3d7d867aff&language=%s" % (idx[0],config.plugins.coverfind.language.value)
                getPage(iurl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getInfos, id, type, cfilename).addErrback(self.dataError)

        elif type == "serie":
            list = []
            list = re.findall('<seriesid>(.*?)</seriesid>', data, re.S)
            if list:
                purl = "http://www.thetvdb.com/banners/_cache/posters/%s-1.jpg" % list[0]
                self.guilist.append(((cleanTitle, True, filename),))
                cfilename = cleanEnd(filename)
                if not fileExists(cfilename+".jpg"):
                    downloadPage(purl, cfilename+'.jpg').addErrback(self.dataError)

                # get description
                if season and episode:
                    iurl = "http://www.thetvdb.com/api/2AAF0562E31BCEEC/series/%s/default/%s/%s/de.xml" % (list[0], str(int(season)), str(int(episode)))
                    getPage(iurl, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getInfos, id, type, cfilename).addErrback(self.dataError)
            else:
                self.guilist.append(((cleanTitle, False, filename),))

        self['list'].setList(self.guilist, "TEST")
        self['searchinfo'].setText(_("Cover search runs: %s / %s") % (str(self.counting), str(self.count).replace('(','').replace(')','').replace(',','')))

        if int(self.counting) == int(str(self.count).replace('(','').replace(')','').replace(',','')):
            self['searchinfo'].setText(_("Cover search done!"))
    
    def getInfos(self, data, id, type, cfilename):
        self.savePath = cfilename
        if type == "movie":
            infos = re.findall('"genres":\[(.*?)\].*?"overview":"(.*?)"', data, re.S)
            if infos:
                (genres, desc) = infos[0]
                self.writeTofile(decodeHtml(desc))

        elif type == "serie":
            infos = re.findall('<Overview>(.*?)</Overview>', data, re.S)
            if infos:
                desc = infos[0]
                self.writeTofile(decodeHtml(desc))

    def writeTofile(self, text):
        if not fileExists(self.savePath+".txt"):
            wFile = open(self.savePath+".txt","w") 
            wFile.write(text) 
            wFile.close()

    def dataError(self, error):
        print "ERROR:", error

    def dataError2(self, error):
        self.counting = int(self.counting) + 1
        print "ERROR:", error

    def download(self, url):
        return getPage(url, timeout=20, headers={'Accept': 'application/json'})

    def getInfo(self):
        filename = self['list'].getCurrent()[2]
        cfilename = cleanEnd(filename)
        self.showCover(cfilename+".jpg")

    def showCover(self, coverName):
        self.picload = ePicLoad()
        if not fileExists(coverName):
            coverName = "/usr/lib/enigma2/python/Plugins/Extensions/CoverFind/pic/no_cover.png"

        if fileExists(coverName):
            self['cover'].instance.setPixmap(gPixmapPtr())
            scale = AVSwitch().getFramebufferScale()
            size = self['cover'].instance.size()
            self.picload.setPara((size.width(), size.height(), scale[0], scale[1], False, 1, "#FF000000"))
            if self.picload.startDecode(coverName, 0, 0, False) == 0:
                ptr = self.picload.getData()
                if ptr != None:
                    self['cover'].instance.setPixmap(ptr)
                    self['cover'].show()
            del self.picload

    def keyLeft(self):
        check = self['list'].getCurrent()
        if check == None:
            return
        self['list'].pageUp()
        self.getInfo()

    def keyRight(self):
        check = self['list'].getCurrent()
        if check == None:
            return
        self['list'].pageDown()
        self.getInfo()

    def keyDown(self):
        check = self['list'].getCurrent()
        if check == None:
            return
        self['list'].down()
        self.getInfo()

    def keyUp(self):
        check = self['list'].getCurrent()
        if check == None:
            return
        self['list'].up()
        self.getInfo()

    def cancel(self):
        self.close()

class createCoverFindList(GUIComponent, object):
    GUI_WIDGET = eListbox
    
    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.l.setFont(0, gFont('Regular', 22))
        self.l.setItemHeight(30)
        self.l.setBuildFunc(self.buildList)

    def buildList(self, entry):
        width = self.l.getItemSize().width()
        (name, coverFound, filename) = entry
        res = [ None ]

        if coverFound:
            truePath = "/usr/lib/enigma2/python/Plugins/Extensions/CoverFind/pic/cover_yes.png"
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 10, 1, 25, 25, loadPNG(truePath)))
        else:
            falsePath = "/usr/lib/enigma2/python/Plugins/Extensions/CoverFind/pic/cover_no.png"
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 10, 1, 25, 25, loadPNG(falsePath)))

        res.append((eListboxPythonMultiContent.TYPE_TEXT, 50, 0, 1280, 30, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, str(name)))
        return res

    def getCurrent(self):
        cur = self.l.getCurrentSelection()
        return cur and cur[0]

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        self.instance.setWrapAround(True)

    def preWidgetRemove(self, instance):
        instance.setContent(None)

    def setList(self, list, type):
        self.type = type
        self.l.setList(list)

    def moveToIndex(self, idx):
        self.instance.moveSelectionTo(idx)

    def getSelectionIndex(self):
        return self.l.getCurrentSelectionIndex()

    def getSelectedIndex(self):
        return self.l.getCurrentSelectionIndex()

    def selectionEnabled(self, enabled):
        if self.instance is not None:
            self.instance.setSelectionEnable(enabled)

    def pageUp(self):
        if self.instance is not None:
            self.instance.moveSelection(self.instance.pageUp)

    def pageDown(self):
        if self.instance is not None:
            self.instance.moveSelection(self.instance.pageDown)

    def up(self):
        if self.instance is not None:
            self.instance.moveSelection(self.instance.moveUp)

    def down(self):
        if self.instance is not None:
            self.instance.moveSelection(self.instance.moveDown)

class createCoverList(GUIComponent, object):
    GUI_WIDGET = eListbox
    
    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.l.setFont(0, gFont('Regular', 22))
        self.l.setItemHeight(138)
        self.l.setBuildFunc(self.buildList)

    def buildList(self, entry):
        width = self.l.getItemSize().width()
        (title, bild, id, type) = entry
        res = [ None ]

        self.picloader = PicLoader(92, 138)
        bild = self.picloader.load(bild)
        #color, color_sel, backcolor, backcolor_sel
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 0, 0, 138, 138, bild))
        self.picloader.destroy()
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 150, 0, 1280, 30, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, str(title)))
        return res

    def getCurrent(self):
        cur = self.l.getCurrentSelection()
        return cur and cur[0]

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        self.instance.setWrapAround(True)

    def preWidgetRemove(self, instance):
        instance.setContent(None)

    def setList(self, list, type):
        self.type = type
        self.l.setList(list)

    def moveToIndex(self, idx):
        self.instance.moveSelectionTo(idx)

    def getSelectionIndex(self):
        return self.l.getCurrentSelectionIndex()

    def getSelectedIndex(self):
        return self.l.getCurrentSelectionIndex()

    def selectionEnabled(self, enabled):
        if self.instance is not None:
            self.instance.setSelectionEnable(enabled)

    def pageUp(self):
        if self.instance is not None:
            self.instance.moveSelection(self.instance.pageUp)

    def pageDown(self):
        if self.instance is not None:
            self.instance.moveSelection(self.instance.pageDown)

    def up(self):
        if self.instance is not None:
            self.instance.moveSelection(self.instance.moveUp)

    def down(self):
        if self.instance is not None:
            self.instance.moveSelection(self.instance.moveDown)

class CoverFindFile(Screen):
    skin = """
        <screen position="40,80" size="1200,600" title=" " >
            <widget name="media" position="10,10" size="1180,30" font="Regular;24" foregroundColor="#00fff000"/>
            <widget name="filelist" position="10,60" size="800,480" scrollbarMode="showOnDemand"/>
            <widget name="picture" position="850,90" size="300,420" alphatest="blend"/>
            <widget name="key_red" position="100,570" size="260,25" transparent="1" font="Regular;20"/>
            <widget name="key_green" position="395,570" size="260,25"  transparent="1" font="Regular;20"/>
            <widget name="key_yellow" position="690,570" size="260,25" transparent="1" font="Regular;20"/>
            <ePixmap position="70,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CoverFind/pic/button_red.png" transparent="1" alphatest="on"/>
            <ePixmap position="365,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CoverFind/pic/button_green.png" transparent="1" alphatest="on"/>
            <ePixmap position="660,570" size="260,25" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CoverFind/pic/button_yellow.png" transparent="1" alphatest="on"/>
        </screen>"""

    def __init__(self, session, initDir, plugin_path = None):
        Screen.__init__(self, session)
        #self.skin_path = plugin_path
        self["filelist"] = FileList(initDir, inhibitMounts = False, inhibitDirs = False, showMountpoints = False, matchingPattern = "(?i)^.*\.(jpg|png)")
        self["media"] = Label()
        self["picture"] = Pixmap()
        
        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions", "EPGSelectActions"],
        {
            "back": self.cancel,
            "left": self.left,
            "right": self.right,
            "up": self.up,
            "down": self.down,
            "ok": self.ok,
            "yellow": self.yellow,
            "green": self.green,
            "red": self.cancel
        }, -1)

        self.title=_("Select a cover file")
        try:
            self["title"]=StaticText(self.title)
        except:
            print 'self["title"] was not found in skin'    
            
        self['key_red'] = Label(_("Cancel"))
        self['key_green'] = Label(_("Select Cover"))
        self['key_yellow'] = Label(_("Delete cover"))

    def cancel(self):
        self.close(None)

    def green(self):
        if self["filelist"].getSelection()[1] == True:
            self["media"].setText(_("Invalid choice!"))
        else:
            directory = self["filelist"].getCurrentDirectory()
            if (directory.endswith("/")):
                self.fullpath = self["filelist"].getCurrentDirectory() + self["filelist"].getFilename()
            else:
                self.fullpath = self["filelist"].getCurrentDirectory() + "/" + self["filelist"].getFilename()
            self.close(self.fullpath)

    def yellow(self):
        if self["filelist"].getSelection()[1] == True:
            self["media"].setText(_("Invalid choice!"))
        else:
            print "[CoverFind] remove " + self.fullpath
            remove(self.fullpath)
            self["filelist"].refresh()
            self.updateFile()
            
    def up(self):
        self["filelist"].up()
        self.updateFile()

    def down(self):
        self["filelist"].down()
        self.updateFile()

    def left(self):
        self["filelist"].pageUp()
        self.updateFile()

    def right(self):
        self["filelist"].pageDown()
        self.updateFile()

    def ok(self):
        if self["filelist"].canDescent():
            self["filelist"].descent()
            self.updateFile()

    def updateFile(self):
        currFolder = self["filelist"].getSelection()[0]
        if self["filelist"].getFilename() is not None:
            directory = self["filelist"].getCurrentDirectory()
            if (directory.endswith("/")):
                self.fullpath = self["filelist"].getCurrentDirectory() + self["filelist"].getFilename()
            else:
                self.fullpath = self["filelist"].getCurrentDirectory() + "/" + self["filelist"].getFilename()
            
            self["media"].setText(self["filelist"].getFilename())

        else:
            currFolder = self["filelist"].getSelection()[0]
            if currFolder is not None:
                self["media"].setText(currFolder)
            else:
                self["media"].setText(_("Invalid choice!"))

        print "[CoverFind] " + self.fullpath        
        self.showPreview(self.fullpath)

    def showPreview(self, pic):
        if pic:
            jpgpath = pic
            if jpgpath and os.path.exists(jpgpath):
                sc = AVSwitch().getFramebufferScale()
                size = self["picture"].instance.size()
                self.picload = ePicLoad()
                self.picload.PictureData.get().append(self.showPreviewCB)
                if self.picload:
                    self.picload.setPara((size.width(), size.height(), sc[0], sc[1], False, 1, "#00000000"))
                    if self.picload.startDecode(jpgpath) != 0:
                        del self.picload
            else:
                self["picture"].hide()
        else:
            self["picture"].hide()

    def showPreviewCB(self, picInfo=None):
        if self.picload and picInfo:
            ptr = self.picload.getData()
            if ptr != None:
                self["picture"].instance.setPixmap(ptr)
                self["picture"].show()
            del self.picload

# FileList mod
EXTENSIONS = {"jpg": "picture",    "png": "picture"}
        
def FileEntryComponent(name, absolute = None, isDir = False):
    res = [ (absolute, isDir) ]
    res.append((eListboxPythonMultiContent.TYPE_TEXT, 35, 1, 1280, 30, 0, RT_HALIGN_LEFT, name))
    if isDir:
        png = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "extensions/directory.png"))
    else:
        extension = name.split('.')
        extension = extension[-1].lower()
        if EXTENSIONS.has_key(extension):
            png = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "extensions/" + EXTENSIONS[extension] + ".png"))
        else:
            png = None
    if png is not None:
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 10, 5, 20, 20, png))
    
    return res

class FileList(MenuList):
    def __init__(self, directory, showDirectories = True, showFiles = True, showMountpoints = True, matchingPattern = None, useServiceRef = False, inhibitDirs = False, inhibitMounts = False, isTop = False, enableWrapAround = False, additionalExtensions = None):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.additional_extensions = additionalExtensions
        self.mountpoints = []
        self.current_directory = None
        self.current_mountpoint = None
        self.useServiceRef = useServiceRef
        self.showDirectories = showDirectories
        self.showMountpoints = showMountpoints
        self.showFiles = showFiles
        self.isTop = isTop
        # example: matching .nfi and .ts files: "^.*\.(nfi|ts)"
        self.matchingPattern = matchingPattern
        self.inhibitDirs = inhibitDirs or []
        self.inhibitMounts = inhibitMounts or []

        self.refreshMountpoints()
        self.changeDir(directory)
        self.l.setFont(0, gFont("Regular", 22))
        self.l.setItemHeight(30)
        self.serviceHandler = eServiceCenter.getInstance()

    def refreshMountpoints(self):
        self.mountpoints = [os_path.join(p.mountpoint, "") for p in harddiskmanager.getMountedPartitions()]
        self.mountpoints.sort(reverse = True)

    def getMountpoint(self, file):
        file = os_path.join(os_path.realpath(file), "")
        for m in self.mountpoints:
            if file.startswith(m):
                return m
        return False

    def getMountpointLink(self, file):
        if os_path.realpath(file) == file:
            return self.getMountpoint(file)
        else:
            if file[-1] == "/":
                file = file[:-1]
            mp = self.getMountpoint(file)
            last = file
            file = os_path.dirname(file)
            while last != "/" and mp == self.getMountpoint(file):
                last = file
                file = os_path.dirname(file)
            return os_path.join(last, "")

    def getSelection(self):
        if self.l.getCurrentSelection() is None:
            return None
        return self.l.getCurrentSelection()[0]

    def getCurrentEvent(self):
        l = self.l.getCurrentSelection()
        if not l or l[0][1] == True:
            return None
        else:
            return self.serviceHandler.info(l[0][0]).getEvent(l[0][0])

    def getFileList(self):
        return self.list

    def inParentDirs(self, dir, parents):
        dir = os_path.realpath(dir)
        for p in parents:
            if dir.startswith(p):
                return True
        return False

    def changeDir(self, directory, select = None):
        self.list = []

        # if we are just entering from the list of mount points:
        if self.current_directory is None:
            if directory and self.showMountpoints:
                self.current_mountpoint = self.getMountpointLink(directory)
            else:
                self.current_mountpoint = None
        self.current_directory = directory
        directories = []
        files = []

        if directory is None and self.showMountpoints: # present available mountpoints
            for p in harddiskmanager.getMountedPartitions():
                path = os_path.join(p.mountpoint, "")
                if path not in self.inhibitMounts and not self.inParentDirs(path, self.inhibitDirs):
                    self.list.append(FileEntryComponent(name = p.description, absolute = path, isDir = True))
            files = [ ]
            directories = [ ]
        elif directory is None:
            files = [ ]
            directories = [ ]
        elif self.useServiceRef:
            root = eServiceReference("2:0:1:0:0:0:0:0:0:0:" + directory)
            if self.additional_extensions:
                root.setName(self.additional_extensions)
            serviceHandler = eServiceCenter.getInstance()
            list = serviceHandler.list(root)

            while 1:
                s = list.getNext()
                if not s.valid():
                    del list
                    break
                if s.flags & s.mustDescent:
                    directories.append(s.getPath())
                else:
                    files.append(s)
            directories.sort()
            files.sort()
        else:
            if fileExists(directory):
                try:
                    files = listdir(directory)
                except:
                    files = []
                files.sort()
                tmpfiles = files[:]
                for x in tmpfiles:
                    if os_path.isdir(directory + x):
                        directories.append(directory + x + "/")
                        files.remove(x)

        if directory is not None and self.showDirectories and not self.isTop:
            if directory == self.current_mountpoint and self.showMountpoints:
                self.list.append(FileEntryComponent(name = "<" +_("List of Storage Devices") + ">", absolute = None, isDir = True))
            elif (directory != "/") and not (self.inhibitMounts and self.getMountpoint(directory) in self.inhibitMounts):
                self.list.append(FileEntryComponent(name = "<" +_("Parent Directory") + ">", absolute = '/'.join(directory.split('/')[:-2]) + '/', isDir = True))

        if self.showDirectories:
            for x in directories:
                if not (self.inhibitMounts and self.getMountpoint(x) in self.inhibitMounts) and not self.inParentDirs(x, self.inhibitDirs):
                    name = x.split('/')[-2]
                    self.list.append(FileEntryComponent(name = name, absolute = x, isDir = True))

        if self.showFiles:
            for x in files:
                if self.useServiceRef:
                    path = x.getPath()
                    name = path.split('/')[-1]
                else:
                    path = directory + x
                    name = x

                if (self.matchingPattern is None) or re_compile(self.matchingPattern).search(path):
                    self.list.append(FileEntryComponent(name = name, absolute = x , isDir = False))

        if self.showMountpoints and len(self.list) == 0:
            self.list.append(FileEntryComponent(name = _("nothing connected"), absolute = None, isDir = False))

        self.l.setList(self.list)

        if select is not None:
            i = 0
            self.moveToIndex(0)
            for x in self.list:
                p = x[0][0]
                
                if isinstance(p, eServiceReference):
                    p = p.getPath()
                
                if p == select:
                    self.moveToIndex(i)
                i += 1

    def getCurrentDirectory(self):
        return self.current_directory

    def canDescent(self):
        if self.getSelection() is None:
            return False
        return self.getSelection()[1]

    def descent(self):
        if self.getSelection() is None:
            return
        self.changeDir(self.getSelection()[0], select = self.current_directory)

    def getFilename(self):
        if self.getSelection() is None:
            return None
        x = self.getSelection()[0]
        if isinstance(x, eServiceReference):
            x = x.getPath()
        return x

    def getServiceRef(self):
        if self.getSelection() is None:
            return None
        x = self.getSelection()[0]
        if isinstance(x, eServiceReference):
            return x
        return None

    def execBegin(self):
        harddiskmanager.on_partition_list_change.append(self.partitionListChanged)

    def execEnd(self):
        harddiskmanager.on_partition_list_change.remove(self.partitionListChanged)

    def refresh(self):
        idx = self.l.getCurrentSelectionIndex()
        self.changeDir(self.current_directory, self.getFilename())
        self.moveToIndex(idx-1)

    def partitionListChanged(self, action, device):
        self.refreshMountpoints()
        if self.current_directory is None:
            self.refresh()
