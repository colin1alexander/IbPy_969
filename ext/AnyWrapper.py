#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# Translated source for AnyWrapper.
# Compared against v969 on 3-Jun-2013.  No changes.
##

# Source file: AnyWrapper.java
# Target file: AnyWrapper.py
#
# Original file copyright original author(s).
# This file copyright Troy Melhase, troy@gci.net.
#
# WARNING: all changes to this file will be lost.

from ib.lib.overloading import overloaded


class AnyWrapper(object):
    """ generated source for AnyWrapper

    """

    @overloaded
    def error(self, e):
        raise NotImplementedError()

    @error.register(object, str)
    def error_0(self, strval):
        raise NotImplementedError()

    @error.register(object, int, int, str)
    def error_1(self, id, errorCode, errorMsg):
        raise NotImplementedError()

    def connectionClosed(self):
        raise NotImplementedError()

"""
Java Source Code:
public interface AnyWrapper {
    void error( Exception e);
    void error( String str);
    void error(int id, int errorCode, String errorMsg);
    void connectionClosed();
}
"""
