#!/usr/bin/python3
# -*- coding: utf-8 -*-


from abc import ABC, abstractmethod

class IAction(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def addParserArgs(self,argparser):
        pass

    @abstractmethod
    def getName(self):
        pass

    @abstractmethod
    def getExampleUsage(self):
        pass

    @abstractmethod
    def process(self,args):
        pass