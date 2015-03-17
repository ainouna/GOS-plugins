# -*- coding: utf-8 -*-
#!/usr/bin/python

import urllib, urllib2, cookielib, hashlib, time, re
global WebPageCharSet
global outsidePLI
global WebPageLastTime

def GetFullThread(WebPage = -1):
    if WebPage == -1:
        WebPage = GetWebPage(url = 'http://forum.xunil.pl', vdir = '/index.php?topic=1128.9999')
    if WebPage == -1:
        print("[SMF]Brak WebPage, koniec\n")
        return -1
    PostsInThread = 'BŁAD'
    WebPage = WebPage.encode('utf8')
    if WebPage.find('<title>') > 0 and WebPage.find('</title>') > 0:
        PostsInThread = WebPage[WebPage.find('<title>')+len('<title>'):WebPage.find('</title>')]
    if WebPage.find('Strony:') > 0:
        tmpPage = WebPage[WebPage.find('Strony: ') + len('Strony: '):]
        tmpPage = tmpPage[tmpPage.find('[<strong>')+len ('[<strong>'):tmpPage.find(']')]
        tmpPage = tmpPage[:tmpPage.find('<')].strip()
        PostsInThread += ' - Strona ' + str(tmpPage) + ' - forum xunil\n'

    print("[SMF]Tytul:" + PostsInThread)
    WebPage = WebPage[WebPage.find('<div id="main_content_section">'):]
    WebPage = WebPage[WebPage.find('<div id="forumposts">'):]
    WebPage = WebPage[:WebPage.find('<div class="pagesection">')]
    WebPage = WebPage.replace('\r','').replace('\n','') #wszystko w jednej linii
    WebPage = WebPage.replace('<div class','\nDivClass=') #kazdy div w jednej linii
    WebPage = WebPage.replace('<ul class=','\nUlClass=') #kazdy div w jednej linii
    WebPage = WebPage.replace('<span class=','\nSpanClass=') #kazdy div w jednej linii
    WebPage = WebPage.replace('<hr class=','\nHrClass=') #kazdy div w jednej linii

    #WebPage = WebPage.replace('title="Wink"','').replace('title="Wink"','').replace('title="Wink"','')
    #wywalenie smieci
    WebPage = re.sub('class="[a-zA-Z]*"','',WebPage)
    WebPage = re.sub('title="[a-zA-Z]*"','',WebPage)
    WebPage = re.sub('alt="[;&#1234567890]*"','',WebPage)
    
    WebPage = WebPage.replace('  ',' ').replace('\t\t\t\t','\t').replace('\t\t\t','\t').replace('\t\t','\t')
    WebPage = re.sub('DivClass=="pagesection">.*','',WebPage) #wywalenie konca strony
    WebPage = re.sub('DivClass=="keyinfo">.*','',WebPage)
    WebPage = re.sub('HrClass="post_separator".*','',WebPage)
    WebPage = re.sub('SpanClass=".*','',WebPage)
    WebPage = re.sub('UlClass=".*','',WebPage)
    WebPage = re.sub('DivClass=="post_wrapper">.*','',WebPage)
    WebPage = re.sub('DivClass=="postarea">.*','',WebPage)
    WebPage = re.sub('ivClass=="flow_hidden">.*','',WebPage)
    WebPage = re.sub('DivClass=="moderatorbar">.*','',WebPage)
    WebPage = re.sub('DivClass=="smalltext modified".*','',WebPage)
    WebPage = re.sub('DivClass=="messageicon">.*','',WebPage)
    WebPage = re.sub('DivClass=="windowbg.*','',WebPage)
    
    WebPage = re.sub('DivClass=="signature".*','',WebPage)
    WebPage = re.sub('DivClass=="smalltext reportlinks">.*','',WebPage)
    WebPage = re.sub('DivClass=="post">.*','',WebPage)
    WebPage = re.sub('DivClass=="quoteheader">.*','',WebPage)
    WebPage = re.sub('DivClass=="quotefooter">.*','',WebPage)
    
    WebPage = re.sub('DivClass=="poster">.*title=.*">','DivClass=Poster=',WebPage)
    WebPage = re.sub('<a href=.*target="_blank">','',WebPage)
    WebPage = re.sub('<div id="msg.*smalltext">','',WebPage)
    WebPage = re.sub('<div style="overflow: auto;">','',WebPage)
    WebPage = re.sub('<a href=.*id="thumb_[0123456789]*" />','',WebPage)
    WebPage = WebPage.replace('\r','').replace('\n','').replace('DivClass=Poster=','ENDofLINE\n\nNaszPost=Poster=') #wszystko z jednego posta w jednej linii
    #zamiana emotikon na standardowe
    WebPage = WebPage.replace('<img src="images/smilies/newtongue.gif" border="0" alt="" title="Stick Out Tongue" class="inlineimg" />',':P')
    WebPage = WebPage.replace('<img src="images/smilies/newblink.gif" border="0" alt="" title="EEK!" class="inlineimg" />',':o')
    WebPage = WebPage.replace('<img src="http://xunil.pl/forum/Smileys/akyhne/smiley.gif"',':)')
    WebPage = WebPage.replace('<img src="http://xunil.pl/forum/Smileys/akyhne/wink.gif"',';)')
    WebPage = WebPage.replace('<img src="http://xunil.pl/forum/Smileys/akyhne/cheesy.gif"','{:-D')
    WebPage = WebPage.replace('<img src="http://xunil.pl/forum/Smileys/akyhne/sad.gif"',':(')

    #WebPage = re.sub('<img src=".*sad.gif.*title="Sad" class="smiley" />',':(',WebPage)
    WebPage += 'ENDofLINE'
    print "[SMF] Webpage=\n%s" % WebPage
    for Post in re.findall('NaszPost=Poster=(.+?)</a>.+?<strong>.+?strong>(.+?)&#187;</div>.+?DivClass=="inner".+?id="msg_[0-9]+?">(.+?)ENDofLINE', WebPage):
        AutorPostu = Post[0]
        DataPostu  = Post[1].replace("<strong>","").replace("</strong>","") # 'dzisiaj' jest boldem
        TekstPostu = str(Post[2].replace('<br />','\n').strip())
        #print "[SMF] DataPostu=%s" % DataPostu
        #print "[SMF] TekstPostu=\n%s" % TekstPostu
        #obsluga cytatow
        LicznikCytatow = 0
        while (TekstPostu.count('DivClass=="topslice_quote">') > 0):
            LicznikCytatow = LicznikCytatow + 1
            TekstPostu = TekstPostu.replace('DivClass=="topslice_quote">','Cytat%i:"' % LicznikCytatow,1)
            TekstPostu = TekstPostu.replace('DivClass=="botslice_quote">','"\n',1)
        ######CYTATY!!!!!!!
        #>link do innego postu z cytatu
        TekstPostu = TekstPostu.replace('<img class="inlineimg" src="disturbed/buttons/viewpost.gif" border="0" alt="Zobacz post" />','')
        TekstPostu = TekstPostu.replace('<table cellpadding="6" cellspacing="0" border="0" width="100%">','<table>')
        TekstPostu = TekstPostu.replace('<div style="font-style:italic">','')
        TekstPostu = TekstPostu.replace('<td class="alt2" style="border:1px inset">','')
        TekstPostu = re.sub('<a href="showthread.php\?p=.+?" rel="nofollow"','',TekstPostu)
        #TekstPostu = TekstPostu.replace('','').replace('','').replace('','')
        #czyscimy formatowanie i smieci
        TekstPostu = re.sub('<span style=.*color">','',TekstPostu)
        TekstPostu = re.sub('DivClass=="codeheader">.* class="bbc_code">','Kod:\n#',TekstPostu)
        TekstPostu = re.sub('</code>','#\n',TekstPostu)
        TekstPostu = re.sub('<a href=".*clip.gif.*/>','Załączono: ',TekstPostu)
        TekstPostu = re.sub('"<a href=".*topic[,=][0-9]*.*class="bbc_standard_quote">','"',TekstPostu)
        TekstPostu = re.sub('<img src=".*modify_inline.gif.*" />','',TekstPostu)
        TekstPostu = TekstPostu.replace('</blockquote>','')
        TekstPostu = re.sub('</div>[\t ]*</div>','',TekstPostu)
        TekstPostu = re.sub(':"Cytuj<blockquote class="bbc_standard_quote">',':"',TekstPostu)

        TekstPostu = TekstPostu.replace('<strong>','').replace('</strong>','').replace('</a>','').replace('<tt class="bbc_tt">','').replace('</tt>','')
        TekstPostu = TekstPostu.replace('</span>','').replace('\n\n','\n')
        TekstPostu = TekstPostu.replace('\t\t\t</div>','').replace('\t\t</div>','').replace('\t</div>','')
        TekstPostu = TekstPostu.replace('\t\n','\n').replace('\n\n','\n')
        TekstPostu = TekstPostu.replace('/>','')
        #sklejamy wszystko do kupy
        PostsInThread = str(PostsInThread) + "\n########## " + DataPostu + ' , ' + AutorPostu + str(' napisał:\n')
        PostsInThread = PostsInThread + TekstPostu.strip() + '\n'
    print("[SMF] %s" % PostsInThread)
    return PostsInThread

