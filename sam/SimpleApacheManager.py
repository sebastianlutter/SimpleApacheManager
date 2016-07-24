# -*- coding: utf-8 -*-

import sys
# check if python3 is used (required)
if sys.version_info < (3, 0):
    sys.stdout.write("\nSorry, requires Python 3.x, not Python 2.x\n\n")
    sys.exit(1)

import configparser
import argparse
import os

from sam.services.ApacheService import ApacheService
from sam.services.UserService import UserService
from sam.services.VHostService import VhostService
from sam.os.OSDebian8 import OSDebian8
from sam.os.OSUbuntu1604 import OSUbuntu1604
from sam.commands.DomainCommand import DomainCommand
from sam.commands.SystemCommand import SystemCommand
from sam.commands.UserCommand import UserCommand
from pprint import pprint

class SimpleApacheManager():

    __version__ = "0.0.9"
    __config_file__ = "config.ini"
    #TODO: get user home path from environment
    __config_file_paths__ = [ os.path.abspath("."),os.path.join("/home/user/",".sam/"),"/etc/sam/" ]

    def __init__(self):
        print("\nExecuting SimpleApacheManager version "+self.__version__+"\n")
        # initalize services and os worker
        self.os_services = [OSDebian8(), OSUbuntu1604()]
        self.services = [ApacheService(),UserService(),VhostService()]
        # init all action classes
        self.actions = [DomainCommand(), SystemCommand(), UserCommand()]
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
                print("\tfound no config.ini in folder "+search_path)
        if not configFound:
            raise Exception("Could not find the file "+self.__config_file__)
        # do what is needed
        self.execute(self.args)

    """
    Print the parsed content of config.ini
    """
    def printConfig(self):
        for section in self.config.keys():
            print("Section ["+section+"]")
            for key in self.config[section].keys():
                print('\t{:<20s}= {}'.format(key,self.config[section][key]))

    """
    Actually do the work needed. Read params and call the according commands
    :return Exit code 0 if success, else value > 0
    """
    def execute(self,args):
        pprint(args)
        print()
        # execute the right Actions class
        for action in self.actions:
            if action.getName() == args.command:
                action.process(args)
                print()
                return
            elif args.command == 'check':
                self.check()
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
                            help='if set program does a test-run withou changing anything on your system.')
        # subparsers for second argument
        subparsers = parser.add_subparsers(dest = 'command', title='sub command help', help = 'available subcommands')
        subparsers.required=True
        # add global check parameter
        check_parser = subparsers.add_parser("check",help='Check environment and all service and OS modules.')
        # let each action class add its parameter to the parser
        for action in self.actions:
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
        print("\nConfiguration")
        self.printConfig()
        # run all os checks
        print("\ncheck OS modules:")
        for os_service in self.os_services:
            print('  '+os_service.name() + "\t: " + os_service.info())
        print("\ncheck service modules:")
        for service in self.services:
            print('  '+service.name() + "\t: " + service.info())
        print()

    '''
    Print example usage strings (from subparsers)
    '''
    def printExamples(self):
        print("\nExample usage:\n")
        for action in self.actions:
            for example in action.getExampleUsage():
                print(example)
        print(' $ {:<45s} : {}'.format('sam check ','Check environment and all service and OS modules.'+'\n'))


# programm entry point
def main():
    SimpleApacheManager()