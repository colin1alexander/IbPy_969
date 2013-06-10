# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 02:33:51 2013

@author: Colin Alexander, CFA
"""

from ib.lib import Double, Integer


class Builder(object):
    """
    This class is used to build messages so the entire message can be
    sent to the socket in a single write.
    """
    SEP = chr(0)

    def __init__(self):
        self.m_sb = bytearray(4096)

    def send(self, a):
        if isinstance(a, bool):
            print 'bool'
            self.send(1 if a else 0)
        
        elif isinstance(a, int):  # i.e., 'a' is an integer
            print 'int'
            self.send("" if a == Integer.MAX_VALUE else str(a))

        elif isinstance(a, float):  # i.e., 'a' is an integer
            print 'float'
            self.send("" if a == Double.MAX_VALUE else str(a))

        elif isinstance(a, str):
            print 'str'
            if a is not None:
                self.m_sb.extend(a)
            else:
                self.m_sb.append(self.SEP)

    def __str__(self):
        return str(self.m_sb)

    def getBytes(self):
        return bytearray(str(self.m_sb))
