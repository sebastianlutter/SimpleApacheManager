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

    # Returns true if service is operational and environment is sane
    @abstractmethod
    def check(self,config):
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
