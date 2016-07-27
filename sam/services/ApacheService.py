#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys

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

    def install(self):
        pass

    """
    Check the apache configuration and reload apache configuration if check is ok.
    """
    def reloadApache(self,sys_service):
        # Testen, ob die Konfiguration noch funktioniert
        try:
            print("\tCheck apache configuration for errors")
            exitcode,stdout,stderr = sys_service.run_shell_commando(["apache2ctl", "configtest"])
            if exitcode != 0:
                print("stdout={}\nstderr={}".format(stdout,stderr))
                msg="Apache coofiguration has errors. Abort to restart apache. Please fix the configuration manually."
                print(msg)
                raise Exception(msg)
            # everything seems ok, reload apache service
            print(" -- reload apache2 service")
            exitcode, stdout, stderr = sys_service.run_shell_commando(["service", "apache2", "reload"])
            if exitcode != 0:
                print("stdout={}\nstderr={}".format(stdout,stderr))
                msg="Apache coofiguration reload failed. Please fix the configuration manually and restart apache server."
                print(msg)
                raise Exception(msg)
        except OSError:
            msg="An error happend while apache was restarted. Abort. "
            print(msg)
            raise Exception(msg)
        except:
            msg="Unexpected error:", sys.exc_info()[0]
            print(msg)
            raise Exception(msg)
        return True