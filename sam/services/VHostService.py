#!/usr/bin/python3
# -*- coding: utf-8 -*-

from sam.services.IService import IService

__author__ = 'Sebastian Lutter'

class VhostService(IService):

    def __init__(self):
        pass

    def check(self,user):
        print("TODO: implement VHostService.check()")

    def info(self):
        return "VHost service module for create new vhosts."

    def name(self):
        return "VHost service"