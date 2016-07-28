#!/usr/bin/python3
# -*- coding: utf-8 -*-
import apt
import platform
"""
Make sure that required environment packages are installed in Ubuntu 16.04.
"""
from sam.os.IOperationSystem import IOperationSystem

__author__ = 'Sebastian Lutter'

class OSUbuntu1604(IOperationSystem):

    required_packages = ["libapache2-mpm-itk",
                         "apache2",
                         "libapache2-mod-php",
                         "libffi-dev"
                         ]

    def __init__(self):
        pass

    def check(self,config):
        # check if debian 8 is running
        infos=platform.linux_distribution()
        if not infos == ('Ubuntu', '16.04', 'xenial'):
            # in case the OS is wrong stop here
            a,b,c = infos
            return False
        return True

    def info(self):
        return "Service for Ubuntu 16.04 install."

    def name(self):
        return "OSUbuntu1604"

    """
    Identifies which required packages are not installed, and install them. Check if we have sudo permissions.
    """
    def install(self,config):
        missing=self.get_missing_packages()
        # First off all, install the needed software packages in the OS
        cache = apt.cache.Cache()
        try:
            cache.update()
        except:
            print("WARNING: Update apt cache failed, continue with old package cache")
        # mark missing packages to install
        for package in missing:
            pkg = cache[package]
            #print("Package "+package+" installed="+str(pkg.is_installed) )
            print("\tmark to install "+package)
            pkg.mark_install()
        # if packages were marked as installed commit and update cache
        if len(missing)>0:
            cache.commit()
            cache.update()
            # check again if they are installed now
            missing=self.get_missing_packages()
            if len(missing)>0:
                raise Exception("Abort install of required packages, something has gone wrong. Sorry.")
        else:
            print("All required OS packages are already installed.")

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