# -*- coding: utf-8 -*-

import hashlib
import os
import sys
import tempfile
import time
from event import Event
from eventengine import EventEngine

from ctp import ApiStruct, MdApi
from sqlalchemy import create_engine

dbstr = 'postgres://aoctp:aoctp@localhost:5432/aoctp'


EVENT_MARKETDATA  = 'event_marketdata'
class MyMdApi(MdApi):
    def __init__(self, brokerID, userID, password, instrumentIDs):
        self.requestID = 0
        self.brokerID = brokerID
        self.userID = userID
        self.password = password
        self.instrumentIDs = instrumentIDs
        self.Create()
        self.Ready = False

    def Create(self):
        dir = b''.join((b'ctp.futures', self.brokerID, self.userID))
        dir = hashlib.md5(dir).hexdigest()
        dir = os.path.join(tempfile.gettempdir(), dir, 'Md') + os.sep
        if not os.path.isdir(dir): os.makedirs(dir)
        MdApi.Create(self,
                     os.fsencode(dir) if sys.version_info[0] >= 3 else dir)

    def RegisterFront(self, front):
        if isinstance(front, bytes):
            return MdApi.RegisterFront(self, front)
        for front in front:
            MdApi.RegisterFront(self, front)

    def OnFrontConnected(self):
        print('OnFrontConnected: Login...')
        req = ApiStruct.ReqUserLogin(
            BrokerID=self.brokerID, UserID=self.userID, Password=self.password)
        self.requestID += 1
        self.ReqUserLogin(req, self.requestID)

    def OnFrontDisconnected(self, nReason):
        print('OnFrontDisconnected:', nReason)

    def OnHeartBeatWarning(self, nTimeLapse):
        print('OnHeartBeatWarning:', nTimeLapse)

    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
        print('OnRspUserLogin:', pRspInfo)
        if pRspInfo.ErrorID == 0:  # Success
            print('GetTradingDay:', self.GetTradingDay())
            self.Ready = True

    def OnRspSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID,
                           bIsLast):
        print('OnRspSubMarketData:', pRspInfo)

    def OnRspUnSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID,
                             bIsLast):
        print('OnRspUnSubMarketData:', pRspInfo)

    def OnRspError(self, pRspInfo, nRequestID, bIsLast):
        print('OnRspError:', pRspInfo)

    def OnRspUserLogout(self, pUserLogout, pRspInfo, nRequestID, bIsLast):
        print('OnRspUserLogout:', pRspInfo)

    def OnRtnDepthMarketData(self, pDepthMarketData):
        #print('OnRtnDepthMarketData:', pDepthMarketData)
        event = Event(EVENT_MARKETDATA)
        event.dict_=pDepthMarketData
        self.engine.put(event)

    def BindEventEngine(self, engine):
        self.engine = engine

class dbhandler(object):
    def __init__(self):
        self.db = create_engine(dbstr)

    def pinfo(self,event):
        print(event.dict_)
if __name__ == '__main__':
    mdapi = MyMdApi(b'8888', b'111712', b'427278', [b'rb1801'])
    mdapi.RegisterFront(b'tcp://118.242.3.178:41173')
    mdapi.Init()
    try:
        while mdapi.Ready == False:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    loghadler = dbhandler()
    engine = EventEngine()
    engine.registerGeneralHandler(loghadler.pinfo)
    engine.start()
    mdapi.BindEventEngine(engine)
    mdapi.SubscribeMarketData([b'rb1801',])
    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
