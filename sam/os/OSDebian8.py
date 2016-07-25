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
        # check if debian 8 is running
        infos=platform.linux_distribution()
        if not infos == ('debian','8.5',''):
            # in case the OS is wrong stop here
            return False
        return True

    def checkStatus(self,config):
        err=False
        # collect packages not installed in the host system
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
        # First off all, install the needed software packages in the OS
        for package in self.get_missing_packages():
            cache = apt.cache.Cache()
            cache.update()
            pkg = cache[package]
            print("Package "+package+" installed="+pkg.is_installed )
            print("it is not installed.Now you are installing...")
            pkg.mark_install()
            cache.commit()
            print("DONE.")
            cache.update()
        # check again if they are installed now
        missing=self.get_missing_packages()
        if len(missing)>0:
            raise Exception("Abort install of required packages, something has gone wrong. Sorry.")

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

