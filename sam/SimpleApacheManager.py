# -*- coding: utf-8 -*-
import getpass
import sys
# check if python3 is used (required)
import pwd

if sys.version_info < (3, 0):
    sys.stdout.write("\nSorry, requires Python 3.x, not Python 2.x\n\n")
    sys.exit(1)

import configparser
import argparse
import os
import platform

from sam.services.ApacheService import ApacheService
from sam.services.UserService import UserService
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
    __admin_commands__ = ['user','system']


    def __init__(self):
        # identify if sudo permissions are given and get the real user name
        self.real_user=self.getRealUserCheckSudo()
        # initalize services and os worker
        self.os_services = [OSDebian8(), OSUbuntu1604()]
        self.services = { "apache":ApacheService(),
                          "user":UserService(),
                          "template":TemplateService(),
                          "system":SystemService()
                          }
        # init all action classes
        self.commands = {"domain":DomainCommand(),
                         "system":SystemCommand(),
                         "user":UserCommand()
                         }
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
        if not configFound:
            raise Exception("Could not find the file "+self.__config_file__)
        # find working os implementation
        if not self.findWorkingOSImpl():
            raise Exception("OperationSystem "+','.join(platform.linux_distribution())+" is not supported by SimpleApacheManager. Abort.")
        # check if this user has permission to trigger user add/list commands
        self.is_sam_user=(self.real_user in self.services['user'].listLinkedUsers(self.services['system'],self.services['template'].folder_vhost_user))
        self.admin_permission=(self.real_user == 'root'
                               or self.real_user == self.config['system']['admin_user'])
        # parse command line args
        self.args=self.parseParameters()
        # do what is needed
        self.execute(self.args)

    """
    Check if the script has been called with sudo permissions or as root.
    Return the username that executed the script (the user that called sudo)
    or root if sudo was not used.
    """
    def getRealUserCheckSudo(self):
        real_user=''
        process_user=pwd.getpwuid(os.getuid())[0]
        # identify user executing this script
        try:
            real_user=os.environ['SUDO_USER']
        except KeyError:
            # it is not user with sudo roghts, it is a root user
            real_user=os.getenv('USER')
        print("Script executed with {} permissions from user {}".format(process_user,real_user))
        if not os.geteuid() == 0:
            msg="Script needs sudo permissions, please run:\nsudo samcli"
            print(msg)
            sys.exit(1)
        # check if we have sudo rights
        return real_user

    """
    Find the right IOperationSystem implementation
    """
    def findWorkingOSImpl(self):
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
            command=self.commands[action_key]
            if command.getName() == args.command:
                command.process(self.services,self.config,args,self.real_user)
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
        #parser.add_argument('--testrun', action="store_true",
        #                    help='if set program does a test-run without modifying anything.')
        # subparsers for second argument
        subparsers = parser.add_subparsers(dest = 'command', title='sub command help', help = 'available subcommands')
        subparsers.required=True
        # let each action class add its parameter to the parser
        for action_key in self.commands.keys():
            action = self.commands[action_key]
            if action_key in self.__admin_commands__:
                if self.admin_permission:
                    # only add parameters if admin permission is given
                    action.addParserArgs(subparsers)
            else:
                # no special permission needed
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
        # install required OS packages if needed
        try:
            self.__os_service__.install(self.config)
        except:
            print("OS package install failed.\n\n Please manually install these packages:")
            print("apt-get install "+' '.join(self.__os_service__.required_packages))
            print()
        # Delegate SimpleApacheManger installation to SystemCommand class
        self.commands['system'].process(self.services,self.config,self.args,self.real_user)

    '''
    Print example usage strings (from subparsers)
    '''
    def printExamples(self):
        print("\nExample usage:\n")
        for action_key in self.commands.keys():
            action = self.commands[action_key]
            if action_key in self.__admin_commands__:
                if self.admin_permission:
                    for example in action.getExampleUsage():
                        print(example)
            else:
                for example in action.getExampleUsage():
                    print(example)
        print()

# programm entry point
def main():
    SimpleApacheManager()