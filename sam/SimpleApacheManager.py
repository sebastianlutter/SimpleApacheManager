# -*- coding: utf-8 -*-

import sys
# check if python3 is used (required)
if sys.version_info < (3, 0):
    sys.stdout.write("\nSorry, requires Python 3.x, not Python 2.x\n\n")
    sys.exit(1)

import configparser
import argparse

from sam.services.ApacheService import ApacheService
from sam.os.OSDebian8 import OSDebian8
from sam.os.OSUbuntu1604 import OSUbuntu1604
from sam.actions.DomainActions import DomainActions
from sam.actions.SystemActions import SystemActions
from pprint import pprint

class SimpleApacheManager():

    __version__ = "0.0.9"

    def __init__(self):
        print("\nExecuting SimpleApacheManager version "+self.__version__+"\n")
        # read config.ini first of all
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        # initalize services and os worker
        self.os_services = [OSDebian8(), OSUbuntu1604()]
        self.services = [ApacheService()]
        # init all action classes
        self.actions = [DomainActions(), SystemActions()]
        # parse command line args
        self.args=self.parseParameters()
        # do what is needed
        self.execute(self.args)

    """
    Actually do the work needed. Read params and call the according actions
    """
    def execute(self,args):
        pprint(args)
        # execute the right Actions class
        for action in self.actions:
            if action.getName() == args.command:
                action.process(args)
                return
        raise Exception("Command "+args.command+" cannot be processed. No module that handle it found.")


    """
    Parse the command line arguments.
    """
    def parseParameters(self):
        # parse all actions to generate argparser
        actionNamesList = list()
        for action in self.actions:
            actionNamesList.append(action.getName())
        # create the command line parameters parser
        parser = argparse.ArgumentParser(description='SimpleApacheManager version ' + self.__version__ + '.')
        parser.add_argument('--testrun',action="store_true",help='if set program does try-run withou changing anything on your system.')
        #parser.add_argument('command', choices=actionNamesList, help='Possible actions.')
        # subparsers for second argument
        subparsers = parser.add_subparsers(dest = 'command', title='sub command help', help = 'available subcommands')
        subparsers.required=True
        # let each action class add its parameter to the parser
        for action in self.actions:
            action.addParserArgs(subparsers)
        # Parse the command line arguments
        try:
            parsedArgs=parser.parse_args()
        except:
            self.printExamples()
            raise
        return parser.parse_args()

    """
    Run check on all services and os worker
    """
    def check(self):
        # run all os checks
        print("\nOS modules:")
        for os_service in self.os_services:
            print(os_service.name() + " -> " + os_service.info())
        print("\nService modules:")
        for service in self.services:
            print(service.name() + " -> " + service.info())
    '''
    Print example usage strings (from subparsers)
    '''
    def printExamples(self):
        print("\nExample usage:\n")
        for action in self.actions:
            for example in action.getExampleUsage():
                print(example)
        print()


# programm entry point
def main():
    SimpleApacheManager()