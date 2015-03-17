import threading

class AsyncCall(object):
	def __init__(self, fnc, callback = None):
		self.Callable = fnc
		self.Callback = callback

	def __call__(self, *args, **kwargs):
		self.Thread = threading.Thread(target = self.run, name = self.Callable.__name__, args = args, kwargs = kwargs)
		self.Thread.start()
		return self

	def wait(self, timeout = None):
		self.Thread.join(timeout)
		if self.Thread.isAlive():
			return self.Callback(None)
		else:
			return self.Result

	def run(self, *args, **kwargs):
		self.Result = self.Callable(*args, **kwargs)
		if self.Callback:
			self.Callback(self.Result)

class AsyncMethod(object):
	def __init__(self, fnc, callback=None):
		self.Callable = fnc
		self.Callback = callback

	def __call__(self, *args, **kwargs):
		return AsyncCall(self.Callable, self.Callback)(*args, **kwargs)
        
        
###############################################################################
#                          Proxy function Queue
#           can be used to run call back function from MainThread
###############################################################################
class CFunProxyQueueItem:
    def __init__(self, clientFunName, retValue):
        print "CFunProxyQueueItem"
        self.clientFunName = clientFunName
        self.retValue = retValue
  
class CFunctionProxyQueue:
    def __init__(self):
        # read/write/change display elements should be done from main thread
        self.Queue = []
        self.QueueLock = threading.Lock()
        
        self.mainThreadName = threading.currentThread().getName()
        
        self.registeredFunctions = {} 
        
    ############################################################
    #       This method can be called only from mainThread
    #       so there is no need to synchronize it by mutex
    ############################################################
    def registerFunction(self, fun):
    
        currThreadName = threading.currentThread().getName()
        if self.mainThreadName != currThreadName:
            print("ERROR CFunctionProxyQueue.registerFunction: thread [%s] is not main thread" % currThreadName)
            raise AssertionError
            return False
            
        funName = fun.__name__
      
        print("INFO CFunctionProxyQueue.registerFunction: [%s]" % fun.__name__)
        
        # check if function is not already registered
        if funName in self.registeredFunctions:
            print("WARNING CFunctionProxyQueue.registerFunction: function [%s] is already registered" %  funName)
            # maybe this should be allowed (without assertion)
            raise AssertionError, ("CFunctionProxyQueue.registerFunction: function [%s] is already registered" %  funName)
            return False
        
        # add new function to dictionary
        self.registeredFunctions[funName] = fun
        
        print("Info CFunctionProxyQueue.registerFunction: the function [%s] has been successfully registered" % funName)
        
        return True      
        
    ############################################################
    #       This method can be called only from mainThread
    #       so there is no need to synchronize it by mutex
    ############################################################
    def unregisterFunction(self, fun):
    
        currThreadName = threading.currentThread().getName()
        if self.mainThreadName != currThreadName:
            print("ERROR CFunctionProxyQueue.unregisterFunction: thread [%s] is not main thread" % currThreadName)
            raise AssertionError, ("ERROR CFunctionProxyQueue.unregisterFunction: thread [%s] is not main thread" % currThreadName)
            return False
            
        funName = fun.__name__
        
        print("INFO CFunctionProxyQueue.unregisterFunction: [%s]" % fun.__name__)
                    
        # check if function is not already registered
        if not (funName in self.registeredFunctions):
            print("WARNING CFunctionProxyQueue.unregisterFunction: function [%s] is not registered" %  funName)
            # maybe this should be allowed (without assertion)
            raise AssertionError, ("WARNING CFunctionProxyQueue.unregisterFunction: function [%s] is not registered" %  funName)
            return False
        
        # get appropriate item from function dictionary
        funItem = self.registeredFunctions[funName]
        
        # check if this item is the same as we want to unregister
        if funItem != fun:
            print("WARNING CFunctionProxyQueue.unregisterFunction: function [%s] is registered for diffrent object" %  funName)
            # maybe this should be allowed (without assertion)
            raise AssertionError, ("WARNING CFunctionProxyQueue.unregisterFunction: function [%s] is registered for diffrent object" %  funName)
            return False
            
        del self.registeredFunctions[funName]
        
        print("Info CFunctionProxyQueue.unregisterFunction: the function [%s] has been successfully unregistered" % funName)

        return True 
        
        
    ############################################################
    #       This method can be called only from mainThread
    #       so there is no need to synchronize it by mutex
    ############################################################
    def unregisterAllFunctions(self):
        print('unregisterAllFunctions')
        self.registeredFunctions.clear() 
        return
        
    def clearQueue(self):
        print('clearQueue')
        
        self.QueueLock.acquire()
        self.Queue = []
        self.QueueLock.release()
        
    def addToQueue(self, funName, retValue):
        print "addToQueue"
        item = CFunProxyQueueItem(funName, retValue)
        
        self.QueueLock.acquire()
        self.Queue.append(item)
        self.QueueLock.release()
        
    def processQueue(self):
       
       # Queue can be processed only from main thread
        currThreadName = threading.currentThread().getName()
        if self.mainThreadName != currThreadName:
            print("ERROR CFunctionProxyQueue.processQueue: Queue can be processed only from main thread, thread [%s] is not main thread" % currThreadName)
            raise AssertionError, ("ERROR CFunctionProxyQueue.processQueue: Queue can be processed only from main thread, thread [%s] is not main thread" % currThreadName)
            return False
            
            
        while True:
            QueueIsEmpty = False
            
            self.QueueLock.acquire()
            if len(self.Queue) > 0:
                #get CFunProxyQueueItem from mainList
                item = self.Queue.pop(0)
                print("CFunctionProxyQueue.processQueue")
            else:
                QueueIsEmpty = True 
                
            self.QueueLock.release()
            
            if QueueIsEmpty:
                return
                
            # check if function with such name is registered
            if not item.clientFunName in self.registeredFunctions:
                print("ERROR CFunctionProxyQueue.processQueue:: function with name [%s] is not registered",  item.clientFunName)
                raise AssertionError, ("ERROR CFunctionProxyQueue.processQueue:: function with name [%s] is not registered",  item.clientFunName)
                continue
                    
            #run function
            regFunItem = self.registeredFunctions[item.clientFunName]
            print("processQueue calling function %s" % item.clientFunName)
            regFunItem(item.retValue)           

        # and while True:
        return
        
        
###############################################################
#                   CFunctionProxyQueue TEST
###############################################################
'''
class CTest(object):
    def __init__(self):
        print("CTest")
        
    def ala(self):
        print "ala"
    
    def mialcz(self, ret):
        print "CTest Miaucze %d" % ret
        self.ala()
        
        self.alaMaKota = "Tak"
        return
        
kot = CTest()

kot2 = CTest()

gQueue = CFunctionProxyQueue()

#gQueue.registerFunction(kot.mialcz)
gQueue.registerFunction(kot2.mialcz)
gQueue.addToQueue("mialcz", 12)
gQueue.processQueue()
#gQueue.unregisterFunction(kot.mialcz)
gQueue.unregisterFunction(kot2.mialcz)

#print "\n\n %s" % kot.alaMaKota
print "\n\n %s" % kot2.alaMaKota
'''