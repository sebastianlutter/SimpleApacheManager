#!/usr/bin/python3
# -*- coding: utf-8 -*-

from sam.os.IOperationSystem import IOperationSystem
"""
Make sure that required environment packages are installed in Debian8.
"""
import apt
import platform

from sam.services.SystemService import SystemService

__author__ = 'Sebastian Lutter'

class OSDebian8(IOperationSystem):

    required_packages = ["libapache2-mpm-itk",
                         "apache2",
                         "libapache2-mod-php5",
                         "libapache2-mod-proxy-html",
                         "apache2-mpm-itk",
                         "libffi-dev"
                         ]

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
            print("FAILED: There are {} required packages missing.".format(str(len(missing))))
            err=True
        # check if samcli command is in place
        sys_service = SystemService()
        exitcode,stdout,stderr = sys_service.run_shell_commando(['samcli','-h'])
        if exitcode != 0:
            print("FAILED: The samcli command is not present in PATH: "+stderr)
            err=True
        # if nothing is wrong return true
        return not err

    def info(self):
        return "Service for Debian 8 install."

    def name(self):
        return "OSDebian8"

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


    """
    Check if required packages are installed. Return the list of packages that are missing.
    """
    def get_missing_packages(self):
        print("Check if required OS packages are installed:")
        missing=list()
        for package in self.required_packages:
            cache = apt.Cache()
            if cache[package].is_installed:
                print('\tok -> '+package)
            else:
                print('\tmissing ->'+package)
                missing.append(package)
        return missing

