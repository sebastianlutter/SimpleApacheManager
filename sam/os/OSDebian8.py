#!/usr/bin/python3
# -*- coding: utf-8 -*-

from sam.os.IOperationSystem import IOperationSystem

__author__ = 'Sebastian Lutter'

class OSDebian8(IOperationSystem):

    def __init__(self):
        pass


    def check(self,config):
        return 0

    def info(self):
        return "Service for Debian 8 install."

    def name(self):
        return "OSDebian8"