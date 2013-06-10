# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 17:50:32 2013

@author: Colin
"""


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)


#MESSAGE TYPE NAMES
MSG = enum(
    'accountDownloadEnd',
    'bondContractDetails',
    'cancelFundamentalData',
    'cancelHistoricalData',
    'cancelMktData',
    'cancelMktDepth',
    'cancelNewsBulletins',
    'cancelOrder',
    'cancelRealTimeBars',
    'cancelScannerSubscription',
    'connectionClosed',
    'contractDetails',
    'contractDetailsEnd',
    'currentTime',
    'deltaNeutralValidation',
    'error',
    'execDetails',
    'execDetailsEnd',
    'fundamentalData',
    'historicalData',
    'managedAccounts',
    'nextValidId',
    'openOrder',
    'openOrderEnd',
    'orderStatus',
    'placeOrder',
    'realtimeBar',
    'receiveFA',
    'reqAccountUpdates',
    'reqAllOpenOrders',
    'reqAutoOpenOrders',
    'reqContractDetails',
    'reqCurrentTime',
    'reqExecutions',
    'reqFundamentalData',
    'reqHistoricalData',
    'reqIds',
    'reqManagedAccts',
    'reqMktData',
    'reqMktDepth',
    'reqNewsBulletins',
    'reqOpenOrders',
    'reqRealTimeBars',
    'reqScannerParameters',
    'reqScannerSubscription',
    'requestFA',
    'scannerData',
    'scannerDataEnd',
    'scannerParameters',
    'tickEFP',
    'tickGeneric',
    'tickOptionComputation',
    'tickPrice',
    'tickSize',
    'tickSnapshotEnd',
    'tickString',
    'updateAccountTime',
    'updateAccountValue',
    'updateMktDepth',
    'updateMktDepthL2',
    'updateNewsBulletin',
    'updatePortfolio')
