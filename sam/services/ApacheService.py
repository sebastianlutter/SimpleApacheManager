#!/usr/bin/python3
# -*- coding: utf-8 -*-

from sam.services.IService import IService

__author__ = 'Sebastian Lutter'

class ApacheService(IService):

    def __init__(self):
        pass

    def check(self,config):
        print("TODO: implement ApacheService.check()")

    def info(self):
        return "Apache service module for reload and restart the webserver."

    def name(self):
        return "ApacheService"