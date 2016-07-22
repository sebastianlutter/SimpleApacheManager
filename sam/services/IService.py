#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'Sebastian Lutter'
#
# Abstract service class. A service responsible of doing some operation.
# It only provides operations for a given task.
#

from abc import ABC, abstractmethod

class IService(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def init(self,):
        pass

    @abstractmethod
    def check(self):
        pass

    @abstractmethod
    def process(self, job):
        pass

    @abstractmethod
    def info(self):
        pass

    @abstractmethod
    def name(self):
        pass