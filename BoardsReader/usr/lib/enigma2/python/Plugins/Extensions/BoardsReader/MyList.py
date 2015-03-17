from Components.GUIComponent import GUIComponent
from enigma import eListboxPythonMultiContent, eListbox, gFont, \
    RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_VALIGN_CENTER
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

from ihost import CDisplayListItem

class MyListComponent(GUIComponent, object):
    def buildEntry(self, item):
        width = self.l.getItemSize().width()
        res = [ None ]

        res.append((eListboxPythonMultiContent.TYPE_TEXT, 45, 3, width-45, 20, 1, RT_HALIGN_LEFT|RT_VALIGN_CENTER, item.name))
        
        if CDisplayListItem.TYPE_CATEGORY == item.type:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 3, 1, 33, 33, self.categoryPIX))
        elif CDisplayListItem.TYPE_SEARCH == item.type:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 3, 1, 33, 33, self.searchPIX))
        elif CDisplayListItem.TYPE_NEWTHREAD == item.type:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 3, 1, 33, 33, self.newthreadPIX))
        elif CDisplayListItem.TYPE_OLDTHREAD == item.type:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 3, 1, 33, 33, self.oldthreadPIX))
        elif CDisplayListItem.TYPE_LOCKEDTHREAD == item.type:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 3, 1, 33, 33, self.lockedthreadPIX))
        elif CDisplayListItem.TYPE_HOTTHREAD == item.type:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 3, 1, 33, 33, self.hotthreadPIX))
        elif CDisplayListItem.TYPE_NEWHOTTHREAD == item.type:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 3, 1, 33, 33, self.newhotthreadPIX))
        elif CDisplayListItem.TYPE_THREAD == item.type:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 3, 1, 33, 33, self.threadPIX))
         
        return res

    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.l.setFont(0, gFont("Regular", 24))
        self.l.setFont(1, gFont("Regular", 18))
  
        self.l.setBuildFunc(self.buildEntry)
        #self.l.setItemHeight(65)
        self.l.setItemHeight(35)
        self.onSelectionChanged = [ ]
        self.MyListComponentPath = resolveFilename(SCOPE_PLUGINS, 'Extensions/BoardsReader/icons/')
        
        try:
            self.categoryPIX = LoadPixmap(cached=True, path=self.MyListComponentPath + 'CategoryItem.png')
            print("loaded")
            self.searchPIX = LoadPixmap(cached=True,  path=self.MyListComponentPath + 'SearchItem.png')
            print("loaded")
            self.newthreadPIX = LoadPixmap(cached=True,  path=self.MyListComponentPath + 'thread_new.png')
            print("loaded")
            self.oldthreadPIX = LoadPixmap(cached=True,  path=self.MyListComponentPath + 'ICON_OLDTHREAD.png')
            print("loaded")
            self.lockedthreadPIX = LoadPixmap(cached=True,  path=self.MyListComponentPath + 'thread_lock.png')
            print("loaded")
            self.hotthreadPIX = LoadPixmap(cached=True,  path=self.MyListComponentPath + 'thread_hot.png')
            print("loaded")
            self.newhotthreadPIX = LoadPixmap(cached=True,  path=self.MyListComponentPath + 'thread_hot_new.png')
            print("loaded")
            self.threadPIX = LoadPixmap(cached=True,  path=self.MyListComponentPath + 'thread.png')
            print("loaded")
        except:
            self.categoryPIX = None
            self.searchPIX = None
            self.newthreadPIX = None
            self.oldthreadPIX = None
            self.lockedthreadPIX = None
            self.hotthreadPIX = None
            self.newhotthreadPIX = None
            self.threadPIX = None
            print("Problem with loading markers for MyList")

    def connectSelChanged(self, fnc):
        if not fnc in self.onSelectionChanged:
            self.onSelectionChanged.append(fnc)

    def disconnectSelChanged(self, fnc):
        if fnc in self.onSelectionChanged:
            self.onSelectionChanged.remove(fnc)

    def selectionChanged(self):
        for x in self.onSelectionChanged:
            x()
   
    def getCurrent(self):
        cur = self.l.getCurrentSelection()
        return cur and cur[0]
   
    GUI_WIDGET = eListbox
   
    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        instance.selectionChanged.get().append(self.selectionChanged)

    def preWidgetRemove(self, instance):
        instance.setContent(None)
        instance.selectionChanged.get().remove(self.selectionChanged)

    def moveToIndex(self, index):
        self.instance.moveSelectionTo(index)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def setList(self, list):
        self.l.setList(list)
        
    currentIndex = property(getCurrentIndex, moveToIndex)
    currentSelection = property(getCurrent)
