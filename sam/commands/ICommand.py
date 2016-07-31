#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Abstract action class. A action class provides high level functions to the CLI API
and uses Service or OperationSystem classes to complete an action. Class that inherit
from this class should not implement direct operations.
"""

from abc import ABC, abstractmethod

import sys


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
    def process(self, services, config, args):
        pass

    def askUser(self,message):
        answer = input(message+": (yes/no) ")
        if not answer == "yes":
            print("Aborted.")
            sys.exit(1)