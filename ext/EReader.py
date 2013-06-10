#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# Translated source for EReader.
##

# Source file: EReader.java
# Target file: EReader.py
#
# Original file copyright original author(s).
# This file copyright Troy Melhase, troy@gci.net.
#
# WARNING: all changes to this file will be lost.

from ib.lib import Boolean, Double, DataInputStream, Integer,\
    Long, StringBuffer, Thread
from ib.lib.overloading import overloaded

from ib.ext.Contract import Contract
from ib.ext.ContractDetails import ContractDetails
from ib.ext.Execution import Execution
from ib.ext.Order import Order
from ib.ext.OrderState import OrderState
from ib.ext.TickType import TickType
from ib.ext.UnderComp import UnderComp
from ib.ext.Util import Util
from ib.ext.TagValue import TagValue
from ib.ext.CommissionReport import CommissionReport
from ib.ext.EClientErrors import EClientErrors

from ib.lib.logger import logger


class EReader(Thread):
    """ generated source for EReader

    """
    TICK_PRICE = 1
    TICK_SIZE = 2
    ORDER_STATUS = 3
    ERR_MSG = 4
    OPEN_ORDER = 5
    ACCT_VALUE = 6
    PORTFOLIO_VALUE = 7
    ACCT_UPDATE_TIME = 8
    NEXT_VALID_ID = 9
    CONTRACT_DATA = 10
    EXECUTION_DATA = 11
    MARKET_DEPTH = 12
    MARKET_DEPTH_L2 = 13
    NEWS_BULLETINS = 14
    MANAGED_ACCTS = 15
    RECEIVE_FA = 16
    HISTORICAL_DATA = 17
    BOND_CONTRACT_DATA = 18
    SCANNER_PARAMETERS = 19
    SCANNER_DATA = 20
    TICK_OPTION_COMPUTATION = 21
    TICK_GENERIC = 45
    TICK_STRING = 46
    TICK_EFP = 47
    CURRENT_TIME = 49
    REAL_TIME_BARS = 50
    FUNDAMENTAL_DATA = 51
    CONTRACT_DATA_END = 52
    OPEN_ORDER_END = 53
    ACCT_DOWNLOAD_END = 54
    EXECUTION_DATA_END = 55
    DELTA_NEUTRAL_VALIDATION = 56
    TICK_SNAPSHOT_END = 57
    MARKET_DATA_TYPE = 58
    COMMISSION_REPORT = 59
    POSITION = 61
    POSITION_END = 62
    ACCOUNT_SUMMARY = 63
    ACCOUNT_SUMMARY_END = 64

    m_parent = None
    m_dis = None

    def parent(self):
        return self.m_parent

    def eWrapper(self):
        return self.parent().wrapper()

    @overloaded
    def __init__(self, parent, dis):
        self.__init__("EReader", parent, dis)

    @__init__.register(object, str, object, DataInputStream)
    def __init___0(self, name, parent, dis):
        Thread.__init__(self, name, parent, dis)
        self.setName(name)
        self.m_parent = parent
        self.m_dis = dis

    def run(self):
        try:
            while not self.isInterrupted() and self.processMsg(self.readInt()):
                pass
        except (Exception, ), ex:
            errmsg = ("Exception while processing message.  ")
            logger().exception(errmsg)
            if self.parent().isConnected():
                self.eWrapper().error(ex)
        if self.parent().isConnected():
            self.m_parent.close()
        try:
            self.m_dis.close()
            self.m_dis = None
        except (IOError, ), ex:
            print 'Data Import Stream IO error.'
            raise IOError

    def processMsg(self, msgId):
        if (msgId == -1):
            return False
        if msgId == self.TICK_PRICE:
            version = self.readInt()
            MIN_VERSION = 6
            if version < MIN_VERSION:
                print "Old TWS Server not supported."
                print "EREADER: Tick Price Min Version = ", MIN_VERSION,\
                      "Current version = ", version
                raise Exception
            tickerId = self.readInt()
            tickType = self.readInt()
            price = self.readDouble()
            size = self.readInt()
            canAutoExecute = self.readInt()
            self.eWrapper().tickPrice(tickerId, tickType, price,
                                      canAutoExecute)
            tickTypes = {1: 0, 2: 3, 4: 5}  # Bid/Ask/Last
            sizeTickType = tickTypes.get(tickType, -1)  # -1 = Not a tick
            if (sizeTickType != -1):
                self.eWrapper().tickSize(tickerId, sizeTickType, size)
        elif msgId == self.TICK_SIZE:
            version = self.readInt()
            tickerId = self.readInt()
            tickType = self.readInt()
            size = self.readInt()
            self.eWrapper().tickSize(tickerId, tickType, size)
        elif msgId == self.POSITION:
            version = self.readInt()
            account = self.readStr()
            contract = Contract()
            contract.m_conId = self.readInt()
            contract.m_symbol = self.readStr()
            contract.m_secType = self.readStr()
            contract.m_expiry = self.readStr()
            contract.m_strike = self.readDouble()
            contract.m_right = self.readStr()
            contract.m_multiplier = self.readStr()
            contract.m_exchange = self.readStr()
            contract.m_currency = self.readStr()
            contract.m_localSymbol = self.readStr()
            if version >= 2:
                contract.m_tradingClass = self.readStr()
            pos = self.readInt()
            self.eWrapper().position(account, contract, pos)
        elif msgId == self.POSITION_END:
            version = self.readInt()
            self.eWrapper().positionEnd()
        elif msgId == self.ACCOUNT_SUMMARY:
            version = self.readInt()
            reqId = self.readInt()
            account = self.readStr()
            tag = self.readStr()
            value = self.readStr()
            currency = self.readStr()
            self.eWrapper().accountSummary(reqId, account, tag, value,
                                           currency)
        elif msgId == self.ACCOUNT_SUMMARY_END:
            version = self.readInt()
            reqId = self.readInt()
            self.eWrapper().accountSummaryEnd(reqId)
        elif msgId == self.TICK_OPTION_COMPUTATION:
            version = self.readInt()
            MIN_VERSION = 6
            if version < MIN_VERSION:
                print "Old TWS Server not supported."
                print "EREADER: Tick Option Computation Min Version = ",\
                    MIN_VERSION,\
                      "Current version = ", version
                raise Exception
            tickerId = self.readInt()
            tickType = self.readInt()
            impliedVol = self.readDouble()
            if impliedVol < 0:  # -1 is 'not yet computed' indicator
                impliedVol = Double.MAX_VALUE
            delta = self.readDouble()
            if abs(delta) > 1:  # -2 is the 'not yet computed' indicator
                delta = Double.MAX_VALUE
            optPrice = float()
            pvDividend = float()
            gamma = Double.MAX_VALUE
            vega = Double.MAX_VALUE
            theta = Double.MAX_VALUE
            undPrice = Double.MAX_VALUE
            optPrice = self.readDouble()
            if optPrice < 0:  # -1 is 'not yet computed' indicator
                optPrice = Double.MAX_VALUE
            pvDividend = self.readDouble()
            if pvDividend < 0:  # -1 is 'not yet computed' indicator
                pvDividend = Double.MAX_VALUE
            gamma = self.readDouble()
            if abs(gamma) > 1:  # -2 is 'not yet computed' indicator
                gamma = Double.MAX_VALUE
            vega = self.readDouble()
            if abs(vega) > 1:  # -2 is 'not yet computed' indicator
                vega = Double.MAX_VALUE
            theta = self.readDouble()            
            if abs(theta) > 1:  # -2 is 'not yet computed' indicator
                theta = Double.MAX_VALUE
            undPrice = self.readDouble()
            if undPrice < 0:  # -1 is 'not yet computed' indicator
                undPrice = Double.MAX_VALUE

            self.eWrapper().tickOptionComputation(tickerId, tickType,
                                                  impliedVol, delta,
                                                  optPrice, pvDividend,
                                                  gamma, vega, theta, undPrice)
        elif msgId == self.TICK_GENERIC:
            version = self.readInt()
            tickerId = self.readInt()
            tickType = self.readInt()
            value = self.readDouble()
            self.eWrapper().tickGeneric(tickerId, tickType, value)
        elif msgId == self.TICK_STRING:
            version = self.readInt()
            tickerId = self.readInt()
            tickType = self.readInt()
            value = self.readStr()
            self.eWrapper().tickString(tickerId, tickType, value)
        elif msgId == self.TICK_EFP:
            version = self.readInt()
            tickerId = self.readInt()
            tickType = self.readInt()
            basisPoints = self.readDouble()
            formattedBasisPoints = self.readStr()
            impliedFuturesPrice = self.readDouble()
            holdDays = self.readInt()
            futureExpiry = self.readStr()
            dividendImpact = self.readDouble()
            dividendsToExpiry = self.readDouble()
            self.eWrapper().tickEFP(tickerId, tickType, basisPoints,
                                    formattedBasisPoints, impliedFuturesPrice,
                                    holdDays, futureExpiry, dividendImpact,
                                    dividendsToExpiry)
        elif msgId == self.ORDER_STATUS:
            version = self.readInt()
            MIN_VERSION = 6
            if version < MIN_VERSION:
                print "Old TWS Server not supported."
                print "EREADER: Order Status Min Version = ", MIN_VERSION,\
                      "Current version = ", version
                raise Exception
            id = self.readInt()
            status = self.readStr()
            filled = self.readInt()
            remaining = self.readInt()
            avgFillPrice = self.readDouble()
            permId = self.readInt()
            parentId = self.readInt()
            lastFillPrice = 0
            lastFillPrice = self.readDouble()
            clientId = 0
            clientId = self.readInt()
            whyHeld = None
            whyHeld = self.readStr()
            self.eWrapper().orderStatus(id, status, filled, remaining,
                                        avgFillPrice, permId, parentId,
                                        lastFillPrice, clientId, whyHeld)
        elif msgId == self.ACCT_VALUE:
            version = self.readInt()
            MIN_VERSION = 2
            if version < MIN_VERSION:
                print "Old TWS Server not supported."
                print "EREADER: Account Value Min Version = ", MIN_VERSION,\
                      "Current version = ", version
                raise Exception
            key = self.readStr()
            val = self.readStr()
            cur = self.readStr()
            accountName = None
            accountName = self.readStr()
            self.eWrapper().updateAccountValue(key, val, cur, accountName)
        elif msgId == self.PORTFOLIO_VALUE:
            version = self.readInt()
            MIN_VERSION = 7
            if version < MIN_VERSION:
                print "Old TWS Server not supported."
                print "EREADER: Portfolio Value Min Version = ", MIN_VERSION,\
                      "Current version = ", version
                raise Exception
            contract = Contract()
            contract.m_conId = self.readInt()
            contract.m_symbol = self.readStr()
            contract.m_secType = self.readStr()
            contract.m_expiry = self.readStr()
            contract.m_strike = self.readDouble()
            contract.m_right = self.readStr()
            contract.m_multiplier = self.readStr()
            contract.m_primaryExch = self.readStr()
            contract.m_currency = self.readStr()
            contract.m_localSymbol = self.readStr()
            if version >= 8:
                contract.m_tradingClass = self.readStr()
            position = self.readInt()
            marketPrice = self.readDouble()
            marketValue = self.readDouble()
            averageCost = self.readDouble()
            unrealizedPNL = self.readDouble()
            realizedPNL = self.readDouble()
            accountName = self.readStr()
            contract.m_primaryExch = self.readStr()
            self.eWrapper().updatePortfolio(contract, position, marketPrice,
                                            marketValue, averageCost,
                                            unrealizedPNL, realizedPNL,
                                            accountName)
        elif msgId == self.ACCT_UPDATE_TIME:
            version = self.readInt()
            timeStamp = self.readStr()
            self.eWrapper().updateAccountTime(timeStamp)
        elif msgId == self.ERR_MSG:
            version = self.readInt()
            MIN_VERSION = 2
            if version < MIN_VERSION:
                print "Old TWS Server not supported."
                print "EREADER: ERR_MSG Min Version = ", MIN_VERSION,\
                      "Current version = ", version
                raise Exception
            id = self.readInt()
            errorCode = self.readInt()
            errorMsg = self.readStr()
            self.m_parent.error(id, errorCode, errorMsg)
        elif msgId == self.OPEN_ORDER:
            version = self.readInt()
            MIN_VERSION = 30
            if version < MIN_VERSION:
                print "Old TWS Server not supported."
                print "EREADER: Open Order Min Version = ", MIN_VERSION,\
                      "Current version = ", version
                raise Exception
            order = Order()
            order.m_orderId = self.readInt()
            contract = Contract()
            contract.m_conId = self.readInt()
            contract.m_symbol = self.readStr()
            contract.m_secType = self.readStr()
            contract.m_expiry = self.readStr()
            contract.m_strike = self.readDouble()
            contract.m_right = self.readStr()
            if (version > 32):
                contract.m_multiplier = self.readStr()
            contract.m_exchange = self.readStr()
            contract.m_currency = self.readStr()
            contract.m_localSymbol = self.readStr()
            if (version > 32):
                contract.m_tradingClass = self.readStr()
            order.m_action = self.readStr()
            order.m_totalQuantity = self.readInt()
            order.m_orderType = self.readStr()
            order.m_lmtPrice = self.readDoubleMax()
            order.m_auxPrice = self.readDoubleMax()
            order.m_tif = self.readStr()
            order.m_ocaGroup = self.readStr()
            order.m_account = self.readStr()
            order.m_openClose = self.readStr()
            order.m_origin = self.readInt()
            order.m_orderRef = self.readStr()
            order.m_clientId = self.readInt()
            order.m_permId = self.readInt()
            order.m_outsideRth = self.readBoolFromInt()
            order.m_hidden = (self.readInt() == 1)
            order.m_discretionaryAmt = self.readDouble()
            order.m_goodAfterTime = self.readStr()
            self.readStr()  # skip deprecated sharesAllocation field
            order.m_faGroup = self.readStr()
            order.m_faMethod = self.readStr()
            order.m_faPercentage = self.readStr()
            order.m_faProfile = self.readStr()
            order.m_goodTillDate = self.readStr()
            order.m_rule80A = self.readStr()
            order.m_percentOffset = self.readDoubleMax()
            order.m_settlingFirm = self.readStr()
            order.m_shortSaleSlot = self.readInt()
            order.m_designatedLocation = self.readStr()
            order.m_exemptCode = self.readInt()
            order.m_auctionStrategy = self.readInt()
            order.m_startingPrice = self.readDoubleMax()
            order.m_stockRefPrice = self.readDoubleMax()
            order.m_delta = self.readDoubleMax()
            order.m_stockRangeLower = self.readDoubleMax()
            order.m_stockRangeUpper = self.readDoubleMax()
            order.m_displaySize = self.readInt()
            order.m_blockOrder = self.readBoolFromInt()
            order.m_sweepToFill = self.readBoolFromInt()
            order.m_allOrNone = self.readBoolFromInt()
            order.m_minQty = self.readIntMax()
            order.m_ocaType = self.readInt()
            order.m_eTradeOnly = self.readBoolFromInt()
            order.m_firmQuoteOnly = self.readBoolFromInt()
            order.m_nbboPriceCap = self.readDoubleMax()
            order.m_parentId = self.readInt()
            order.m_triggerMethod = self.readInt()
            order.m_volatility = self.readDoubleMax()
            order.m_volatilityType = self.readInt()
            order.m_deltaNeutralOrderType = self.readStr()
            order.m_deltaNeutralAuxPrice = self.readDoubleMax()
            if not Util.StringIsEmpty(order.m_deltaNeutralOrderType):
                order.m_deltaNeutralConId = self.readInt()
                order.m_deltaNeutraSettlingFirm = self.readStr()
                order.m_deltaNeutralClearingAccount = self.readStr()
                order.m_deltaNeutralClearingIntent = self.readStr()
            if version >= 31 and\
                    not Util.StringIsEmpty(order.m_deltaNeutralOrderType):
                order.m_deltaNeutralOpenClose = self.readStr()
                order.m_deltaNeutralShortSale = self.readBoolFromInt()
                order.m_deltaNeutralShortSaleSlot = self.readInt()
                order.m_deltaNeutralDesignatedLocation = self.readStr()
            order.m_continuousUpdate = self.readInt()
            order.m_referencePriceType = self.readInt()
            order.m_trailStopPrice = self.readDoubleMax()
            order.m_trailingPercent = self.readDoubleMax()
            order.m_basisPoints = self.readDoubleMax()
            order.m_basisPointsType = self.readIntMax()
            contract.m_comboLegsDescrip = self.readStr()
            if version >= 29:
                pass
            smartComboRoutingparamsCount = self.readInt()
            if smartComboRoutingparamsCount > 0:
                order.m_smartComboRoutingParams = []
                for _ in xrange(smartComboRoutingparamsCount):
                    tagValue = TagValue()
                    tagValue.m_tag = self.readStr()
                    tagValue.m_value = self.readStr()
                    order.m_smartComboRoutingParams.append(tagValue)
            order.m_scaleInitLevelSize = self.readIntMax()
            order.m_scaleSubsLevelSize = self.readIntMax()
            order.m_scalePriceIncrement = self.readDoubleMax()
            if order.m_scalePriceIncrement > 0.0\
                    and order.m_scalePriceIncrement != Double.MAX_VALUE:
                order.m_scalePriceAdjustValue = self.readDoubleMax()
                order.m_scalePriceAdjustInterval = self.readIntMax()
                order.m_scaleAutoReset = self.readBoolFromInt()
                order.m_scaleInitPosition = self.readIntMax()
                order.m_scaleInitFillQty = self.readIntMax()
                order.m_scaleRandomPercent = self.readBoolFromInt()
            order.m_hedgeType = self.readStr()
            if not Util.StringIsEmpty(order.m_hedgeType):
                order.m_hedgeParam = self.readStr()
            order.m_optOutSmartRouting = self.readBoolFromInt
            order.m_clearingAccount = self.readStr()
            order.m_clearingIntent = self.readStr()
            order.m_notHeld = self.readBoolFromInt()
            if self.readBoolFromInt():
                underComp = UnderComp()
                underComp.m_conId = self.readInt()
                underComp.m_delta = self.readDouble()
                underComp.m_price = self.readDouble()
                contract.m_underComp = underComp
            order.m_algoStrategy = self.readStr()
            if not Util.StringIsEmpty(order.m_algoStrategy):
                algoParamsCount = self.readInt()
                if algoParamsCount > 0:
                    order.m_algoParams = []
                    for _ in xrange(algoParamsCount):
                        tagValue = TagValue()
                        tagValue.m_tag = self.readStr()
                        tagValue.m_value = self.readStr()
                        order.m_algoParams.append(tagValue)
            orderState = OrderState()
            order.m_whatIf = self.readBoolFromInt()
            orderState.m_status = self.readStr()
            orderState.m_initMargin = self.readStr()
            orderState.m_maintMargin = self.readStr()
            orderState.m_equityWithLoan = self.readStr()
            orderState.m_commission = self.readDoubleMax()
            orderState.m_minCommission = self.readDoubleMax()
            orderState.m_maxCommission = self.readDoubleMax()
            orderState.m_commissionCurrency = self.readStr()
            orderState.m_warningText = self.readStr()
            self.eWrapper().openOrder(order.m_orderId, contract, order,
                                      orderState)
        elif msgId == self.NEXT_VALID_ID:
            version = self.readInt()
            orderId = self.readInt()
            self.eWrapper().nextValidId(orderId)
        elif msgId == self.SCANNER_DATA:
            contract = ContractDetails()
            version = self.readInt()
            MIN_VERSION = 3
            if version < MIN_VERSION:
                print "Old TWS Server not supported."
                print "EREADER: Scanner Data Min Version = ", MIN_VERSION,\
                      "Current version = ", version
                raise Exception
            tickerId = self.readInt()
            numberOfElements = self.readInt()
            for _ in xrange(numberOfElements):
                rank = self.readInt()
                contract.m_summary.m_conId = self.readInt()
                contract.m_summary.m_symbol = self.readStr()
                contract.m_summary.m_secType = self.readStr()
                contract.m_summary.m_expiry = self.readStr()
                contract.m_summary.m_strike = self.readDouble()
                contract.m_summary.m_right = self.readStr()
                contract.m_summary.m_exchange = self.readStr()
                contract.m_summary.m_currency = self.readStr()
                contract.m_summary.m_localSymbol = self.readStr()
                contract.m_marketName = self.readStr()
                contract.m_summary.m_tradingClass = self.readStr()
                distance = self.readStr()
                benchmark = self.readStr()
                projection = self.readStr()
                legsStr = self.readStr()
                self.eWrapper().scannerData(tickerId, rank, contract, distance,
                                            benchmark, projection, legsStr)
            self.eWrapper().scannerDataEnd(tickerId)
        elif msgId == self.CONTRACT_DATA:
            version = self.readInt()
            MIN_VERSION = 7
            if version < MIN_VERSION:
                print "Old TWS Server not supported."
                print "EREADER: Contract Data Min Version = ", MIN_VERSION,\
                      "Current version = ", version
                raise Exception
            reqId = self.readInt()
            contract = ContractDetails()
            contract.m_summary.m_symbol = self.readStr()
            contract.m_summary.m_secType = self.readStr()
            contract.m_summary.m_expiry = self.readStr()
            contract.m_summary.m_strike = self.readDouble()
            contract.m_summary.m_right = self.readStr()
            contract.m_summary.m_exchange = self.readStr()
            contract.m_summary.m_currency = self.readStr()
            contract.m_summary.m_localSymbol = self.readStr()
            contract.m_marketName = self.readStr()
            contract.m_tradingClass = self.readStr()
            contract.m_summary.m_conId = self.readInt()
            contract.m_minTick = self.readDouble()
            contract.m_summary.m_multiplier = self.readStr()
            contract.m_orderTypes = self.readStr()
            contract.m_validExchanges = self.readStr()
            contract.m_priceMagnifier = self.readInt()
            contract.m_underConId = self.readInt()
            contract.m_longName = self.readStr()
            contract.m_summary.m_primaryExch = self.readStr()
            contract.m_contractMonth = self.readStr()
            contract.m_industry = self.readStr()
            contract.m_category = self.readStr()
            contract.m_subcategory = self.readStr()
            contract.m_timeZoneId = self.readStr()
            contract.m_tradingHours = self.readStr()
            contract.m_liquidHours = self.readStr()
            if version >= 8:
                contract.m_evRule = self.readStr()
                contract.m_evMultiplier = self.readDouble()
            secIdListCount = self.readInt()
            if secIdListCount > 0:
                contract.m_secIdList = []
                for _ in xrange(secIdListCount):
                    tagValue = TagValue()
                    tagValue.m_tag = self.readStr()
                    tagValue.m_value = self.readStr()
                    contract.m_secIdList.append(tagValue)
            self.eWrapper().contractDetails(reqId, contract)
        elif msgId == self.BOND_CONTRACT_DATA:
            version = self.readInt()
            MIN_VERSION = 4
            if version < MIN_VERSION:
                print "Old TWS Server not supported."
                print "EREADER: Bond Contract Data Min Version = ",\
                    MIN_VERSION, "Current version = ", version
                raise Exception
            reqId = self.readInt()
            contract = ContractDetails()
            contract.m_summary.m_symbol = self.readStr()
            contract.m_summary.m_secType = self.readStr()
            contract.m_cusip = self.readStr()
            contract.m_coupon = self.readDouble()
            contract.m_maturity = self.readStr()
            contract.m_issueDate = self.readStr()
            contract.m_ratings = self.readStr()
            contract.m_bondType = self.readStr()
            contract.m_couponType = self.readStr()
            contract.m_convertible = self.readBoolFromInt()
            contract.m_callable = self.readBoolFromInt()
            contract.m_putable = self.readBoolFromInt()
            contract.m_descAppend = self.readStr()
            contract.m_summary.m_exchange = self.readStr()
            contract.m_summary.m_currency = self.readStr()
            contract.m_marketName = self.readStr()
            contract.m_summary.m_tradingClass = self.readStr()
            contract.m_summary.m_conId = self.readInt()
            contract.m_minTick = self.readDouble()
            contract.m_orderTypes = self.readStr()
            contract.m_validExchanges = self.readStr()
            contract.m_nextOptionDate = self.readStr()
            contract.m_nextOptionType = self.readStr()
            contract.m_nextOptionPartial = self.readBoolFromInt()
            contract.m_notes = self.readStr()
            contract.m_longName = self.readStr()
            if version >= 6:
                contract.m_evRule = self.readStr()
                contract.m_evMultiplier = self.readDouble()
            if version >= 5:
                secIdListCount = self.readInt()
                if secIdListCount > 0:
                    contract.m_secIdList = []
                    for _ in xrange(secIdListCount):
                        tagValue = TagValue()
                        tagValue.m_tag = self.readStr()
                        tagValue.m_value = self.readStr()
                        contract.m_secIdList.append(tagValue)
            self.eWrapper().bondContractDetails(reqId, contract)
        elif msgId == self.EXECUTION_DATA:
            version = self.readInt()
            MIN_VERSION = 8
            if version < MIN_VERSION:
                print "Old TWS Server not supported."
                print "EREADER: Execution Data Min Version = ",\
                    MIN_VERSION, "Current version = ", version
                raise Exception
            reqId = self.readInt()
            orderId = self.readInt()
            contract = Contract()
            contract.m_conId = self.readInt()
            contract.m_symbol = self.readStr()
            contract.m_secType = self.readStr()
            contract.m_expiry = self.readStr()
            contract.m_strike = self.readDouble()
            contract.m_right = self.readStr()
            if version >= 9:
                    contract.m_multiplier = self.readStr()
            contract.m_exchange = self.readStr()
            contract.m_currency = self.readStr()
            contract.m_localSymbol = self.readStr()
            if version >= 10:
                contract.m_tradingClass = self.readStr()
            exec_ = Execution()
            exec_.m_orderId = orderId
            exec_.m_execId = self.readStr()
            exec_.m_time = self.readStr()
            exec_.m_acctNumber = self.readStr()
            exec_.m_exchange = self.readStr()
            exec_.m_side = self.readStr()
            exec_.m_shares = self.readInt()
            exec_.m_price = self.readDouble()
            exec_.m_permId = self.readInt()
            exec_.m_clientId = self.readInt()
            exec_.m_liquidation = self.readInt()
            exec_.m_cumQty = self.readInt()
            exec_.m_avgPrice = self.readDouble()
            exec_.m_orderRef = self.readStr()
            if version >= 9:
                exec_.m_evRule = self.readStr()
                exec_.m_evMultiplier = self.readDouble()
            self.eWrapper().execDetails(reqId, contract, exec_)
        elif msgId == self.MARKET_DEPTH:
            version = self.readInt()
            id = self.readInt()
            position = self.readInt()
            operation = self.readInt()
            side = self.readInt()
            price = self.readDouble()
            size = self.readInt()
            self.eWrapper().updateMktDepth(id, position, operation, side,
                                           price, size)
        elif msgId == self.MARKET_DEPTH_L2:
            version = self.readInt()
            id = self.readInt()
            position = self.readInt()
            marketMaker = self.readStr()
            operation = self.readInt()
            side = self.readInt()
            price = self.readDouble()
            size = self.readInt()
            self.eWrapper().updateMktDepthL2(id, position, marketMaker,
                                             operation, side, price, size)
        elif msgId == self.NEWS_BULLETINS:
            version = self.readInt()
            newsMsgId = self.readInt()
            newsMsgType = self.readInt()
            newsMessage = self.readStr()
            originatingExch = self.readStr()
            self.eWrapper().updateNewsBulletin(newsMsgId, newsMsgType,
                                               newsMessage, originatingExch)
        elif msgId == self.MANAGED_ACCTS:
            version = self.readInt()
            accountsList = self.readStr()
            self.eWrapper().managedAccounts(accountsList)
        elif msgId == self.RECEIVE_FA:
            version = self.readInt()
            faDataType = self.readInt()
            xml = self.readStr()
            self.eWrapper().receiveFA(faDataType, xml)
        elif msgId == self.HISTORICAL_DATA:
            version = self.readInt()
            MIN_VERSION = 3
            if version < MIN_VERSION:
                print "Old TWS Server not supported."
                print "EREADER: Historical Data Min Version = ",\
                    MIN_VERSION, "Current version = ", version
                raise Exception
            reqId = self.readInt()
            startDateStr = ""
            endDateStr = ""
            completedIndicator = "finished"
            startDateStr = self.readStr()
            endDateStr = self.readStr()
            completedIndicator += "-" + startDateStr + "-" + endDateStr
            itemCount = self.readInt()
            for _ in xrange(itemCount):
                date = self.readStr()
                open = self.readDouble()
                high = self.readDouble()
                low = self.readDouble()
                close = self.readDouble()
                volume = self.readInt()
                WAP = self.readDouble()
                hasGaps = self.readStr()
                barCount = self.readInt()
                self.eWrapper().historicalData(reqId, date, open, high, low,
                                               close, volume, barCount, WAP,
                                               Boolean.valueOf(hasGaps).
                                               booleanValue())
            # send end of dataset marker
            self.eWrapper().historicalData(reqId, completedIndicator,
                                           -1, -1, -1, -1, -1, -1, -1, False)
        elif msgId == self.SCANNER_PARAMETERS:
            version = self.readInt()
            xml = self.readStr()
            self.eWrapper().scannerParameters(xml)
        elif msgId == self.CURRENT_TIME:
            self.readInt()
            time = self.readLong()
            self.eWrapper().currentTime(time)
        elif msgId == self.REAL_TIME_BARS:
            self.readInt()
            reqId = self.readInt()
            time = self.readLong()
            open_ = self.readDouble()
            high = self.readDouble()
            low = self.readDouble()
            close = self.readDouble()
            volume = self.readLong()
            wap = self.readDouble()
            count = self.readInt()
            self.eWrapper().realtimeBar(reqId, time, open_, high, low, close,
                                        volume, wap, count)
        elif msgId == self.FUNDAMENTAL_DATA:
            self.readInt()
            reqId = self.readInt()
            data = self.readStr()
            self.eWrapper().fundamentalData(reqId, data)
        elif msgId == self.CONTRACT_DATA_END:
            self.readInt()
            reqId = self.readInt()
            self.eWrapper().contractDetailsEnd(reqId)
        elif msgId == self.OPEN_ORDER_END:
            self.readInt()
            self.eWrapper().openOrderEnd()
        elif msgId == self.ACCT_DOWNLOAD_END:
            self.readInt()
            accountName = self.readStr()
            self.eWrapper().accountDownloadEnd(accountName)
        elif msgId == self.EXECUTION_DATA_END:
            self.readInt()
            reqId = self.readInt()
            self.eWrapper().execDetailsEnd(reqId)
        elif msgId == self.DELTA_NEUTRAL_VALIDATION:
            self.readInt()
            reqId = self.readInt()
            underComp = UnderComp()
            underComp.m_conId = self.readInt()
            underComp.m_delta = self.readDouble()
            underComp.m_price = self.readDouble()
            self.eWrapper().deltaNeutralValidation(reqId, underComp)
        elif msgId == self.TICK_SNAPSHOT_END:
            self.readInt()
            reqId = self.readInt()
            self.eWrapper().tickSnapshotEnd(reqId)
        elif msgId == self.MARKET_DATA_TYPE:
            self.readInt()
            reqId = self.readInt()
            marketDataType = self.readInt()
            self.eWrapper().marketDataType(reqId, marketDataType)
        elif msgId == self.TICK_SNAPSHOT_END:
            self.readInt()
            commissionReport = CommissionReport()
            commissionReport.m_execId = self.readStr()
            commissionReport.m_commission = self.readDouble()
            commissionReport.m_currency = self.readStr()
            commissionReport.m_realizedPNL = self.readDouble()
            commissionReport.m_yield = self.readDouble()
            commissionReport.m_yieldRedemptionDate = self.readInt()
            self.eWrapper().commissionReport(commissionReport)
        else:
            print 'Error Msg ID: ', msgId
            self.m_parent.error(EClientErrors.NO_VALID_ID,
                                EClientErrors.UNKNOWN_ID.code(),
                                EClientErrors.UNKNOWN_ID.msg())
            return False
        return True

    def readStr(self):
        buf = StringBuffer()
        while True:
            c = self.m_dis.readByte()
            if (c == 0):
                break
            buf.append(c)
        strval = str(buf)
        return None if strval == 0 else strval

    def readBoolFromInt(self):
        strval = self.readStr()
        return False if strval is None else (Integer.parseInt(strval) != 0)

    def readInt(self):
        strval = self.readStr()
        return 0 if strval is None else Integer.parseInt(strval)

    def readIntMax(self):
        strval = self.readStr()
        return Integer.MAX_VALUE if strval is None or (len(strval) == 0)\
            else Integer.parseInt(strval)

    def readLong(self):
        strval = self.readStr()
        return 0l if strval is None else Long.parseLong(strval)

    def readDouble(self):
        strval = self.readStr()
        return 0 if strval is None else Double.parseDouble(strval)

    def readDoubleMax(self):
        strval = self.readStr()
        return Double.MAX_VALUE if strval is None or (len(strval) == 0)\
            else Double.parseDouble(strval)