def GetThreadsList(WebPage = -1 ):
    global WebPageCharSet
    Threads = []
    if WebPage == -1:
        print("GetThreadsList Pobieram WebPage\n")
        WebPage = GetWebPage( url = 'http://forum.xunil.pl',  vdir = '/index.php?board=56.0' )
    if WebPage == -1:
        print "GetThreadsList Brak WebPage, koniec"
        Threads.append({'threadID': 0,'threadICON': '','threadTITLE': str('Błąd logowania do xunil!!!'), 'threadDESCR': str('Błąd logowania do xunil!!!')})
        return Threads
    #print('\n########################\n' + WebPage.encode('utf-8') +'\n\n')
    WebPage = WebPage[WebPage.find('<div id="main_content_section">'):] #wywalenie naglowka
    #WebPage = WebPage[:WebPage.find('<div class="pagesection">')] # wywalenie stopki
    WebPage = WebPage.replace('\r','').replace('\n','').replace('<span id="msg_','\nthreadID=') #kazdy post w jednej linii
    WebPage = WebPage.replace('<a href="http://forum.xunil.pl/index.php/topic,','ToPiC=')
    #WebPage = WebPage.replace('href="http://forum.xunil.pl/index.php?topic=','ToPiC=')
    WebPage = WebPage.replace('<img src="http://forum.xunil.pl/Themes/default/images/','threadICON=')
    WebPage = WebPage.replace('polish-utf8/','').replace('icons/','')
    
    #WebPage = re.sub('<td class="alt2" title=".+?','',WebPage.encode('utf-8'))
    #WebPage = re.sub('<div>.*<a href="showthread.php.*thread_title_[0-9]*" style="font-weight:bold">','\tthreadTITLE=',WebPage)#search,nowe posty
    #WebPage = re.sub('<div>.*<a href="showthread.php.*thread_title_[0-9]*">','\tthreadTITLE=',WebPage)#lista na forum
    #WebPage = re.sub('</a>[ \t]*</div>[ \t]*<div class=.*','=ENDthreadTITLE',WebPage)#koniec tytulu podfora
    #WebPage = re.sub('</a>	<span class="smallfont" style="white-space:nowrap">','=ENDthreadTITLE',WebPage)#koniec tytulu podfora
    #WebPage = re.sub('.gif.+?title=','\tthreadDESCR=',WebPage)
    #WebPage = re.sub('<img class="inlineimg".+?','',WebPage)
    #print('\n########################\n' + WebPage.encode('utf-8') +'\n\n')
    #for thread in re.findall('threadID=([0-9]+?)">.+?threadICON=(.+?) title="(.+?)">[ \t]+?<div>.+?bold">(.+?)</a>', WebPage.encode('utf-8')):
    print WebPage
    ThreadsList = re.findall('ToPiC=([0-9]+?).0.html">(.+?)</a>.+?threadICON=(.+?).gif"', WebPage)
    if len(ThreadsList) == 0:
        ThreadsList = re.findall('ToPiC=([0-9]+?).0/topicseen.html">(.+?)</a>.+?threadICON=(.+?).gif"', WebPage)
    for thread in ThreadsList:
        #print thread
        threadID = int(thread[0])
        threadTITLE = thread[1].encode(WebPageCharSet)
        threadICON = thread[2].encode(WebPageCharSet)
        threadDESCR = ''
        #print('threadID:'+ str(threadID) + '\nthreadICON:' + threadICON + '\nthreadTITLE:'+ threadTITLE + '\nthreadDESCR:' + threadDESCR + '\n')
        Threads.append({'threadID': threadID,'threadICON': threadICON,'threadTITLE': threadTITLE, 'threadDESCR': threadDESCR})
    print "[SMF] Threads:"
    print Threads
    return Threads
   
