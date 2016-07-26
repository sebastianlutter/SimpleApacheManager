#!/usr/bin/python3
# -*- coding: utf-8 -*-

import collections
import sys

from sam.commands.ICommand import IAction

"""
This class manages SimpleApacheManager system tasks. Install and check if all services.
"""
class SystemCommand(IAction):

    actions = collections.OrderedDict(sorted({
         "check" : "shows current options and configuration as well as runs some sanity checks."
         ,"install" : "install the environment integration in the host system. Needs sudo rights."
         #       ,"restore" : "TODO: restore to last sane configuration if something destroyed the configuration."
     }.items()))

    def __init__(self):
        pass

    """
    Do not add anything here, there is a check and install argument added by SimpleApacheManager
    """
    def addParserArgs(self, subparser):
        # add parameters for each action (i.e. check or install). But do not use "sam system install", add it to parent argparse directly "sam install"
        for action in self.actions.keys():
            tmp_parser=subparser.add_parser(action,help=self.actions[action])

    def getName(self):
        return "system"

    '''
    Return string list with usage examples
    '''
    def getExampleUsage(self):
        out=list()
        for action in self.actions.keys():
            out.append(' $ {:<45s} : {}'.format('sam '+action,self.actions[action]))
        return out

    '''
    Process an action depending on the given args
    '''
    def process(self, services, config, args):
        if args.command=="check":
            self.commandStatus()
        elif args.command=="install":
            self.commandInstall(services,config)
        else:
            raise Exception("Unknown sub_command " + args.sub_command)

    def commandStatus(self):
        print("Show status of SimpleApacheManager installation")
        # TODO: Implement

    """
    Do all steps needed to install SimpleApacheManager folder structures (i.e. /var/www/vhosts/)
    """
    def commandInstall(self,services,config):
        sys_user=config['system']['ADMIN_USER']
        sys_group=config['system']['ADMIN_GROUP']
        print("Install SimpleApacheManager in your OS.")
        # make sure user exists, abort if not
        if not services['user'].checkIfUserExistsInOS(sys_user):
            print("The given ADMIN_USER "+sys_user+" does not exist in your OS. \nPlease create it manually (i.e.: sudo adduser "+sys_user+").")
            sys.exit(1)
        # make sure group exists, add it if not
        if not services['user'].checkIfGroupExistsInOS(sys_group):
            # add group to OS
            print("\tadmin group "+sys_group+" does not exist, try to create it.")
            services['user'].createOSGroup(sys_group,services['system'])
        # add user to group (if not already part of)
        if not services['user'].checkIfUserIsInGroup(sys_user,sys_group):
            print("User "+sys_user+" is not part of "+sys_group+", add it now.")
            services['user'].addUserToGroup(sys_user,sys_group)

