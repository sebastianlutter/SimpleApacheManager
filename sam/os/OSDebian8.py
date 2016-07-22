#!/usr/bin/python3
# -*- coding: utf-8 -*-

from sam.os.IOperationSystem import IOperationSystem

__author__ = 'Sebastian Lutter'

class OSDebian8(IOperationSystem):

    def __init__(self):
        pass


    def init(self, ):
        pass


    def check(self):
        return 0


    def process(self,job):
        pass


    def info(self):
        return "Service for Debian 8 install."

    def name(self):
        return "OSDebian8"