def GetForumsList(WebPage = -1):
    if WebPage == -1:
        WebPage = GetForumContent()
        #print('\n##### WebPage ##### \n' + WebPage.encode('utf-8')) 
    if WebPage == -1:
        print("Brak WebPage, koniec\n")
        return -1
    Forums = []
    if WebPage == -1:
        Forums.append({'ID': 0,'LEVEL': 0,'NAME': 'BŁĄD LOGOWANIA!!!', 'ParenID': 0})
        return Forums
    UsedIDs = []
    BlockedIDs = [998,999]
    level_0_ID = 0
    level_1_ID = 0
    level_2_ID = 0
    parentID = 0
    for forum in re.findall('name="b([0-9]+?)">(.+?)</a>', WebPage.encode('utf-8'), re.DOTALL):
        #print forum
        forumName = forum[1].strip()
        forumID = int(forum[0])
        forumlevel = 0
        if forumlevel == 0:
            level_0_ID = forumID
            parentID = 0
        elif forumlevel == 1:
            level_1_ID = forumID
            parentID = level_0_ID
        elif forumlevel == 2:
            level_2_ID = forumID
            parentID = level_1_ID
        if forumName != '' and forumID not in UsedIDs and forumID not in BlockedIDs and parentID not in BlockedIDs:
            Forums.append({'ID': forumID,'LEVEL': forumlevel,'NAME': forumName, 'ParenID': parentID})
            UsedIDs.append(forumID)
    for forum in Forums:
        Txt2Search = '<tr id="board_' + str(forum['ID']) + "_children"
        if WebPage.find(Txt2Search) > 0:
            print("Forum " + str(forum['ID']) + " ma subfora")
            SubPage = WebPage[WebPage.find(Txt2Search) + len(Txt2Search):]
            SubPage = SubPage[:SubPage.find('</td>')]
            print('\n##### SubPage ##### \n' + SubPage.encode('utf-8'))
            for subforum in re.findall('board=([0-9]+?).0".+?">(.+?)</a>', SubPage.encode('utf-8'), re.DOTALL):
                #print subforum
                forumID = int(subforum[0])
                forumlevel = forum['LEVEL'] + 1
                parentID = forum['ID']
                forumName = subforum[1].strip()
                if forumName != '' and forumID not in UsedIDs and forumID not in BlockedIDs and parentID not in BlockedIDs:
                    Forums.append({'ID': forumID,'LEVEL': forumlevel,'NAME': forumName, 'ParenID': parentID})
                    UsedIDs.append(forumID)
                
    print "[SMF] Forums:"
    print Forums
    return Forums
