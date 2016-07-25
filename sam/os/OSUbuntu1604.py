#!/usr/bin/python3
# -*- coding: utf-8 -*-

import platform

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
        # check if debian 8 is running
        infos=platform.linux_distribution()
        if not infos == ('Ubuntu', '16.04', 'xenial'):
            # in case the OS is wrong stop here
            return False
        return True

    def info(self):
        return "Service for Ubuntu 16.04 install."

    def name(self):
        return "OSUbuntu1604"

    def install(self,config):
        pass

    def checkStatus(self,config):
        pass