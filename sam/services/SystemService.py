#!/usr/bin/python3
# -*- coding: utf-8 -*-

from sam.services.IService import IService
import subprocess
import sys
import pprint

"""
Do shell calls and error handling as service.
"""
__author__ = 'Sebastian Lutter'

class SystemService(IService):

    def __init__(self):
        pass

    """
    Check if the service environment is sane, and all option in config.ini are sane
    """
    def check(self,config):
        # check if we can succesfully run shell commands
        com=['ls']
        exitcode,stdout,stderr = self.run_shell_commando(com)
        if exitcode != 0:
            print("Error checking system service shell execution: "+' '.join(com))
            print('exitcode={}\nstdout={}\nstderr={}'.format(exitcode,stdout,stderr))
            return False
        # check if config values are sane
        sys_ip=config['system']['ip']
        if sys_ip==None:
            raise Exception('config.ini has no "ip" setting in [system] section')
        print("config.system.ip="+sys_ip)
        #TODO: get interfaces ips and compare them to the config
        return True

    def info(self):
        return "System service module for running shell commandos."

    def name(self):
        return "system service"

    def install(self):
        pass

    """
    Run a shell command and its arguments. Return a tupel of (exit code, stdout, stderr), or (1,None,None) if error
    happend.
    """
    def run_shell_commando(self,commandArr):
        try:
            print(" Running shell command: "+' '.join(commandArr))
            with subprocess.Popen([' '.join(commandArr)],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE, shell=True, universal_newlines=True) as proc:
                resultStdout, resultStderr = proc.communicate()
                exitcode=proc.returncode
            return (exitcode,resultStdout,resultStderr)
        except:
            e = sys.exc_info()[0]
            print("An error happend while executing "+' '.join(commandArr))
            print(e)
            return (1,None,None)

