#!/usr/bin/python3
# -*- coding: utf-8 -*-

from sam.os.IOperationSystem import IOperationSystem

__author__ = 'Sebastian Lutter'

class OSUbuntu1604(IOperationSystem):

    required_packages = ["libapache2-mpm-itk",
                         "apache2",
                         "libapache2-mod-php5",
                         "libapache2-mod-proxy-html",
                         "apache2-mpm-itk"]

    def __init__(self):
        pass

    def check(self,config):
        # ('Ubuntu', '16.04', 'xenial')
        return False

    def info(self):
        return "Service for Ubuntu 16.04 install."

    def name(self):
        return "OSUbuntu1604"

    def install(self,config):
        pass