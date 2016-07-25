#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'Sebastian Lutter'
#
# Abstract operation system operations class. This is an interface for
# different linux OS implementations.

from abc import ABC, abstractmethod, abstractproperty

class IOperationSystem(ABC):

    def __init__(self):
        pass

    """
    Check if this class is able to serve for the used OS
    """
    @abstractmethod
    def check(self,config):
        pass

    """
    Check if install status of SimpleApacheManager is sane
    """
    @abstractmethod
    def checkStatus(self):
        pass

    @abstractmethod
    def info(self):
        pass

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def install(self,config):
        pass
