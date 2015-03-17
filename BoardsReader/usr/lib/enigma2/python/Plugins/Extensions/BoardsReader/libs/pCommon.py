# -*- coding: utf-8 -*-
# Based on (root)/trunk/xbmc-addons/src/plugin.video.polishtv.live/hosts/ @ 419 - Wersja 605

###################################################
# LOCAL import
###################################################


###################################################
# FOREIGN import
###################################################
import urllib, urllib2, re, htmlentitydefs
import cookielib
###################################################


class common:
    HOST = 'Mozilla/5.0 (Windows NT 6.1; rv:17.0) Gecko/20100101 Firefox/17.0'
    def __init__(self):
        pass
        
    def getCookieItem(self, cookiefile, item):
        ret = ''
        cj = cookielib.LWPCookieJar()
        cj.load(cookiefile, ignore_discard = True)
        for cookie in cj:
            if cookie.name == item: ret = cookie.value
        return ret

    def html_entity_decode_char(self, m):
        ent = m.group(1)
        if ent.startswith('x'):
            return unichr(int(ent[1:],16))
        try:
            return unichr(int(ent))
        except:
            if ent in htmlentitydefs.name2codepoint:
                return unichr(htmlentitydefs.name2codepoint[ent])
            else:
                return ent

    def html_entity_decode(self, string):
        string = string.decode('UTF-8')
        s = re.compile("&#?(\w+?);").sub(self.html_entity_decode_char, string)
        return s.encode('UTF-8')
        
    def getURLRequestData(self, params = {}, post_data = {}):
        cj = cookielib.LWPCookieJar()
 
        host = common.HOST
        response = None
        req = None
        out_data = None
        opener = None
        headers = { 'User-Agent' : host }
        redirect_handler= urllib2.HTTPRedirectHandler()
        debug_handler = urllib2.HTTPHandler(debuglevel=1)
        try:
            if params['use_header']:
                headers = params['header']
        except: pass
        print('pCommon - getURLRequestData() -> params: ' + str(params))
        if params['use_host']:
            host = params['host']
        if params['use_cookie'] and cj != None:
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), redirect_handler, redirect_handler)
            if params['load_cookie']:
                cj.load(params['cookiefile'], ignore_discard = True)
        if params['use_post']:
            #headers = { 'User-Agent' : host }
            print('pCommon - getURLRequestData() -> post data: ' + str(post_data))
            try:
                if params['raw_post_data']:
                    dataPost = post_data
                else:
                    dataPost = urllib.urlencode(post_data)
            except:
                dataPost = urllib.urlencode(post_data)
            req = urllib2.Request(params['url'], dataPost, headers)
        if not params['use_post']:
            try:
                if params['use_header']:
                    req = urllib2.Request(params['url'], None, headers)
                else:
                    req = urllib2.Request(params['url'])
                    req.add_header('User-Agent', host)
            except:
                req = urllib2.Request(params['url'])
                req.add_header('User-Agent', host)
        if params['use_cookie'] and cj != None:
            response = opener.open(req)
        else:
            response = urllib2.urlopen(req)
        if not params['return_data']:
            try:
                if params['read_data']:
                    out_data = response.read()
                else:
                    out_data = response
            except:
                out_data = response
        if params['return_data']:
            out_data = response.read()
            response.close()
        if params['use_cookie'] and params['save_cookie'] and cj != None:
            cj.save(params['cookiefile'], ignore_discard = True)
        return out_data 
        
    def makeABCList(self):
        strTab = []
        strTab.append('0 - 9');
        for i in range(65,91):
            strTab.append(str(unichr(i)))    
        return strTab

    def isNumeric(self,s):
        try:
            float(s)
            return True
        except ValueError:
            return False
        
    def setLinkTable(self, url, host):
        strTab = []
        strTab.append(url)
        strTab.append(host)
        return strTab
    
