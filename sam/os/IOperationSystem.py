#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'Sebastian Lutter'
#
# Abstract operation system operations class. This is an interface for
# different linux OS implementations.

from abc import ABC, abstractmethod

class IOperationSystem(ABC):

    def __init__(self):
        pass

    # Returns true if service is operational and environment is sane
    @abstractmethod
    def check(self,config):
        pass

    @abstractmethod
    def info(self):
        return "NOT SET YET"

    @abstractmethod
    def name(self):
        return "NOT SET YET"