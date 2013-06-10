# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 02:08:05 2013

@author: Colin Alexander, CFA
"""


class CommissionReport(object):

    def __init__(self):
        m_commission = 0.0
        m_realizedPNL = 0.0
        m_yield = 0.0
        m_yieldRedemptionDate = 0  # YYYYMMDD format
        m_currency = None
        m_execID = None

    def __eq__(self, p_other):
        l_bRetVal = False

        if p_other is None:
            l_bRetVal = False
        elif self == p_other:
            l_bRetVal = True
        else:
            l_theOther = p_other
            l_bRetVal = self.m_execId.equals(l_theOther.m_execId)

        return l_bRetVal
