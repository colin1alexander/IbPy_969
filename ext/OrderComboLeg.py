#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# Manually translated source for OrderComboLeg (use with caution!).
# Confirmed against v969 on 4-Jun-2013.
##

# Source file: OrderComboLeg.java
# Target file: OrderComboLeg.py
#
# Original file copyright original author(s).
# This file copyright Colin Alexander
#
# WARNING: all changes to this file will be lost.

from ib.lib.overloading import overloaded
from ib.lib import Double


class OrderComboLeg(object):
    """ manually translated source for OrderComboLeg

    """
    m_price = float()  # price per leg

    @overloaded
    def __init__(self):
        pass

    @__init__.register(object, float)
    def __init___0(self, p_price=None):
        self.m_price = Double.MAX_VALUE if p_price is None else p_price

    def __eq__(self, other):
        if (self == other):
            return True
        if other is None:
            return False
        state = other
        if self.m_price != state.m_price:
            return False
        return True
