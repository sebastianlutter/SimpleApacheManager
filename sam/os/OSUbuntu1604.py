#!/usr/bin/python3
# -*- coding: utf-8 -*-

from sam.os.IOperationSystem import IOperationSystem

__author__ = 'Sebastian Lutter'

class OSUbuntu1604(IOperationSystem):

    def __init__(self):
        pass

    def check(self):
        pass

    def info(self):
        return "Service for Ubuntu 16.04 install."

    def name(self):
        return "OSUbuntu1604"