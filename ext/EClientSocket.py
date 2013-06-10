#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# Translated source for EClientSocket.
##

# Source file: EClientSocket.java
# Target file: EClientSocket.py
#
# Original file copyright original author(s).
# This file copyright Troy Melhase, troy@gci.net.
#
# WARNING: all changes to this file will be lost.

from logging import debug

#from ib.ext.AnyWrapper import AnyWrapper
from ib.ext.ComboLeg import ComboLeg
from ib.ext.EClientErrors import EClientErrors
from ib.ext.EReader import EReader
from ib.ext.Util import Util

from ib.lib.overloading import overloaded
from ib.lib import synchronized, Socket, DataInputStream, DataOutputStream
from ib.lib import Double, Integer

#from socket import SHUT_RDWR
from threading import RLock
mlock = RLock()


class EClientSocket(object):
    """ generated source for EClientSocket

    """
    CLIENT_VERSION = 61
    SERVER_VERSION = 60
    EOL = 0  # '\0'?
    BAG_SEC_TYPE = "BAG"
    GROUPS = 1
    PROFILES = 2
    ALIASES = 3

    @classmethod
    def faMsgTypeName(cls, faDataType):
        faDataTypes = {cls.GROUPS: "GROUPS",
                       cls.PROFILES: "PROFILES",
                       cls.ALIASES: "ALIASES"}
        return faDataTypes.get(faDataType, None)

    REQ_MKT_DATA = 1
    CANCEL_MKT_DATA = 2
    PLACE_ORDER = 3
    CANCEL_ORDER = 4
    REQ_OPEN_ORDERS = 5
    REQ_ACCOUNT_DATA = 6
    REQ_EXECUTIONS = 7
    REQ_IDS = 8
    REQ_CONTRACT_DATA = 9
    REQ_MKT_DEPTH = 10
    CANCEL_MKT_DEPTH = 11
    REQ_NEWS_BULLETINS = 12
    CANCEL_NEWS_BULLETINS = 13
    SET_SERVER_LOGLEVEL = 14
    REQ_AUTO_OPEN_ORDERS = 15
    REQ_ALL_OPEN_ORDERS = 16
    REQ_MANAGED_ACCTS = 17
    REQ_FA = 18
    REPLACE_FA = 19
    REQ_HISTORICAL_DATA = 20
    EXERCISE_OPTIONS = 21
    REQ_SCANNER_SUBSCRIPTION = 22
    CANCEL_SCANNER_SUBSCRIPTION = 23
    REQ_SCANNER_PARAMETERS = 24
    CANCEL_HISTORICAL_DATA = 25
    REQ_CURRENT_TIME = 49
    REQ_REAL_TIME_BARS = 50
    CANCEL_REAL_TIME_BARS = 51
    REQ_FUNDAMENTAL_DATA = 52
    CANCEL_FUNDAMENTAL_DATA = 53
    REQ_CALC_IMPLIED_VOLAT = 54
    REQ_CALC_OPTION_PRICE = 55
    CANCEL_CALC_IMPLIED_VOLAT = 56
    CANCEL_CALC_OPTION_PRICE = 57
    REQ_GLOBAL_CANCEL = 58
    REQ_MARKET_DATA_TYPE = 59
    REQ_POSITIONS = 61
    REQ_ACCOUNT_SUMMARY = 62
    CANCEL_ACCOUNT_SUMMARY = 63
    CANCEL_POSITIONS = 64

    # ONLY TWS SERVER VERSIONS >= 60 ARE SUPPORTED
    MIN_SERVER_VER_SCALE_ORDERS3 = 60
    MIN_SERVER_VER_ORDER_COMBO_LEGS_PRICE = 61
    MIN_SERVER_VER_TRAILING_PERCENT = 62
    MIN_SERVER_VER_DELTA_NEUTRAL_OPEN_CLOSE = 66
    MIN_SERVER_VER_ACCT_SUMMARY = 67
    MIN_SERVER_VER_TRADING_CLASS = 68

    m_anyWrapper = None
    m_dos = None
    m_connected = bool()
    m_reader = None
    m_serverVersion = 0
    m_TwsTime = ""

    def serverVersion(self):
        return self.m_serverVersion

    def TwsConnectionTime(self):
        return self.m_TwsTime

    def wrapper(self):
        return self.m_anyWrapper

    def reader(self):
        return self.m_reader

    def __init__(self, anyWrapper):
        self.m_anyWrapper = anyWrapper

    # custom made destructor to ensure connection terminated upon object death
    def __del__(self):
        self.close()

    def isConnected(self):
        return self.m_connected

    @overloaded
    @synchronized(mlock)
    def eConnect(self, host, port, clientId):
        host = self.checkConnected(host)
        if host is None:
            return
        try:
            socket = Socket(host, port)
            self.eConnect(socket, clientId)
        except (Exception, ), e:
            self.eDisconnect()
            self.connectionError()
            print 'Connection Error: ', e.message

    def connectionError(self):
        self.m_anyWrapper.error(EClientErrors.NO_VALID_ID,
                                EClientErrors.CONNECT_FAIL.code(),
                                EClientErrors.CONNECT_FAIL.msg())
        self.m_reader = None

    def checkConnected(self, host):
        if self.m_connected:
            self.m_anyWrapper.error(EClientErrors.NO_VALID_ID,
                                    EClientErrors.ALREADY_CONNECTED.code(),
                                    EClientErrors.ALREADY_CONNECTED.msg())
            return
        if self.isNull(host):
            host = "127.0.0.1"
        return host

    def createReader(self, socket, dis):
        return EReader(socket, dis)

    @eConnect.register(object, Socket, int)
    @synchronized(mlock)
    def eConnect_0(self, socket, clientId):
        self.m_dos = DataOutputStream(socket.getOutputStream())
        self.send(self.CLIENT_VERSION)
        self.m_reader =\
            self.createReader(self, DataInputStream(socket.getInputStream()))
        self.m_serverVersion = self.m_reader.readInt()
        debug("Server Version:  %s", self.m_serverVersion)
        self.m_TwsTime = self.m_reader.readStr()
        debug("TWS Time at connection:  %s", self.m_TwsTime)
        if self.m_serverVersion < self.SERVER_VERSION:
            self.eDisconnect()
            self.m_anyWrapper.error(EClientErrors.NO_VALID_ID,
                                    EClientErrors.UPDATE_TWS.code(),
                                    EClientErrors.UPDATE_TWS.msg())
            return
        self.send(clientId)
        self.m_reader.start()
        self.m_connected = True

    @synchronized(mlock)
    def eDisconnect(self):
        if self.m_dos is None:
            return
        self.m_connected = False
        self.m_serverVersion = 0
        self.m_TwsTime = ""
        dos = self.m_dos = None
        reader = self.m_reader = None
        try:
            if reader is not None:
                reader.interrupt()
        except (Exception, ), e:
            print str(e)
        try:
            if dos is not None:
                dos.close()
        except (Exception, ), e:
            print str(e)

    @synchronized(mlock)
    def cancelScannerSubscription(self, tickerId):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.CANCEL_SCANNER_SUBSCRIPTION)
            self.send(VERSION)
            self.send(tickerId)
        except (Exception, ), e:
            self.error(tickerId, EClientErrors.FAIL_SEND_CANSCANNER, str(e))
            self.close()

    @synchronized(mlock)
    def reqScannerParameters(self):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.REQ_SCANNER_PARAMETERS)
            self.send(VERSION)
        except (Exception, ), e:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.FAIL_SEND_REQSCANNERPARAMETERS, str(e))
            self.close()

    @synchronized(mlock)
    def reqScannerSubscription(self, tickerId, subscription):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 3
        try:
            self.send(self.REQ_SCANNER_SUBSCRIPTION)
            self.send(VERSION)
            self.send(tickerId)
            self.sendMax(subscription.numberOfRows())
            self.send(subscription.instrument())
            self.send(subscription.locationCode())
            self.send(subscription.scanCode())
            self.sendMax(subscription.abovePrice())
            self.sendMax(subscription.belowPrice())
            self.sendMax(subscription.aboveVolume())
            self.sendMax(subscription.marketCapAbove())
            self.sendMax(subscription.marketCapBelow())
            self.send(subscription.moodyRatingAbove())
            self.send(subscription.moodyRatingBelow())
            self.send(subscription.spRatingAbove())
            self.send(subscription.spRatingBelow())
            self.send(subscription.maturityDateAbove())
            self.send(subscription.maturityDateBelow())
            self.sendMax(subscription.couponRateAbove())
            self.sendMax(subscription.couponRateBelow())
            self.send(subscription.excludeConvertible())
            self.sendMax(subscription.averageOptionVolumeAbove())
            self.send(subscription.scannerSettingPairs())
            self.send(subscription.stockTypeFilter())
        except (Exception, ), e:
            self.error(tickerId, EClientErrors.FAIL_SEND_REQSCANNER, str(e))
            self.close()

    @synchronized(mlock)
    def reqMktData(self, tickerId, contract, genericTickList, snapshot):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        if self.m_serverVersion < self.MIN_SERVER_VER_TRADING_CLASS:
            if contract.m_tradingClass != "":
                self.error(tickerId, EClientErrors.UPDATE_TWS,
                           "  It does not support tradingClass paramater in"
                           "reqContractDetails.")
        VERSION = 10
        try:
            self.send(self.REQ_MKT_DATA)
            self.send(VERSION)
            self.send(tickerId)
            self.send(contract.m_conId)
            self.send(contract.m_symbol)
            self.send(contract.m_secType)
            self.send(contract.m_expiry)
            self.send(contract.m_strike)
            self.send(contract.m_right)
            self.send(contract.m_multiplier)
            self.send(contract.m_exchange)
            self.send(contract.m_primaryExch)
            self.send(contract.m_currency)
            self.send(contract.m_localSymbol)
            if self.m_serverVersion >= self.MIN_SERVER_VER_TRADING_CLASS:
                self.send(contract.m_tradingClass)
            if self.BAG_SEC_TYPE.lower() == contract.m_secType.lower():
                if contract.m_comboLegs is None:
                    self.send(0)
                else:
                    self.send(len(contract.m_comboLegs))
                    for i in len(contract.m_comboLegs):
                        comboLeg = contract.m_comboLegs[i]
                        self.send(comboLeg.m_conId)
                        self.send(comboLeg.m_ratio)
                        self.send(comboLeg.m_action)
                        self.send(comboLeg.m_exchange)
            if contract.m_underComp is not None:
                underComp = contract.m_underComp
                self.send(True)
                self.send(underComp.m_conId)
                self.send(underComp.m_delta)
                self.send(underComp.m_price)
            else:
                self.send(False)
            self.send(genericTickList)
            self.send(snapshot)
        except (Exception, ), e:
            print 'Exception raised', tickerId
            self.error(tickerId, EClientErrors.FAIL_SEND_REQMKT, str(e))
            self.close()

    @synchronized(mlock)
    def cancelHistoricalData(self, tickerId):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.CANCEL_HISTORICAL_DATA)
            self.send(VERSION)
            self.send(tickerId)
        except (Exception, ), e:
            self.error(tickerId, EClientErrors.FAIL_SEND_CANHISTDATA, str(e))
            self.close()

    def cancelRealTimeBars(self, tickerId):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.CANCEL_REAL_TIME_BARS)
            self.send(VERSION)
            self.send(tickerId)
        except (Exception, ), e:
            self.error(tickerId, EClientErrors.FAIL_SEND_CANRTBARS, str(e))
            self.close()

    @synchronized(mlock)
    def reqHistoricalData(self, tickerId,
                          contract,
                          endDateTime,
                          durationStr,
                          barSizeSetting,
                          whatToShow,
                          useRTH,
                          formatDate):
        if not self.m_connected:
            self.error(tickerId, EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 5
        
        print self.REQ_HISTORICAL_DATA
        print VERSION
        print tickerId
        if self.m_serverVersion >= self.MIN_SERVER_VER_TRADING_CLASS:
            print contract.m_conId
        print 'symbol ', contract.m_symbol
        print contract.m_secType
        print contract.m_expiry
        print contract.m_strike
        print contract.m_right
        print contract.m_multiplier
        print contract.m_exchange
        print contract.m_primaryExch
        print contract.m_currency
        print contract.m_localSymbol
        if self.m_serverVersion >= self.MIN_SERVER_VER_TRADING_CLASS:
            print contract.m_tradingClass
        print 1 if contract.m_includeExpired else 0
        print endDateTime
        print barSizeSetting
        print durationStr
        print useRTH
        print whatToShow
        print formatDate
        if self.BAG_SEC_TYPE.lower() == contract.m_secType.lower():
            if contract.m_comboLegs is None:
                print 0
            else:
                print len(contract.m_comboLegs)
                comboLeg = ComboLeg()
                for i in xrange(len(contract.m_comboLegs)):
                    comboLeg = contract.m_comboLegs[i]
                    print comboLeg.m_conId
                    print comboLeg.m_ratio
                    print comboLeg.m_action
                    print comboLeg.m_exchange

        try:
            if self.m_serverVersion < self.MIN_SERVER_VER_TRADING_CLASS:
                if not self.IsEmpty(contract.m_tradingClass)\
                        or contract.m_conId > 0:
                    self.error(tickerId, EClientErrors.UPDATE_TWS,
                               "  It does not support conId or tradingClass"
                               "parameters in reqHistoricalData.")
                    return
            self.send(self.REQ_HISTORICAL_DATA)
            self.send(VERSION)
            self.send(tickerId)
            if self.m_serverVersion >= self.MIN_SERVER_VER_TRADING_CLASS:
                self.send(contract.m_conId)
            self.send(contract.m_symbol)
            self.send(contract.m_secType)
            self.send(contract.m_expiry)
            self.send(contract.m_strike)
            self.send(contract.m_right)
            self.send(contract.m_multiplier)
            self.send(contract.m_exchange)
            self.send(contract.m_primaryExch)
            self.send(contract.m_currency)
            self.send(contract.m_localSymbol)
            if self.m_serverVersion >= self.MIN_SERVER_VER_TRADING_CLASS:
                self.send(contract.m_tradingClass)
            self.send(1 if contract.m_includeExpired else 0)
            self.send(endDateTime)
            self.send(barSizeSetting)
            self.send(durationStr)
            self.send(useRTH)
            self.send(whatToShow)
            self.send(formatDate)
            if self.BAG_SEC_TYPE.lower() == contract.m_secType.lower():
                if contract.m_comboLegs is None:
                    self.send(0)
                else:
                    self.send(len(contract.m_comboLegs))
                    comboLeg = ComboLeg()
                    for i in xrange(len(contract.m_comboLegs)):
                        comboLeg = contract.m_comboLegs[i]
                        self.send(comboLeg.m_conId)
                        self.send(comboLeg.m_ratio)
                        self.send(comboLeg.m_action)
                        self.send(comboLeg.m_exchange)
        except (Exception, ), e:
            print e.message
            self.error(tickerId, EClientErrors.FAIL_SEND_REQHISTDATA, str(e))
            self.close()

    @synchronized(mlock)
    def reqRealTimeBars(self, tickerId,
                        contract,
                        barSize,
                        whatToShow,
                        useRTH):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        if self.m_serverVersion < self.MIN_SERVER_VER_TRADING_CLASS:
            if contract.m_tradingClass is not None or contract.m_conId > 0:
                self.error(tickerId, EClientErrors.UPDATE_TWS,
                           "  It does not support conId and tradingClass"
                           "parameters in reqRealTimeBars.")
        VERSION = 2
        try:
            self.send(self.REQ_REAL_TIME_BARS)
            self.send(VERSION)
            self.send(tickerId)
            if self.m_serverVersion > self.MIN_SERVER_VER_TRADING_CLASS:
                    self.send(contract.m_conId)
            self.send(contract.m_symbol)
            self.send(contract.m_secType)
            self.send(contract.m_expiry)
            self.send(contract.m_strike)
            self.send(contract.m_right)
            self.send(contract.m_multiplier)
            self.send(contract.m_exchange)
            self.send(contract.m_primaryExch)
            self.send(contract.m_currency)
            self.send(contract.m_localSymbol)
            if self.m_serverVersion > self.MIN_SERVER_VER_TRADING_CLASS:
                    self.send(contract.m_tradingClass)
            self.send(barSize)
            self.send(whatToShow)
            self.send(useRTH)
        except (Exception, ), e:
            self.error(tickerId, EClientErrors.FAIL_SEND_REQRTBARS, str(e))
            self.close()

    @synchronized(mlock)
    def reqContractDetails(self, reqId, contract):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        if self.m_serverVersion < self.MIN_SERVER_VER_TRADING_CLASS:
            if contract.m_tradingClass != "":
                self.error(reqId, EClientErrors.UPDATE_TWS,
                           "  It does not support tradingClass paramater in"
                           "reqContractDetails.")
        VERSION = 7
        try:
            self.send(self.REQ_CONTRACT_DATA)
            self.send(VERSION)
            self.send(reqId)
            self.send(contract.m_conId)
            self.send(contract.m_symbol)
            self.send(contract.m_secType)
            self.send(contract.m_expiry)
            self.send(contract.m_strike)
            self.send(contract.m_right)
            self.send(contract.m_multiplier)
            self.send(contract.m_exchange)
            self.send(contract.m_currency)
            self.send(contract.m_localSymbol)
            if self.m_serverVersion >= self.MIN_SERVER_VER_TRADING_CLASS:
                self.send(contract.m_tradingClass)
            self.send(contract.m_includeExpired)
            self.send(contract.m_secIdType)
            self.send(contract.m_secId)
        except (Exception, ), e:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.FAIL_SEND_REQCONTRACT, str(e))
            self.close()

    @synchronized(mlock)
    def reqMktDepth(self, tickerId, contract, numRows):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 4
        try:
            self.send(self.REQ_MKT_DEPTH)
            self.send(VERSION)
            self.send(tickerId)
            if self.m_serverVersion >= self.MIN_SERVER_VER_TRADING_CLASS:
                self.send(contract.m_conId)
            self.send(contract.m_symbol)
            self.send(contract.m_secType)
            self.send(contract.m_expiry)
            self.send(contract.m_strike)
            self.send(contract.m_right)
            self.send(contract.m_multiplier)
            self.send(contract.m_exchange)
            self.send(contract.m_currency)
            self.send(contract.m_localSymbol)
            if self.m_serverVersion >= self.MIN_SERVER_VER_TRADING_CLASS:
                self.send(contract.m_tradingClass)
            self.send(numRows)
        except (Exception, ), e:
            self.error(tickerId, EClientErrors.FAIL_SEND_REQMKTDEPTH, str(e))
            self.close()

    @synchronized(mlock)
    def cancelMktData(self, tickerId):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.CANCEL_MKT_DATA)
            self.send(VERSION)
            self.send(tickerId)
        except (Exception, ), e:
            self.error(tickerId, EClientErrors.FAIL_SEND_CANMKT, str(e))
            self.close()

    @synchronized(mlock)
    def cancelMktDepth(self, tickerId):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.CANCEL_MKT_DEPTH)
            self.send(VERSION)
            self.send(tickerId)
        except (Exception, ), e:
            self.error(tickerId, EClientErrors.FAIL_SEND_CANMKTDEPTH, str(e))
            self.close()

    @synchronized(mlock)
    def exerciseOptions(self, tickerId,
                        contract,
                        exerciseAction,
                        exerciseQuantity,
                        account,
                        override):
        if not self.m_connected:
            self.error(tickerId, EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 2
        try:
            if self.m_serverVersion < self.MIN_SERVER_VER_TRADING_CLASS:
                if not self.IsEmpty(contract.m_tradingClass)\
                        or contract.m_conId > 0:
                    self.error(tickerId, EClientErrors.UPDATE_TWS,
                               "  It does not support conId or tradingClass"
                               " parameters in exercise options.")
                    return
            self.send(self.EXERCISE_OPTIONS)
            self.send(VERSION)
            self.send(tickerId)
            if self.m_serverVersion >= self.MIN_SERVER_VER_TRADING_CLASS:
                self.send(contract.m_conId)
            self.send(contract.m_symbol)
            self.send(contract.m_secType)
            self.send(contract.m_expiry)
            self.send(contract.m_strike)
            self.send(contract.m_right)
            self.send(contract.m_multiplier)
            self.send(contract.m_exchange)
            self.send(contract.m_currency)
            self.send(contract.m_localSymbol)
            if self.m_serverVersion >= self.MIN_SERVER_VER_TRADING_CLASS:
                self.send(contract.m_tradingClass)
            self.send(exerciseAction)
            self.send(exerciseQuantity)
            self.send(account)
            self.send(override)
        except (Exception, ), e:
            self.error(tickerId, EClientErrors.FAIL_SEND_REQMKT, str(e))
            self.close()

    @synchronized(mlock)
    def placeOrder(self, id, contract, order):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
            if self.m_serverVersion < self.MIN_SERVER_VER_SCALE_ORDERS3:
                if order.m_scalePriceAdjustIncrement > 0\
                        and order.m_scalePriceIncrement != Double.MAX_VALUE:
                    if order.m_scalePriceAdjustValue != Integer.MAX_VALUE\
                            or order.m_scaleProfitOffset != Double.MAX_VALUE\
                            or order.m_scaleAutoReset\
                            or order.m_scaleInitPosition != Integer.MAX_VALUE\
                            or order.m_scaleInitFillQty != Integer.MAX_VALUE\
                            or order.m_scaleRandomPercent:
                        self.error(id, EClientErrors.UPDATE_TWS,
                                   "  It does not support Scale order "
                                   "parameters: PriceAdjustValue, "
                                   "PriceAdjustInterval, ProfitOffset, "
                                   "AutoReset, InitPosition, InitFillQty and "
                                   "RandomPercent.")
                        return
            if self.m_serverVersion\
                    < self.MIN_SERVER_VER_ORDER_COMBO_LEGS_PRICE\
                    and self.BAGS_SEC_TYPE.equalsIgnoreCase(
                        contract.m_secType):
                if not self.IsEmpty(order.m_orderComboLegs):
                    for i in xrange(len(order.m_orderCombaLegs)):
                        orderComboLeg = order.m_orderComboLegs.get(i)
                        if orderComboLeg.m_price != Double.MAX_VALUE:
                            self.error(id, EClientErrors.UPDATE_TWS,
                                       "  It does not support per-leg prices"
                                       " for order combo legs.")
                            return
            if self.m_serverVersion < self.MIN_SERVER_VER_TRAILING_PERCENT:
                if order.m_trailingPercent != Double.MAX_VALUE:
                    self.error(id, EClientErrors.UPDATE_TWS,
                               "  It does not support trailing percent"
                               " parameters.")
                    return
            if self.m_serverVersion < self.MIN_SERVER_VER_TRADING_CLASS:
                if not self.IsEmpty(contract.m_tradingClass):
                    self.error(id, EClientErrors.UPDATE_TWS, "  It does not "
                               "support tradingClass parameters in placeOrder")
                    return
        VERSION = 40
        try:
            self.send(self.PLACE_ORDER)
            self.send(VERSION)
            self.send(id)
            self.send(contract.m_conId)
            self.send(contract.m_symbol)
            self.send(contract.m_secType)
            self.send(contract.m_expiry)
            self.send(contract.m_strike)
            self.send(contract.m_right)
            self.send(contract.m_multiplier)
            self.send(contract.m_exchange)
            self.send(contract.m_primaryExch)
            self.send(contract.m_currency)
            self.send(contract.m_localSymbol)
            if self.m_serverVersion >= self.MIN_SERVER_VER_TRADING_CLASS:
                self.send(contract.m_tradingClass)
            self.send(contract.m_secIdType)
            self.send(contract.m_secId)
            self.send(order.m_action)
            self.send(order.m_totalQuantity)
            self.send(order.m_orderType)
            if self.m_serverVersion\
                    < self.MIN_SERVER_VER_ORDER_COMBO_LEGS_PRICE:
                self.send(0 if order.m_lmtPrice == Double.MAX_VALUE
                          else order.m_lmtPrice)
            else:
                self.sendMax(order.m_lmtPrice)
            if self.m_serverVersion < self.MIN_SERVER_VER_TRAILING_PERCENT:
                self.send(0 if order.m_auxPrice == Double.MAX_VALUE
                          else order.m_ausPrice)
            else:
                self.sendMax(order.m_lmtPrice)
            self.send(order.m_tif)
            self.send(order.m_ocaGroup)
            self.send(order.m_account)
            self.send(order.m_openClose)
            self.send(order.m_origin)
            self.send(order.m_orderRef)
            self.send(order.m_transmit)
            self.send(order.m_parentId)
            self.send(order.m_blockOrder)
            self.send(order.m_sweepToFill)
            self.send(order.m_displaySize)
            self.send(order.m_triggerMethod)
            self.send(order.m_outsideRth)
            self.send(order.m_hidden)
            if self.BAG_SEC_TYPE.lower() == contract.m_secType.lower():
                if contract.m_comboLegs is None:
                    self.send(0)
                else:
                    self.send(len(contract.m_comboLegs))
                    for i in xrange(len(contract.m_comboLegs)):
                        comboLeg = contract.m_comboLegs[i]
                        self.send(comboLeg.m_conId)
                        self.send(comboLeg.m_ratio)
                        self.send(comboLeg.m_action)
                        self.send(comboLeg.m_exchange)
                        self.send(comboLeg.m_openClose)
                        self.send(comboLeg.m_shortSaleSlot)
                        self.send(comboLeg.m_designatedLocation)
                        self.send(comboLeg.m_exemptCode)
            if self.m_serverVersion\
                    >= self.MIN_SERVER_VER_ORDER_COMBO_LEGS_PRICE\
                    and self.BAG_SEC_TYPE.lower()\
                    == contract.m_secType.lower():
                if order.m_orderComboLegs is None:
                    self.send(0)
                else:
                    self.send(len(order.m_orderComboLegs))
                    for i in xrange(len(order.m_orderComboLegs)):
                        orderComboLeg = order.m_orderComboLegs[i]
                        self.sendMax(orderComboLeg.m_price)
            if self.BAG_SEC_TYPE.lower == contract.m_secType.lower():
                smartComboRoutingParams = order.m_smartComboRoutingParams
                smartComboRoutingParamsCount = 0\
                    if smartComboRoutingParams is None\
                    else len(smartComboRoutingParams)
                self.send(smartComboRoutingParamsCount)
                if smartComboRoutingParamsCount > 0:
                    for i in xrange(smartComboRoutingParamsCount):
                        tagValue = smartComboRoutingParams.get(i)
                        self.send(tagValue.m_tag)
                        self.send(tagValue.m_value)
            self.send("")  # deprecated sharesAllocation field
            self.send(order.m_discretionaryAmt)
            self.send(order.m_goodAfterTime)
            self.send(order.m_goodTillDate)
            self.send(order.m_faGroup)
            self.send(order.m_faMethod)
            self.send(order.m_faPercentage)
            self.send(order.m_faProfile)
            self.send(order.m_shortSaleSlot)
            self.send(order.m_designatedLocation)
            self.send(order.m_exemptCode)
            self.send(order.m_ocaType)
            self.send(order.m_rule80A)
            self.send(order.m_settlingFirm)
            self.send(order.m_allOrNone)
            self.sendMax(order.m_minQty)
            self.sendMax(order.m_percentOffset)
            self.send(order.m_eTradeOnly)
            self.send(order.m_firmQuoteOnly)
            self.sendMax(order.m_nbboPriceCap)
            self.sendMax(order.m_auctionStrategy)
            self.sendMax(order.m_startingPrice)
            self.sendMax(order.m_stockRefPrice)
            self.sendMax(order.m_delta)
            self.sendMax(order.m_stockRangeLower)
            self.sendMax(order.m_stockRangeUpper)
            self.send(order.m_overridePercentageConstraints)
            self.sendMax(order.m_volatility)
            self.sendMax(order.m_volatilityType)
            self.send(order.m_deltaNeutralOrderType)
            self.sendMax(order.m_deltaNeutralAuxPrice)
            if not self.IsEmpty(order.m_deltaNeutralOrderType):
                self.send(order.m_deltaNeutralConId)
                self.send(order.m_deltaNeutralSettlingFirm)
                self.send(order.m_deltaNeutralClearingAccount)
                self.send(order.m_deltaNeutralClearingIntent)
            if self.m_serverVersion\
                    >= self.MIN_SERVER_VER_DELTA_NEUTRAL_OPEN_CLOSE\
                    and not self.IsEmpty(order.m_deltaNeutralOrderType):
                self.send(order.m_deltaNeutralOpenClose)
                self.send(order.m_deltaNeutralShortSale)
                self.send(order.m_deltaNeutralShortSaleSlot)
                self.send(order.m_deltaNeutralDesignatedLocation)
            self.send(order.m_continuousUpdate)
            self.sendMax(order.m_referencePriceType)
            if (self.m_serverVersion == 26):
                lower = order.m_stockRangeLower\
                    if order.m_orderType == "VOL"\
                    else Double.MAX_VALUE
                upper = order.m_stockRangeUpper\
                    if order.m_orderType == "VOL"\
                    else Double.MAX_VALUE
                self.sendMax(lower)
                self.sendMax(upper)
            self.sendMax(order.m_referencePriceType)
            self.sendMax(order.m_trailStopPrice)
            if self.m_serverVersion >= self.MIN_SERVER_VER_TRAILING_PERCENT:
                    self.sendMax(order.m_trailingPercent)
            self.sendMax(order.m_scaleInitLevelSize)
            self.sendMax(order.m_scaleSubsLevelSize)
            self.sendMax(order.m_scalePriceIncrement)
            if self.m_serverVersion >= self.MIN_SERVER_VER_SCALE_ORDERS3\
                    and order.m_scalePriceIncrement > 0.0\
                    and order.m_scalePriceIncrement != Double.MAX_VALUE:
                self.sendMax(order.m_scalePriceAdjustValue)
                self.sendMax(order.m_scalePriceAdjustInterval)
                self.sendMax(order.m_scalePriceAdjustInterval)
                self.sendMax(order.m_scaleProfitOffset)
                self.send(order.m_scaleAutoReset)
                self.sendMax(order.m_scaleInitPosition)
                self.sendMax(order.m_scaleInitFillQty)
                self.send(order.m_scaleRandomPercent)
            self.send(order.m_hedgeType)
            if not self.IsEmpty(order.m_hedgeType):
                self.send(order.m_hedgeParam)
            self.send(order.m_optOutSmartRouting)
            self.send(order.m_clearingAccount)
            self.send(order.m_clearingIntent)
            self.send(order.m_notHeld)
            if contract.m_underComp is not None:
                underComp = contract.m_underComp
                self.send(True)
                self.send(underComp.m_conId)
                self.send(underComp.m_delta)
                self.send(underComp.m_price)
            else:
                self.send(False)
            self.send(order.m_algoStrategy)
            if not self.IsEmpty(order.m_algoStrategy):
                algoParams = order.m_algoParams
                algoParamsCount = 0 if algoParams is None else len(algoParams)
                self.send(algoParamsCount)
                if algoParamsCount > 0:
                    for i in xrange(algoParamsCount):
                        tagValue = algoParams[i]
                        self.send(tagValue.m_tag)
                        self.send(tagValue.m_value)
            self.send(order.m_whatIf)
        except (Exception, ), e:
            self.error(id, EClientErrors.FAIL_SEND_ORDER, str(e))
            self.close()

    @synchronized(mlock)
    def reqAccountUpdates(self, subscribe, acctCode):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 2
        try:
            self.send(self.REQ_ACCOUNT_DATA)
            self.send(VERSION)
            self.send(subscribe)
            self.send(acctCode)
        except (Exception, ), e:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.FAIL_SEND_ACCT, str(e))
            self.close()

    @synchronized(mlock)
    def reqExecutions(self, reqId, filter):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 3
        try:
            self.send(self.REQ_EXECUTIONS)
            self.send(VERSION)
            self.send(reqId)
            self.send(filter.m_clientId)
            self.send(filter.m_acctCode)
            self.send(filter.m_time)  # formatted as "yyyymmdd-hh:mm:ss"
            self.send(filter.m_symbol)
            self.send(filter.m_secType)
            self.send(filter.m_exchange)
            self.send(filter.m_side)
        except (Exception, ), e:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.FAIL_SEND_EXEC, str(e))
            self.close()

    @synchronized(mlock)
    def cancelOrder(self, id):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.CANCEL_ORDER)
            self.send(VERSION)
            self.send(id)
        except (Exception, ), e:
            self.error(id, EClientErrors.FAIL_SEND_CORDER, str(e))
            self.close()

    @synchronized(mlock)
    def reqOpenOrders(self):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.REQ_OPEN_ORDERS)
            self.send(VERSION)
        except (Exception, ), e:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.FAIL_SEND_OORDER, str(e))
            self.close()

    @synchronized(mlock)
    def reqIds(self, numIds):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.REQ_IDS)
            self.send(VERSION)
            self.send(numIds)
        except (Exception, ), e:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.FAIL_SEND_CORDER, str(e))
            self.close()

    @synchronized(mlock)
    def reqNewsBulletins(self, allMsgs):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.REQ_NEWS_BULLETINS)
            self.send(VERSION)
            self.send(allMsgs)
        except (Exception, ), e:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.FAIL_SEND_CORDER, str(e))
            self.close()

    @synchronized(mlock)
    def cancelNewsBulletins(self):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.CANCEL_NEWS_BULLETINS)
            self.send(VERSION)
        except (Exception, ), e:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.FAIL_SEND_CORDER, str(e))
            self.close()

    @synchronized(mlock)
    def setServerLogLevel(self, logLevel):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.SET_SERVER_LOGLEVEL)
            self.send(VERSION)
            self.send(logLevel)
        except (Exception, ), e:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.FAIL_SEND_SERVER_LOG_LEVEL, str(e))
            self.close()

    @synchronized(mlock)
    def reqAutoOpenOrders(self, bAutoBind):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.REQ_AUTO_OPEN_ORDERS)
            self.send(VERSION)
            self.send(bAutoBind)
        except (Exception, ), e:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.FAIL_SEND_OORDER, str(e))
            self.close()

    @synchronized(mlock)
    def reqAllOpenOrders(self):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.REQ_ALL_OPEN_ORDERS)
            self.send(VERSION)
        except (Exception, ), e:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.FAIL_SEND_OORDER, str(e))
            self.close()

    @synchronized(mlock)
    def reqManagedAccts(self):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.REQ_MANAGED_ACCTS)
            self.send(VERSION)
        except (Exception, ), e:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.FAIL_SEND_OORDER, str(e))
            self.close()

    @synchronized(mlock)
    def requestFA(self, faDataType):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.REQ_FA)
            self.send(VERSION)
            self.send(faDataType)
        except (Exception, ), e:
            self.error(faDataType, EClientErrors.FAIL_SEND_FA_REQUEST, str(e))
            self.close()

    @synchronized(mlock)
    def replaceFA(self, faDataType, xml):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.REPLACE_FA)
            self.send(VERSION)
            self.send(faDataType)
            self.send(xml)
        except (Exception, ), e:
            self.error(faDataType, EClientErrors.FAIL_SEND_FA_REPLACE, str(e))
            self.close()

    @synchronized(mlock)
    def reqCurrentTime(self):
        if not self.m_connected:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.REQ_CURRENT_TIME)
            self.send(VERSION)
        except (Exception, ), e:
            self.error(EClientErrors.NO_VALID_ID,
                       EClientErrors.FAIL_SEND_REQCURRTIME, str(e))
            self.close()

    @synchronized(mlock)
    def reqFundamentalData(self, reqId, contract, reportType):
        if not self.m_connected:
            self.error(reqId, EClientErrors.NOT_CONNECTED, "")
            return
        if self.m_serverVersion < self.MIN_SERVER_VER_TRADING_CLASS:
            if contract.m_conId > 0:
                self.error(reqId, EClientErrors.UPDATE_TWS,
                           "  It does not support conId parameter in"
                           "reqFundamentalData.")
            return
        VERSION = 2
        try:
            self.send(self.REQ_FUNDAMENTAL_DATA)
            self.send(VERSION)
            self.send(reqId)
            if self.m_serverVersion >= self.MIN_SERVER_VER_TRADING_CLASS:
                self.send(contract.m_conId)
            self.send(contract.m_symbol)
            self.send(contract.m_secType)
            self.send(contract.m_exchange)
            self.send(contract.m_primaryExch)
            self.send(contract.m_currency)
            self.send(contract.m_localSymbol)
            self.send(reportType)
        except (Exception, ), e:
            self.error(reqId, EClientErrors.FAIL_SEND_REQFUNDDATA, str(e))
            self.close()

    @synchronized(mlock)
    def cancelFundamentalData(self, reqId):
        if not self.m_connected:
            self.error(reqId, EClientErrors.NOT_CONNECTED, "")
            return
        VERSION = 1
        try:
            self.send(self.CANCEL_FUNDAMENTAL_DATA)
            self.send(VERSION)
            self.send(reqId)
        except (Exception, ), e:
            self.error(reqId, EClientErrors.FAIL_SEND_CANFUNDDATA, str(e))
            self.close()

    @synchronized(mlock)
    def calculateImpliedVolatility(self, reqId, contract,
                                   optionPrice, underPrice):
        if not self.m_connected:
            self.error(reqId, EClientErrors.NOT_CONNECTED, "")
            return
        if self.m_serverVersion < self.MIN_SERVER_VER_TRADING_CLASS:
            if not self.IsEmpty(contract.m_tradingClass):
                self.error(reqId, EClientErrors.UPDATE_TWS, "It does not "
                           "support tradingClass parameter in "
                           "calculateImpliedVolaitility.")
                return
        VERSION = 2
        try:
            self.send(self.REQ_CALC_IMPLIED_VOLAT)
            self.send(VERSION)
            self.send(reqId)
            self.send(contract.m_conId)
            self.send(contract.m_symbol)
            self.send(contract.m_secType)
            self.send(contract.m_expiry)
            self.send(contract.m_strike)
            self.send(contract.m_right)
            self.send(contract.m_multiplier)
            self.send(contract.m_exchange)
            self.send(contract.m_primaryExch)
            self.send(contract.m_currency)
            self.send(contract.m_localSymbol)
            if(self.m_serverVersion >= self.MIN_SERVER_VER_TRADING_CLASS):
                self.send(contract.m_tradingClass)
            self.send(optionPrice)
            self.send(underPrice)
        except (Exception, ), e:
            self.error(reqId, EClientErrors.FAIL_SEND_REEQCALCIMPLIEDVOLAT,
                       str(e))
            self.close()

    @overloaded
    @synchronized(mlock)
    def error(self, err):
        self.m_anyWrapper.error(err)

    @error.register(object, int, int, str)
    @synchronized(mlock)
    def error_0(self, id, errorCode, errorMsg):
        self.m_anyWrapper.error(id, errorCode, errorMsg)

    def close(self):
        self.eDisconnect()
        self.wrapper().connectionClosed()

    @classmethod
    def is_(cls, strval):
        return strval is not None and len(strval) > 0

    @classmethod
    def isNull(cls, strval):
        return not cls.is_(strval)

    @error.register(object, int, EClientErrors.CodeMsgPair, str)
    def error_1(self, id, pair, tail):
        self.error(id, pair.code(), pair.msg() + tail)

    # TO DO:  Use Try/Except to raise IOExceptions in all functions below
    #bar last (isEmpty)
    @overloaded
    def send(self, strval):
        if not self.IsEmpty(strval):
            self.m_dos.write(strval.getBytes())
        self.sendEOL()

    def sendEOL(self):
        self.m_dos.write(self.EOL)

    @send.register(object, int)
    def send_0(self, val):
        self.send(str(val))

    @send.register(object, str)
    def send_1(self, val):
        self.m_dos.write(val)
        self.sendEOL()

    @send.register(object, float)
    def send_2(self, val):
        self.send(str(val))

    @send.register(object, long)
    def send_3(self, val):
        self.send(str(val))

    @overloaded
    def sendMax(self, val):
        if (val == Double.MAX_VALUE):
            self.sendEOL()
        else:
            self.send(str(val))

    @sendMax.register(object, int)
    def sendMax_0(self, val):
        if (val == Integer.MAX_VALUE):
            self.sendEOL()
        else:
            self.send(str(val))

    @send.register(object, bool)
    def send_4(self, val):
        self.send(1 if val else 0)

    @classmethod
    def IsEmpty(cls, strval):
        return Util.StringIsEmpty(strval)
