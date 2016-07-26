# -*- coding: utf-8 -*-

import sys
# check if python3 is used (required)
if sys.version_info < (3, 0):
    sys.stdout.write("\nSorry, requires Python 3.x, not Python 2.x\n\n")
    sys.exit(1)

import configparser
import argparse
import os
import platform

from sam.services.ApacheService import ApacheService
from sam.services.UserService import UserService
from sam.services.VHostService import VhostService
from sam.services.TemplateService import TemplateService
from sam.services.SystemService import SystemService
from sam.os.OSDebian8 import OSDebian8
from sam.os.OSUbuntu1604 import OSUbuntu1604
from sam.commands.DomainCommand import DomainCommand
from sam.commands.SystemCommand import SystemCommand
from sam.commands.UserCommand import UserCommand
from pprint import pprint

# a global verbose flag
verbose=False

class SimpleApacheManager():

    __version__ = "0.0.9"
    __config_file__ = "config.ini"
    __config_file_paths__ = [ os.path.abspath("."),os.path.expanduser("~/.sam/"),"/etc/sam/" ]
    __os_service__ = None


    def __init__(self):
        print("\nExecuting SimpleApacheManager version "+self.__version__+"\n")
        # initalize services and os worker
        self.os_services = [OSDebian8(), OSUbuntu1604()]
        self.services = { "apache":ApacheService(),
                          "user":UserService(),
                          "vhost":VhostService(),
                          "template":TemplateService(),
                          "system":SystemService()
                          }
        # init all action classes
        self.commands = {"domain":DomainCommand(),
                         "system":SystemCommand(),
                         "user":UserCommand()
                         }
        # parse command line args
        self.args=self.parseParameters()
        # search for config.ini
        configFound=False
        for search_path in self.__config_file_paths__:
            fullpath=os.path.join(search_path,'config.ini')
            if os.path.isfile(fullpath):
                print("Using config.ini found in "+fullpath)
                # read config.ini first of all
                self.config = configparser.ConfigParser()
                self.config.read(self.__config_file__)
                configFound=True
            else:
                if self.verbose():
                    print("\tfound no config.ini in folder "+search_path)
        if not configFound:
            raise Exception("Could not find the file "+self.__config_file__)
        # find working os implementation
        if not self.findWorkingOSImpl():
            raise Exception("OperationSystem "+','.join(platform.linux_distribution())+" is not supported by SimpleApacheManager. Abort.")
        # do what is needed
        self.execute(self.args)


    """
    Find the right IOperationSystem implementation
    """
    def findWorkingOSImpl(self):
        if self.verbose():
            print("Identify OperationSystem")
        for os in self.os_services:
            if os.check(self.config):
                self.__os_service__=os
                print("Found "+os.name()+" environment")
                return True
        return False

    """
    Print the parsed content of config.ini
    """
    def printConfig(self):
        print("\nConfiguration:\n")
        for section in self.config.keys():
            print("Section ["+section+"]")
            for key in self.config[section].keys():
                print('\t{:<20s}= {}'.format(key,self.config[section][key]))

    """
    Actually do the work needed. Read params and call the according commands
    :return Exit code 0 if success, else value > 0
    """
    def execute(self,args):
        if self.verbose():
            pprint(args)
        print()
        if args.command == 'install':
            self.install()
            return
        elif args.command == 'check':
            if not self.check():
                print("ERROR: one or more checks failed. SimpleApacheManager is not operational.")
            return
        # execute the right Actions class
        for action_key in self.commands.keys():
            action=self.commands[action_key]
            if action.getName() == args.command:
                action.process(args,self.services)
                print()
                return
        raise Exception("Command "+args.command+" cannot be processed. No module that handle it found.")


    """
    Parse the command line arguments.
    """
    def parseParameters(self):
        # parse all commands to generate argparser
        # create the command line parameters parser
        parser = argparse.ArgumentParser(description='SimpleApacheManager version ' + self.__version__ + '.')
        parser.add_argument('-v',action="store_true",help='run with verbose output.')
        parser.add_argument('--testrun', action="store_true",
                            help='if set program does a test-run without modifying anything.')
        # subparsers for second argument
        subparsers = parser.add_subparsers(dest = 'command', title='sub command help', help = 'available subcommands')
        subparsers.required=True
        # let each action class add its parameter to the parser
        for action_key in self.commands.keys():
            action = self.commands[action_key]
            action.addParserArgs(subparsers)
        # Parse the command line arguments
        try:
            parsedArgs=parser.parse_args()
        except:
            self.printExamples()
            raise
        return parsedArgs

    """
    Run check on all services and os worker
    """
    def check(self):
        err=False
        self.printConfig()
        # run os check
        print("\ncheck OS module:")
        print('  '+self.__os_service__.name() + "\t: " + self.__os_service__.info())
        if not self.__os_service__.checkStatus(self.config):
            if self.args.v:
                print("\tOS check failed for "+self.__os_service__.name())
            err=True
        else:
            print("\tcheck OK for "+self.__os_service__.name())
        print("\ncheck service modules:")
        for service_key in self.services.keys():
            service=self.services[service_key]
            print('  '+service_key + "\t: " + service.info())
            if not service.check(self.config):
                err=True
        print()
        return not err

    """
    Install SimpleApacheManager on the host system. Do pre-install check before.
    """
    def install(self):
        print("Install SimpleApacheManager on "+self.__os_service__.name())
        # do we have sudo rights?
        if not self.services['user'].sudoPermissionsAvailable():
            print("To install SimpleApacheManager run script with sudo. Abort.")
            sys.exit(1)
        # install required OS packages if needed
        self.__os_service__.install(self.config)
        # Delegate SimpleApacheManger installation to SystemCommand class
        self.commands['system'].process(self.services,self.config,self.args)

    '''
    Print example usage strings (from subparsers)
    '''
    def printExamples(self):
        print("\nExample usage:\n")
        for action_key in self.commands.keys():
            action = self.commands[action_key]
            for example in action.getExampleUsage():
                print(example)
        print(' $ {:<45s} : {}'.format('sam check ','Check environment and all service and OS modules.'+'\n'))

    """
    Shorthand for verbose
    """
    def verbose(self):
        return self.args.v

# programm entry point
def main():
    SimpleApacheManager()