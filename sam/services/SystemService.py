#!/usr/bin/python3
# -*- coding: utf-8 -*-

from sam.services.IService import IService
import subprocess
import sys

"""
Do shell calls and error handling as service.
"""
__author__ = 'Sebastian Lutter'

class SystemService(IService):

    def __init__(self):
        pass

    def check(self,config):
        exitcode,stdout,stderr = self.run_shell_commando(['ls','-1','/home/user'])
        print('exitcode={}\nstdout={}\nstderr={}'.format(exitcode,stdout,stderr))

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
            with subprocess.Popen(commandArr,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE, shell=True, universal_newlines=True) as proc:
                resultStdout, resultStderr = proc.communicate()
                exitcode=proc.returncode
            return (exitcode,resultStdout,resultStderr)
        except:
            print("An error happend while executing "+' '.join(commandArr))
            raise
            #return (1,None,None)

