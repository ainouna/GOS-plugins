# -*- coding: utf-8 -*-
#! /usr/bin/python
#
#sys.path.append('/usr/lib/enigma2/python/Plugins/Extensions/BoardsReader/')

from cookielib import CookieJar
import urllib, urllib2, re, time, os, sys 
from urllib2 import Request, urlopen, URLError, HTTPError
import time
import tarfile
from datetime import datetime
from Components.config import config
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_CONFIG

#####################################################
# get host list based on files in /hosts folder
#####################################################
def GetHostsList():
    print('getHostsList begin')
    HOST_PATH = resolveFilename(SCOPE_PLUGINS, 'Extensions/BoardsReader/forums/')
    lhosts = [] 
    
    fileList = os.listdir( HOST_PATH )
    for wholeFileName in fileList:
        # separate file name and file extension
        fileName, fileExt = os.path.splitext(wholeFileName)
        nameLen = len( fileName )
        if fileExt in ['.pyo', '.pyc', '.py'] and nameLen >  5 and fileName[:5] == 'forum' and fileName.find('_blocked_') == -1:
            if fileName[5:] not in lhosts:
                lhosts.append( fileName[5:] )
                print('BoardsReader.tools.getHostsList add host with fileName: "%s"' % fileName[5:])
    print('BoardsReader.tools.getHostsList end')
    lhosts.sort()
    return lhosts
    
def IsHostEnabled( hostName ):
    hostEnabled  = False
    try:
        exec('if config.plugins.BoardReader.host' + hostName + '.value: hostEnabled = True')
    except:
        hostEnabled = False
    return hostEnabled

#####################################################
# czy mamy wystarczajaco wolnego miejsca?
#####################################################
def FreeSpace(katalog, WymaganeMB):
    try:
        s = os.statvfs(katalog)
        WolneMB=s.f_bavail * s.f_frsize / 1048576
        if WolneMB >= WymaganeMB:
            return True
        else:
            return False
    except:
        return False
        
#####################################################
# rekursywne tworzenie katalogow
#####################################################

def mkdirs(newdir):
    """ Create a directory and all parent folders.
        Features:
        - parent directories will be created
        - if directory already exists, then do nothing
        - if there is another filsystem object with the same name, raise an exception
    """
    print('mkdirs: "%s"' % newdir)
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("cannot create directory, file already exists: '%s'" % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head) and not os.path.ismount(head) and not os.path.islink(head):
            mkdirs(head)
        if tail:
            os.mkdir(newdir)

#####################################################
# autoupdate
#####################################################

def GetGITversion():
    try:
        req = urllib2.Request("http://gitorious.org/opli-plugins/opli-plugins/blobs/master/BoardsReader/_version.py")
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        html_doc = str(response.read())
        response.close()
    except:
        html_doc="BLAD"
    print("GetGITversion:" + html_doc)
    #znajdujemy wersje w pliku
    r=re.search( r'version=&quot;(.+)&quot;',html_doc)
    if r:
        znalezione=r.groups(1)
        wersjaGIT=znalezione[0]
        print("Wersja GIT na gitorious: %s" % wersjaGIT)
        return wersjaGIT
    else:
        return "??"

def Porzadki(sciezkaTMP="/tmp/"):
    #porzadki w razie czego
    if os.path.exists(sciezkaTMP + 'plugin.tar.gz'):
        os.remove(sciezkaTMP + 'plugin.tar.gz')
    if os.path.exists(sciezkaTMP + 'opli-plugins-opli-plugins'):
        import shutil
        shutil.rmtree(sciezkaTMP + 'opli-plugins-opli-plugins')

                
########################################################
#                     For icon menager
########################################################
def checkIconName(name):
    #check if name is correct 
    nameIsOk = False
    if 36 == len(name) and '.jpg' == name[-4:]:
        #print("Icon name %s is correct" % name)
        try:
            tmp = int(name[:-4], 16)
            nameIsOk = True
        except:
            nameIsOk = False
            pass
    return nameIsOk
    
    
def removeAllIconsFromPath(path):
    print "removeAllIconsFromPath"
    try:
        list = os.listdir(path)
        for item in list:
            filePath = path + '/' + item
            if checkIconName(item) and os.path.isfile(filePath):
                print 'removeAllIconsFromPath img: ' + filePath
                try:
                    os.remove(filePath)
                except error:
                    print "ERROR while removing file %s" % filePath
    except:
        print 'ERROR: in removeAllIconsFromPath'
        pass
    return 
    
def getModifyDeltaDateInDays(fullPath):
    ret = -1
    try:
        modifiedTime = os.path.getatime(fullPath)
        currTime = datetime.now()
        modTime = datetime.fromtimestamp(modifiedTime)
        deltaTime = currTime - modTime
        ret = deltaTime.days
    except:
        ret = -1 
    
    return ret
    
def remove_html_markup(s):
    tag = False
    quote = False
    out = ""

    for c in s:
            if c == '<' and not quote:
                tag = True
            elif c == '>' and not quote:
                tag = False
            elif (c == '"' or c == "'") and tag:
                quote = not quote
            elif not tag:
                out = out + c

    return re.sub('&\w+;', ' ',out)

#localization part
from Components.Language import language
import gettext

PluginLanguageDomain = "plugin-BoardsReader"
LanguagePath = "/usr/share/locale"

def localeInit():
	lang = language.getLanguage()[:2] # getLanguage returns e.g. "fi_FI" for "language_country"
	os.environ["LANGUAGE"] = lang # Enigma doesn't set this (or LC_ALL, LC_MESSAGES, LANG). gettext needs it!
	print(PluginLanguageDomain + " set language to " + lang)
	gettext.bindtextdomain(PluginLanguageDomain, LanguagePath)

def TranslateTXT(txt):
	t = gettext.dgettext(PluginLanguageDomain, txt)
	if t == txt:
		#print PluginLanguageDomain, "fallback to default translation for", txt
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)