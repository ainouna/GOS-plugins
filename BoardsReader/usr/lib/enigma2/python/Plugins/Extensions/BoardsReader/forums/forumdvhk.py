# -*- coding: utf-8 -*-
###################################################
# LOCAL import
###################################################
from Plugins.Extensions.BoardsReader.ihost import IHost, CDisplayListItem, RetHost, CUrlItem
import Plugins.Extensions.BoardsReader.libs.pCommon as pCommon
from Plugins.Extensions.BoardsReader.libs.vbulletin import GetWebPage, GetDVHKforumContent, GetForumsList, GetThreadsList, GetFullThread as vb_GetFullThread
try:
    from Components.LanguageGOS import gosgettext as _ 
except:
    from ..libs.tools import TranslateTXT as _

###################################################
# FOREIGN import
###################################################
import urllib2
from sys import exc_info
import xml.etree.cElementTree
import os
from Components.config import config, getConfigListEntry, ConfigText
import re
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, fileExists

###################################################
# Config options for HOST
###################################################
config.plugins.BoardReader.dvhk_login = ConfigText(default = "", fixed_size = False)
config.plugins.BoardReader.dvhk_password = ConfigText(default = "", fixed_size = False)
config.plugins.BoardReader.dvhk_BlockedIDs = ConfigText(default = "7,8,98,31,19,17,103", fixed_size = False)

def gettytul():
    return "DVHK (http://forum.dvhk.to)"

def getpicon():
    return "icons/MENU-dvhk.png"

def GetConfigList():
    optionList = []
    optionList.append(getConfigListEntry(_("login:"), config.plugins.BoardReader.dvhk_login))
    optionList.append(getConfigListEntry(_("password:"), config.plugins.BoardReader.dvhk_password))
    optionList.append(getConfigListEntry(_("Blocked subforums IDs:"), config.plugins.BoardReader.dvhk_BlockedIDs))
    return optionList

def compare(item1, item2):
    name1 = item1.name.lower()
    name2 = item2.name.lower()
    
    if name1 < name2:
        return -1
    elif name1 > name2:
        return 1
    else:
        return 0

