## @file  ihost.py
#


class CUrlItem:
    def __init__(self, name = "", url = "", urlNeedsResolve = 0):
        self.name = name
        self.url = url # used only for TYPE_VIDEO item 
        self.urlNeedsResolve = urlNeedsResolve #  additional request to host is needed to resolv this url (url is not direct link)
## class CDisplayListItem
# define attribiutes for item of diplay list
# communicate display layer with host
#
class CDisplayListItem:
    TYPE_UNKNOWN = 0
    TYPE_CATEGORY = 1
    TYPE_VIDEO = 2
    TYPE_SEARCH = 3
    TYPE_NEWTHREAD = 4
    TYPE_OLDTHREAD = 5
    TYPE_LOCKEDTHREAD = 6
    TYPE_HOTTHREAD = 7
    TYPE_NEWHOTTHREAD = 8
    TYPE_THREAD = 9
    
    def __init__(self, name = "", \
                description = "", \
                type = TYPE_UNKNOWN, \
                urlItems = [], \
                urlSeparateRequest = 0, \
                iconimage = '', \
                possibleTypesOfSearch = None):
        self.name = name
        self.description = description
        self.type = type
        
        self.iconimage = iconimage 
        
        # used only for TYPE_VIDEO item         
        self.urlItems = urlItems # url to VIDEO 
        self.urlSeparateRequest = urlSeparateRequest # links are not available the separate request is needed to get links

        # used only for TYPE_SEARCH item     
        self.possibleTypesOfSearch = possibleTypesOfSearch
       
class RetHost:
    OK = "OK"
    ERROR = "ERROR"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    def __init__(self, status , value, message = ''):
        self.status = status
        self.value = value  
        self.message = message

## class IHost
# interface base class with method used to
# communicate display layer with host
#
class IHost:

    # return firs available list of item category or video or link
    def getInitList(self):
        return RetHost(RetHost.NOT_IMPLEMENTED, value = [])
    
    # return List of item from current List
    # for given Index
    # 1 == refresh - force to read data from 
    #                server if possible 
    # server instead of cache 
    # item - object of CDisplayListItem for selected item
    def getListForItem(self, Index = 0, refresh = 0, item = None):
        return RetHost(RetHost.NOT_IMPLEMENTED, value = [])
        
    # return prev requested List of item 
    # for given Index
    # 1 == refresh - force to read data from 
    #                server if possible
    def getPrevList(self, refresh = 0):
        return RetHost(RetHost.NOT_IMPLEMENTED, value = [])
        
    # return current List
    # for given Index
    # 1 == refresh - force to read data from 
    #                server if possible
    def getCurrentList(self, refresh = 0):
        return RetHost(RetHost.NOT_IMPLEMENTED, value = [])
        
    # return list of links for VIDEO 
    # for given Index, item should have type VIDEO!
    # item - object of CDisplayListItem for selected item
    def getLinksForVideo(self, Index = 0, item = None):
        return RetHost(RetHost.NOT_IMPLEMENTED, value = [])
        
    # return resolved url
    # for given url
    def getResolvedURL(self, url):
        return RetHost(RetHost.NOT_IMPLEMENTED, value = [])
        
    # return full path to player logo
    def getLogoPath(self):
        return RetHost(RetHost.NOT_IMPLEMENTED, value = [])
        
    def getSearchResults(self, pattern, searchType = None):
        return RetHost(RetHost.NOT_IMPLEMENTED, value = [])