# mniej danych do parsowania = szybciej dzialajacy skrypt

def GetForumContent(WebPage = -1):
    if WebPage == -1:
        print("GetForumContent Pobieram WebPage\n")
        WebPage = GetWebPage()
    if WebPage == -1:
        print("Brak WebPage, koniec\n")
        return -1
    #krok 1.1 - obcinamy gore strony dla newposts
    Txt2Search = '<div id="recent" class="main_content">'
    if WebPage.find(Txt2Search) > 0:
        WebPage = WebPage[WebPage.find(Txt2Search) + len(Txt2Search):]
    #krok 1.2 - obcinamy gore strony dla index.php
    Txt2Search = '<div id="main_content_section">'
    if WebPage.find(Txt2Search) > 0:
        WebPage = WebPage[WebPage.find(Txt2Search) + len(Txt2Search):]
    #krok 2 - obcinamy dol strony
    Txt2Search = '<div class="pagesection" id="readbuttons">'
    if WebPage.find(Txt2Search) > 0:
        WebPage = WebPage[:WebPage.find(Txt2Search)]
    return WebPage

def GetWebPage(url = 'forum.xunil.pl', vdir = '/index.php', uname = '', passwd = '' ):
    global WebPageLastTime
    CurTime = time.time()
    try:
        if WebPageLastTime > CurTime - 2:
            time.sleep(WebPageLastTime - CurTime + 2)
    except:
        print "NoWebpage"
    if uname == '' and passwd == '':
        print("GetWebPage szukam uname i passwd\n")
        try:
            file = open("/etc/enigma2/settings")
            for line in file:
                if line.startswith('config.plugins.BoardReader.xunil_login=' ) :
                    uname=line.split("=")[1].strip()
                    print('Znaleziono uname:' + uname + '\n')
                if line.startswith('config.plugins.BoardReader.xunil_password=' ) :
                    passwd=line.split("=")[1].strip()
                    print('Znaleziono passwd: XXXXXXX\n')
                if uname != '' and passwd != '':
                    break
        except:
            pass
        try:
            file = open("/usr/local/e2/etc/enigma2/settings")
            for line in file:
                if line.startswith('config.plugins.BoardReader.xunil_login=' ) :
                    uname=line.split("=")[1].strip()
                    print('Znaleziono uname:' + uname + '\n')
                if line.startswith('config.plugins.BoardReader.xunil_password=' ) :
                    passwd=line.split("=")[1].strip()
                    print('Znaleziono passwd:' + passwd + '\n')
                if uname != '' and passwd != '':
                    break
        except:
            pass
    if uname == '' or passwd == '':
        print("GetWebPage uname lub passwd\n")
        
    global WebPageCharSet
    if not url.startswith('http://'):
        url = 'http://' + url
    loginurl = url + '/index.php?action=login2'
    if not vdir.startswith('/') and not url.endswith('/'):
        vdir = '/' + vdir
    forumurl = url + vdir
    print('loginurl:' + loginurl + '\n')
    print('forumurl:' + forumurl + '\n')
    md5 = hashlib.md5(passwd);md5 = md5.hexdigest()
    # Options for request
    opts = {
    'user': uname, 
    'passwrd': passwd,
    'cookielength': '-1',
    'openid_identifier': '',
    'hash_passwrd': md5
    }
    data = urllib.urlencode(opts)
    
    # Request header
    global headers
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-GB; rv:1.8.1.12) Gecko/20100101 Firefox/7.0.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-gb,en;q=0.5',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'Connection': 'keep-alive',
    'Referer': loginurl
    }
    
    # Cookie Handling
    jar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
    
    # Send Request
    opener.addheader = headers
    opener.open(loginurl, data)
    # Check
    response = opener.open(forumurl)
    WebPageCharSet = response.headers.getparam('charset')
    print('\nWebPageCharSet:' + WebPageCharSet + '\n')
    #print kodowanie
    WebPage = response.read().decode(WebPageCharSet)
    WebPage = WebPage.replace('&quot;','"').replace('&amp;','&').replace('&lt;','<').replace('&gt;','>').replace('&nbsp;',' ') #poprawka smieci po kodowaniu html-a
    WebPageLastTime = time.time()
    if 'id="button_logout"' in WebPage:
        print('\nGetWebPage:Zalogowany do xunil :)\n')
        #print  WebPage
        return WebPage
    else:
        print('\nGetWebPage:Blad logowania do xunil :(\n')
        return -1
