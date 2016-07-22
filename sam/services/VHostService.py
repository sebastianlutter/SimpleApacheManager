#!/usr/bin/python3
# -*- coding: utf-8 -*-

from sam.services.IService import IService

__author__ = 'Sebastian Lutter'

class VhostService(IService):

    def __init__(self):
        pass

    def init(self):
        pass

    def check(self):
        pass

    def process(self, job):
        pass

    def info(self):
        return "VHost service module for reload and restart the webserver."

    def name(self):
        return "VHost service"