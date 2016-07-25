#!/usr/bin/python3
# -*- coding: utf-8 -*-
import apt
import platform

from sam.os.IOperationSystem import IOperationSystem

__author__ = 'Sebastian Lutter'

class OSUbuntu1604(IOperationSystem):

    required_packages = ["libapache2-mpm-itk",
                         "apache2",
                         "libapache2-mod-php",
                         "libapache2-mod-proxy-html",
                         "apache2-mpm-itk"
                         ]

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
        err=False
        # collect packages not installed in the host system
        missing=self.get_missing_packages()
        # return false if packages were missing
        if not len(missing)==0:
            err=True
        # if nothing is wrong return true
        return not err

    """
    Check if required packages are installed. Return the list of packages that are missing.
    """
    def get_missing_packages(self):
        print("Check if required OS packages are installed:")
        missing=list()
        for package in self.required_packages:
            cache = apt.Cache()
            if cache[package].is_installed:
                print('\t'+package+" installed")
            else:
                print('\t'+package+' missing')
                missing.append(package)
        return missing