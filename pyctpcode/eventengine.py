from collections import defaultdict
from queue import Empty, Queue
from threading import Thread
from time import sleep, time

from event import Event

EVENT_TIMER = 'event_timer'
class EventEngine(object):
    '''event engin for all the message'''

    def __init__(self):
        self.__queue = Queue()
        self.__active = False
        self.__thread = Thread(target=self.__run)
        self.__handlers = defaultdict(list)
        self.__generalHandlers = []
        self.__timer = Thread(target=self.__runTimer)
        self.__timerActive = False
        self.__timerSleep = 0.5

    def __run(self):
        """run engine"""
        while self.__active == True:
            try:
                event = self.__queue.get(block=True, timeout=1)  # 获取事件的阻塞时间1秒
                self.__process(event)
            except Empty:
                pass

    #----------------------------------------------------------------------
    def __process(self, event):
        """process event"""
        if event.type_ in self.__handlers:
            [handler(event) for handler in self.__handlers[event.type_]]
        if self.__generalHandlers:
            [handler(event) for handler in self.__generalHandlers]

    #----------------------------------------------------------------------
    def __runTimer(self):
        while self.__timerActive:
            event = Event(type_=EVENT_TIMER)
            self.put(event)
            sleep(self.__timerSleep)

    #----------------------------------------------------------------------
    def start(self, timer=True):
        self.__active = True
        self.__thread.start()
        if timer:
            self.__timerActive = True
            self.__timer.start()

    #----------------------------------------------------------------------
    def stop(self):
        self.__active = False
        self.__timerActive = False
        self.__timer.join()
        self.__thread.join()

    #----------------------------------------------------------------------
    def register(self, type_, handler):
        handlerList = self.__handlers[type_]
        if handler not in handlerList:
            handlerList.append(handler)

    #----------------------------------------------------------------------
    def unregister(self, type_, handler):
        handlerList = self.__handlers[type_]
        if handler in handlerList:
            handlerList.remove(handler)
        if not handlerList:
            del self.__handlers[type_]

    def registerGeneralHandler(self, handler):
        if handler not in self.__generalHandlers:
            self.__generalHandlers.append(handler)

    def unregisterGeneralHandler(self, handler):
        if handler in self.__generalHandlers:
            self.__generalHandlers.remove(handler)

    def put(self, event):
        self.__queue.put(event)

def pevent(event):
    print(event.type_)

def test():
    testee = EventEngine()
    testee.registerGeneralHandler(pevent)
    testee.start()
    for i in range(5):
        sleep(1)
    testee.stop()
if __name__ == "__main__":
    test()
