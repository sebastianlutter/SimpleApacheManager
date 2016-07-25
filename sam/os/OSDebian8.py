#!/usr/bin/python3
# -*- coding: utf-8 -*-

from sam.os.IOperationSystem import IOperationSystem

import apt
import platform
import pprint

__author__ = 'Sebastian Lutter'

class OSDebian8(IOperationSystem):

    required_packages = ["libapache2-mpm-itk",
                         "apache2",
                         "libapache2-mod-php5",
                         "libapache2-mod-proxy-html",
                         "apache2-mpm-itk"]

    def __init__(self):
        pass

    def check(self,config):
        err=False
        # check if debian 8 is running
        infos=platform.linux_distribution()
        if not infos == ('debian','8.5',''):
            # in case the OS is wrong stop here
            return False
        #TODO: implement checks for config and environment
        missing=self.get_missing_packages()
        # return false if packages were missing
        if not len(missing)==0:
            err=True
        # if nothing is wrong return true
        return not err

    def info(self):
        return "Service for Debian 8 install."

    def name(self):
        return "OSDebian8"

    def install(self,config):
        #TODO: install missing packages if not installed yet
        pass

    """
    Check if required packages are installed. Return the list of packages that are missing.
    """
    def get_missing_packages(self):
        missing=list()
        for package in self.required_packages:
            cache = apt.Cache()
            if cache[package].is_installed:
                print('\t'+package+" installed")
            else:
                print('\t'+package+' missing')
                missing.append(package)
        return missing