class MyHost(IHost):
    PATH_TO_LOGO = resolveFilename(SCOPE_PLUGINS, 'Extensions/BoardsReader/icons/dvhklogo.png')
    
    #{'Name': 'OGÓLNE TV-SAT', 'Desc': '', 'IMG': '', 'catURL': '/forumdisplay.php?f=3', 'CatLIST': [],, 'forumlevel': (0-2) },
    TREE_TAB = []
    CURRENT_TAB = []

    TREE_LEVEL = 0
    TREE_LEVEL_IDs = [0,0,0,0,0]
    #dla wygody, aby numeracja kategorii zgadzala sie z indeksami z listy
    
    mainurl='http://forum.dvhk.to'
    forumurl='/forumdisplay.php?f=' #i jako parametr zawierajacy numer forum
    threadurl='/showthread.php?t=' #i jako parametr zawierajacy numer forum
    threadLastPage='&page=999'
    dailyURL='/search.php?do=getdaily'
    username = ''
    password = ''
    BlockedIDs = ''
    WebPage = ''
    StartWebPage = ""
    Lista_Forums = []
    Lista_Threads = []
    
    # ERROR = {'Error': 0, 'Message': }
    def __init__(self):
        # urls
        self.DBG = True
        COOKIEFILE = resolveFilename(SCOPE_PLUGINS, 'Extensions/BoardsReader/cache/') + 'dvhk.cookie'
        
        # for grouped urllist.txt
        self.catDict = None
        self.categoryList = [] # 'LEKTOR', 'KOMEDIA'
        self.currIndex = 0
        
        # for search
        self.cm = pCommon.common()
        self.searchPattern = ''
        
        self.username = config.plugins.BoardReader.dvhk_login.value
        self.password = config.plugins.BoardReader.dvhk_password.value
        self.BlockedIDs = config.plugins.BoardReader.dvhk_BlockedIDs.value
        #zapelnienie TREE_TAB {'Name': 'OGÓLNE TV-SAT', 'Desc': '', 'IMG': '', 'catURL': '/forumdisplay.php?f=3', 'CatLIST': [], 'forumlevel': (0-2) },
        self.TREE_TAB = []
        
    # zwraca link do ikonki
    def getLogoPath(self):  
        return RetHost(RetHost.OK, value = [self.PATH_TO_LOGO])
        
    def checkLink(self, Naszlink):
        urlNeedsResolve = -1
        return urlNeedsResolve
        
    # zwraca glowna kategorie TREE_TAB
    def getInitList(self):
        #self.__init__()      
        self.TREE_LEVEL = 0
        TREE_LEVEL_IDs = [0,0,0,0,0]
        if self.StartWebPage == '':
            self.StartWebPage = GetDVHKforumContent(GetWebPage(self.mainurl,self.dailyURL,self.username,self.password))
        if self.StartWebPage != -1:
            if len(self.Lista_Forums) == 0:
                self.Lista_Forums = GetForumsList(self.StartWebPage)
            if len(self.TREE_TAB) == 0:
                for forum in self.Lista_Forums:
                    if str(forum['ID']) not in self.BlockedIDs.split(','):
                        self.TREE_TAB.append({'Name': forum['NAME'], 'Desc': self.forumurl + str(forum['ID']), 'IMG': '', 'catURL':forum['ID'], 'CatLIST': [], 'ForumLevel': forum['LEVEL'], 'ParentID': forum['ParenID'] })
        else:
            self.TREE_TAB.append({'Name': str(_('Error logging to %s forum!!!') % "DVHK"), 'Desc': str(_('Check forum settings. ;)')), 'IMG': '', 'catURL':'', 'CatLIST': [], 'ForumLevel': 0, 'ParentID': 0 })
        #print self.TREE_TAB
        
        return RetHost(RetHost.OK, value = self.ListTREETOHostList())
    
    # return current List
    # for given Index
    # 1 == refresh - force to read data from 
    #                server if possible
    def getCurrentList(self, refresh = 1):
        if self.TREE_LEVEL == 0:
            return self.getInitList()
        else:
            self.getPrevList()
            return self.getListForItem(self.currIndex)
            
    def ListTREETOHostList(self, Cat_URL = ''):
        self.TREE_LEVEL_IDs[self.TREE_LEVEL] = Cat_URL
        self.CURRENT_TAB = []
        TheList = []
        for item in self.TREE_TAB:
            if self.TREE_LEVEL == 0:
                self.PARRENT_ID_L1 = 0
                self.PARRENT_ID_L2 = 0
                if item['ForumLevel'] == 0:
                    print '[BoardsReader] hostdvhk.ListTREETOHostList.Cat_URPoziom 0:' + item['Name']
                    Item = CDisplayListItem(item['Name'], item['Desc'], CDisplayListItem.TYPE_CATEGORY)
                    TheList.append(Item)
                    self.CURRENT_TAB.append({'Name': item['Name'], 'Desc': item['catURL'], 'IMG': '', 'catURL':item['catURL'], 'CatLIST': [], 'ForumLevel': item['ForumLevel'], 'ParentID': item['ParentID'] })
            else:
                if item['ParentID'] == Cat_URL and item['ForumLevel'] == self.TREE_LEVEL:
                    print '[BoardsReader] hostdvhk.ListTREETOHostList.Cat_URPoziom %i :' %item['ForumLevel'] + item['Name']
                    Item = CDisplayListItem(item['Name'], item['Desc'], CDisplayListItem.TYPE_CATEGORY)
                    self.CURRENT_TAB.append({'Name': item['Name'], 'Desc': item['catURL'], 'IMG': '', 'catURL':item['catURL'], 'CatLIST': [], 'ForumLevel': item['ForumLevel'], 'ParentID': item['ParentID'] })
                    TheList.append(Item)
              
        self.Lista_Threads = [] # za kazdym razem wypelniamy liste threads od nowa
        #teraz pobierzmy posty
        if self.TREE_LEVEL == 0:
            #Cat_URL = self.mainurl
            self.Lista_Threads = GetThreadsList(self.StartWebPage)
        else:
            print("ListTREETOHostList: " + self.mainurl + self.forumurl + str(Cat_URL))
            self.WebPage = GetDVHKforumContent(GetWebPage(self.mainurl,self.forumurl + str(Cat_URL),self.username,self.password))
            self.Lista_Threads = GetThreadsList(self.WebPage)

        #i wypelnijmy liste postami
        for item in self.Lista_Threads:
            #'threadID:' 'threadICON:' 'threadTITLE:' 'threadDESCR:'
            #linkList = []
            #link = CUrlItem(item['Tytul'], self.mainurl + item['Link'], urlNeedsResolve = 1)
            #linkList.append(link)
            #do wyjasnienia''
            urlItems = []
            urlItems.append(self.threadurl + str(item['threadID']))
            print "threadICON='%s'" % item['threadICON']
            if item['threadICON'] == 'thread_lock_new' or item['threadICON']=='thread_lock':
                curCAT = CDisplayListItem.TYPE_LOCKEDTHREAD
            elif item['threadICON'] == 'thread_new':
                curCAT = CDisplayListItem.TYPE_NEWTHREAD
            elif item['threadICON'] == 'thread_dot':
                curCAT = CDisplayListItem.TYPE_HOTTHREAD
            elif item['threadICON'] == 'thread_dot_new':
                curCAT = CDisplayListItem.TYPE_NEWHOTTHREAD
            else:
                curCAT = CDisplayListItem.TYPE_OLDTHREAD
            iconimage = ''
            if item['threadDESCR'].find('http:') > 0 and item['threadDESCR'].find('.jpg') > 0:
                iconimage = item['threadDESCR'][item['threadDESCR'].find('http:'):item['threadDESCR'].find('.jpg')+4]
                print("JPG link: " + iconimage)
            Item = CDisplayListItem(item['threadTITLE'], item['threadDESCR'], curCAT, urlItems, 0, iconimage)
            TheList.append(Item)
            self.CURRENT_TAB.append({'Name': item['threadTITLE'], 'Desc': item['threadDESCR'], 'IMG': iconimage, 'catURL':self.threadurl + str(item['threadID']), 'CatLIST': [], 'ForumLevel': -1, 'ParentID': -1 })
        return TheList
        
    def parseSearchResults(self, data):
        return ''

    def ListVideoToHostList(self, Index):
        hostList = []
        return hostList
    

    def getFullThread(self, Index = 0):
        if Index > len(self.CURRENT_TAB):
            Index = Index - len(self.CURRENT_TAB)
        if len(self.CURRENT_TAB) <= Index or Index < 0:
            print("[BoardsReader] ERROR: .hostdvhk.BoardsReaderHost.getFullThread there is no item with index: %d, self.CURRENT_TAB.len: %d" % (Index, len(self.CURRENT_TAB)))
            return ""
        else:
            print('[BoardsReader] zwroc Thread "' + self.CURRENT_TAB[Index]['Name'] + '" url=' + self.CURRENT_TAB[Index]['catURL'])
            self.WebPage = GetWebPage(self.mainurl,self.CURRENT_TAB[Index]['catURL'] + self.threadLastPage,self.username,self.password)
            return vb_GetFullThread(self.WebPage) , self.mainurl, self.CURRENT_TAB[Index]['catURL']
            
    def getListForItem(self, Index = 0, refresh = 0, selItem = None):
        print "[BoardsReader] hostdvhk.BoardsReaderHost.getListForItem index: %d" % Index

        if len(self.CURRENT_TAB) <= Index or Index < 0:
            print("[BoardsReader] ERROR: .hostdvhk.BoardsReaderHost.getListForItem there is no item with index: %d, TREE_TAB.len: %d" % (Index, len(self.TREE_TAB)))
            return RetHost(RetHost.ERROR, value = [])
        else:
            print("[BoardsReader] zwroc kategorie " + self.CURRENT_TAB[Index]['Name'] + " id=" + str(self.CURRENT_TAB[Index]['catURL']) + ' parrentID=' + str(self.CURRENT_TAB[Index]['ParentID']))
            self.currentLevel = Index
            self.currIndex = Index
            print("Aktualny poziom:" +  str(self.CURRENT_TAB[Index]['ForumLevel']))
            retList = []
            self.TREE_LEVEL = self.TREE_LEVEL + 1
            retList = self.ListTREETOHostList( self.CURRENT_TAB[Index]['catURL'])
            return RetHost(RetHost.OK, value = retList)

        return RetHost(RetHost.ERROR, value = [])
        
    # return prev requested List of item 
    # for given Index
    # 1 == refresh - force to read data from 
    #                server if possible
    def getPrevList(self, refresh = 1):
        if self.TREE_LEVEL == 0:
            TREE_LEVEL_IDs = [0,0,0,0,0]
            return RetHost(RetHost.OK, value = self.ListTREETOHostList())
        else:
            self.TREE_LEVEL = self.TREE_LEVEL - 1
            if self.TREE_LEVEL < 0:
                self.TREE_LEVEL=0            
                TREE_LEVEL_IDs = [0,0,0,0,0]
            return RetHost(RetHost.OK, value = self.ListTREETOHostList( self.TREE_LEVEL_IDs[self.TREE_LEVEL] ))
          
        
    