#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'Sebastian Lutter'

"""
 Abstract service class. A service is responsible of doing some operation.
 It only provides operations for a given task. Unlike Action classes this
 are low level functions.
"""
from abc import ABC, abstractmethod

class IService(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def check(self,config,services):
        pass

    @abstractmethod
    def info(self):
        pass

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def install(self):
        pass