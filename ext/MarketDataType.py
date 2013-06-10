# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 04:23:21 2013

@author: Colin Alexander, CFA
"""


class MarketDataType(object):
    # constants - market data types
    REALTIME = 1
    FROZEN = 2

    def getField(self, marketDataType):
        if marketDataType == self.REALTIME:
            return "Real-Time"
        elif marketDataType == self.FROZEN:
            return "Frozen"
        else:
            return "Unknown"

#   Not sure what this is supposed to do...
#    def getFields(self):
#    	totalFields = MarketDataType.class.getFields().length;
#    	fields = []
#    	for field in xrange(totalFields):
#    		fields.append(MarketDataType.getField(i + 1);
#    	}
#    	return fields;
    